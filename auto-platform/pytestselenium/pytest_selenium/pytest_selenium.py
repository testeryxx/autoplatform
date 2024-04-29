# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import copy
from datetime import datetime
import os
import io
import logging

import pytest
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver
from tenacity import Retrying, stop_after_attempt, wait_exponential

from .utils import CaseInsensitiveDict, SeleniumAdapter
from . import drivers

import warnings

LOGGER = logging.getLogger(__name__)

# 当前插件支持的 浏览器类型/ 驱动类型
SUPPORTED_DRIVERS = CaseInsensitiveDict(
    {
        "BrowserStack": webdriver.Remote,
        "CrossBrowserTesting": webdriver.Remote,
        "Chrome": webdriver.Chrome,
        "Edge": webdriver.Edge,
        "Firefox": webdriver.Firefox,
        "IE": webdriver.Ie,
        "Remote": webdriver.Remote,
        "Safari": webdriver.Safari,
        "SauceLabs": webdriver.Remote,
        "TestingBot": webdriver.Remote,
    }
)

try:
    from appium import webdriver as appiumdriver

    SUPPORTED_DRIVERS["Appium"] = appiumdriver.Remote
except ImportError:
    pass  # Appium is optional.


def _merge(a, b):
    """merges b and a configurations.
    Based on http://bit.ly/2uFUHgb
    """
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                _merge(a[key], b[key], [] + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif isinstance(a[key], list):
                if isinstance(b[key], list):
                    a[key].extend(b[key])
                else:
                    a[key].append(b[key])
            else:
                # b wins
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


def pytest_addhooks(pluginmanager):
    from . import hooks

    method = getattr(pluginmanager, "add_hookspecs", None)
    if method is None:
        method = pluginmanager.addhooks
    method(hooks)


@pytest.fixture(scope="session")
def session_capabilities(pytestconfig):
    """Returns combined capabilities from pytest-variables and command line"""
    driver = pytestconfig.getoption("driver").upper()
    capabilities = getattr(DesiredCapabilities, driver, {}).copy()
    if driver == "REMOTE":
        browser = capabilities.get("browserName", "").upper()
        capabilities.update(getattr(DesiredCapabilities, browser, {}))
    capabilities.update(pytestconfig._capabilities)
    return capabilities


@pytest.fixture
def capabilities(
    request,
    driver_class,
    chrome_options,
    firefox_options,
    edge_options,
    session_capabilities,
):
    """Returns combined capabilities"""
    capabilities = copy.deepcopy(session_capabilities)  # make a copy
    if driver_class == webdriver.Remote:
        browser = capabilities.get("browserName", "").upper()
        key, options = (None, None)
        if browser == "CHROME":
            key = getattr(chrome_options, "KEY", "goog:chromeOptions")
            options = chrome_options.to_capabilities()
            if key not in options:
                key = "chromeOptions"
        elif browser == "FIREFOX":
            key = firefox_options.KEY
            options = firefox_options.to_capabilities()
        elif browser == "EDGE":
            key = getattr(edge_options, "KEY", None)
            options = edge_options.to_capabilities()
        if all([key, options]):
            capabilities[key] = _merge(capabilities.get(key, {}), options.get(key, {}))
    capabilities.update(get_capabilities_from_markers(request.node))
    return capabilities


def get_capabilities_from_markers(node):
    capabilities = dict()
    for level, mark in node.iter_markers_with_node("capabilities"):
        LOGGER.debug(
            "{0} marker <{1.name}> "
            "contained kwargs <{1.kwargs}>".format(level.__class__.__name__, mark)
        )
        capabilities.update(mark.kwargs)
    LOGGER.info("Capabilities from markers: {}".format(capabilities))
    return capabilities


@pytest.fixture
def driver_args():
    """Return arguments to pass to the driver service"""
    return None


@pytest.fixture
def driver_kwargs(
    request,
    capabilities,
    chrome_options,
    driver_args,
    driver_class,
    driver_log,
    driver_path,
    firefox_options,
    firefox_profile,
    edge_options,
    pytestconfig,
):
    kwargs = {}
    driver = getattr(drivers, pytestconfig.getoption("driver").lower())
    kwargs.update(
        driver.driver_kwargs(
            capabilities=capabilities,
            chrome_options=chrome_options,
            driver_args=driver_args,
            driver_log=driver_log,
            driver_path=driver_path,
            firefox_options=firefox_options,
            firefox_profile=firefox_profile,
            edge_options=edge_options,
            host=pytestconfig.getoption("selenium_host"),
            port=pytestconfig.getoption("selenium_port"),
            service_log_path=None,
            request=request,
            test=".".join(split_class_and_test_names(request.node.nodeid)),
        )
    )

    pytestconfig._driver_log = driver_log
    return kwargs


@pytest.fixture(scope="session")
def driver_class(request):
    """
    此处返回 运行命令行里面添加 --driver参数值。 这次执行需要一个什么类型的driver
    """
    driver = request.config.getoption("driver")
    if driver is None:
        raise pytest.UsageError("--driver must be specified")
    return SUPPORTED_DRIVERS[driver]


@pytest.fixture
def driver_log(tmpdir):
    """Return path to driver log"""
    return str(tmpdir.join("driver.log"))


@pytest.fixture
def driver_path(request):
    return request.config.getoption("driver_path")


@pytest.fixture
def selenium_adapter(request, driver_class, driver_kwargs):
    """
    返回一个 web驱动
    """
    """Returns a WebDriver instance based on options and capabilities"""

    retries = int(request.config.getini("max_driver_init_attempts"))
    for retry in Retrying(
        stop=stop_after_attempt(retries), wait=wait_exponential(), reraise=True
    ):
        with retry:
            LOGGER.info(
                f"Driver init, attempt {retry.retry_state.attempt_number}/{retries}"
            )
            driver = driver_class(**driver_kwargs)

    event_listener = request.config.getoption("event_listener")
    if event_listener is not None:
        # Import the specified event listener and wrap the driver instance
        mod_name, class_name = event_listener.rsplit(".", 1)
        mod = __import__(mod_name, fromlist=[class_name])
        event_listener = getattr(mod, class_name)
        if not isinstance(driver, EventFiringWebDriver):
            driver = EventFiringWebDriver(driver, event_listener())

    # request.node._driver = driver
    _adapter = SeleniumAdapter(driver)
    request.node._adapter = _adapter
    yield _adapter
    _adapter.driver.quit()
    _adapter.driver = None
    return None


@pytest.fixture
def selenium(selenium_adapter):
    yield selenium_adapter


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    if config.getoption("host"):
        warnings.warn(
            "--host has been deprecated and will be removed in a "
            "future release. Please use --selenium-host instead.",
            DeprecationWarning,
        )
        config.option.selenium_host = config.getoption("host")

    if config.getoption("port"):
        warnings.warn(
            "--port has been deprecated and will be removed in a "
            "future release. Please use --selenium-port instead.",
            DeprecationWarning,
        )
        config.option.selenium_port = config.getoption("port")

    capabilities = config._variables.get("capabilities", {})
    capabilities.update({k: v for k, v in config.getoption("capabilities")})
    config.addinivalue_line(
        "markers",
        "capabilities(kwargs): add or change existing "
        "capabilities. specify capabilities as keyword arguments, for example "
        "capabilities(foo="
        "bar"
        ")",
    )
    if hasattr(config, "_metadata"):
        config._metadata["Driver"] = config.getoption("driver")
        config._metadata["Capabilities"] = capabilities
        if all((config.option.selenium_host, config.option.selenium_port)):
            config._metadata["Server"] = "{0}:{1}".format(
                config.option.selenium_host, config.option.selenium_port
            )
    config._capabilities = capabilities


def pytest_report_header(config, startdir):
    driver = config.getoption("driver")
    if driver is not None:
        return "driver: {0}".format(driver)


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    """
    钩子函数： pytest 生成测试报告的时候会调用此函数
    测试报告的数据，是pytest在执行一个用例的每个阶段都会进行保存。
    """
    outcome = yield
    report = outcome.get_result()
    summary = []
    extra = getattr(report, "extra", [])
    when = getattr(report, "when", None)  # 测试执行的阶段 setup，call，teardown
    adapter = getattr(item, "_adapter", None)
    driver = None
    if adapter is not None:
        driver = adapter.driver
    xfail = hasattr(report, "wasxfail")
    failure = (report.skipped and xfail) or (report.failed and not xfail)
    selenium_capture_debug = item.config.getini("selenium_capture_debug").lower()
    # 指定测试节点截图，或者结束的时候截图
    capture_debug = selenium_capture_debug == "always" \
                    or when == selenium_capture_debug \
                    or failure

    if capture_debug:
        exclude = item.config.getini("selenium_exclude_debug").lower()
        if "logs" not in exclude:
            # gather logs that do not depend on a driver instance
            _gather_driver_log(item, summary, extra)
        if driver is not None:
            # gather debug that depends on a driver instance
            if "url" not in exclude:
                _gather_url(item, report, driver, summary, extra)
            if "screenshot" not in exclude:
                _gather_screenshot(item, report, driver, summary, extra)
            if "html" not in exclude:
                _gather_html(item, report, driver, summary, extra)
            if "logs" not in exclude:
                _gather_logs(item, report, driver, summary, extra)
            # gather debug from hook implementations
            item.config.hook.pytest_selenium_capture_debug(
                item=item, report=report, extra=extra
            )
    # 测试用例执行结束后，把断言中的截图添加进去
    if when == "teardown" and len(adapter.captures) > 0 :
        for capture in adapter.captures:
            if "logs" == capture["type"]:
                pytest_html = item.config.pluginmanager.getplugin("html")
                if pytest_html is not None:
                    extra.append(pytest_html.extras.text(capture["data"], "HTML"))
            if "screenshot" == capture["type"]:
                pytest_html = item.config.pluginmanager.getplugin("html")
                if pytest_html is not None:
                    # add page source to the html report
                    html = '<div class="image"><img src="data:image/png;base64,{}" alt="运行快照截图" ' \
                           'style="cursor:pointer;" ' \
                           'align="right"' \
                           ' onclick="javascript:var aa=window.open();aa.document.write(\'<img src=\'+this.src+\' />\');;" ' \
                           ' ></img>{}</div>'.format(capture["data"],capture["desc"])
                    extra.append(pytest_html.extras.html(html))
                    # extra.append(pytest_html.extras.image(capture["data"], "xxxx"))

    if driver is not None:
        # allow hook implementations to further modify the report
        item.config.hook.pytest_selenium_runtest_makereport(
            item=item, report=report, summary=summary, extra=extra
        )
    if summary:
        report.sections.append(("pytest-selenium", "\n".join(summary)))
    report.extra = extra


def _gather_url(item, report, driver, summary, extra):
    try:
        url = driver.current_url
    except Exception as e:
        summary.append("WARNING: Failed to gather URL: {0}".format(e))
        return
    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html is not None:
        # add url to the html report
        extra.append(pytest_html.extras.url(url))
    summary.append("URL: {0}".format(url))


def _gather_screenshot(item, report, driver, summary, extra):
    try:
        screenshot = driver.get_screenshot_as_base64()
    except Exception as e:
        summary.append("WARNING: Failed to gather screenshot: {0}".format(e))
        return
    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html is not None:
        # add screenshot to the html report
        html = '<div class="image"><img src="data:image/png;base64,{}" alt="运行快照截图" ' \
               'style="cursor:pointer;" ' \
               'align="right"' \
               ' onclick="javascript:var aa=window.open();aa.document.write(\'<img src=\'+this.src+\' />\');;" ' \
               ' ></img></div>'.format(screenshot)
        extra.append(pytest_html.extras.html(html))



def _gather_html(item, report, driver, summary, extra):
    try:
        html = driver.page_source
    except Exception as e:
        summary.append("WARNING: Failed to gather HTML: {0}".format(e))
        return
    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html is not None:
        # add page source to the html report
        extra.append(pytest_html.extras.text(html, "HTML"))


def _gather_logs(item, report, driver, summary, extra):
    pytest_html = item.config.pluginmanager.getplugin("html")
    try:
        types = driver.log_types
    except Exception as e:
        # note that some drivers may not implement log types
        summary.append("WARNING: Failed to gather log types: {0}".format(e))
        return
    for name in types:
        try:
            log = driver.get_log(name)
        except Exception as e:
            summary.append("WARNING: Failed to gather {0} log: {1}".format(name, e))
            return
        if pytest_html is not None:
            extra.append(
                pytest_html.extras.text(format_log(log), "%s Log" % name.title())
            )


def _gather_driver_log(item, summary, extra):
    pytest_html = item.config.pluginmanager.getplugin("html")
    if (
        hasattr(item.config, "_driver_log")
        and item.config._driver_log is not None
        and os.path.exists(item.config._driver_log)
    ):
        if pytest_html is not None:
            with io.open(item.config._driver_log, "r", encoding="utf8") as f:
                extra.append(pytest_html.extras.text(f.read(), "Driver Log"))
            summary.append("Driver log: {0}".format(item.config._driver_log))


def format_log(log):
    timestamp_format = "%Y-%m-%d %H:%M:%S.%f"
    entries = [
        "{0} {1[level]} - {1[message]}".format(
            datetime.utcfromtimestamp(entry["timestamp"] / 1000.0).strftime(
                timestamp_format
            ),
            entry,
        ).rstrip()
        for entry in log
    ]
    log = "\n".join(entries)
    return log


def split_class_and_test_names(nodeid):
    """Returns the class and method name from the current test"""
    names = nodeid.split("::")
    names[0] = names[0].replace("/", ".")
    names = [x.replace(".py", "") for x in names if x != "()"]
    classnames = names[:-1]
    classname = ".".join(classnames)
    name = names[-1]
    return classname, name


class DriverAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        driver = getattr(drivers, values.lower())
        # set the default host and port if specified in the driver module
        namespace.selenium_host = namespace.selenium_host or getattr(
            driver, "HOST", None
        )
        namespace.selenium_port = namespace.selenium_port or getattr(
            driver, "PORT", None
        )


def pytest_addoption(parser):
    """
    pytest 增加启动选项
    pytest 钩子方法 --> pytest初始化的时候会自动调用这个方法
    """

    # addini 配置文件里面的选项
    _capture_choices = ("never", "failure", "always")
    parser.addini(
        "selenium_capture_debug",
        help="when debug is captured {0}".format(_capture_choices),
        default=os.getenv("SELENIUM_CAPTURE_DEBUG", "failure"),
    )
    parser.addini(
        "selenium_exclude_debug",
        help="debug to exclude from capture",
        default=os.getenv("SELENIUM_EXCLUDE_DEBUG"),
    )

    _auth_choices = ("none", "token", "hour", "day")
    parser.addini(
        "saucelabs_job_auth",
        help="Authorization options for the Sauce Labs job: {0}".format(_auth_choices),
        default=os.getenv("SAUCELABS_JOB_AUTH", "none"),
    )

    _data_center_choices = ("us-west-1", "us-east-1", "eu-central-1")
    parser.addini(
        "saucelabs_data_center",
        help="Data center options for Sauce Labs connections: {0}".format(
            _data_center_choices
        ),
        default="us-west-1",
    )

    parser.addini(
        "max_driver_init_attempts",
        help="Maximum number of driver initialization attempts",
        default=3,
    )
    group = parser.getgroup("selenium", "selenium")
    # 添加启动 命令行参数
    group._addoption(
        "--driver",
        action=DriverAction,
        choices=SUPPORTED_DRIVERS,
        help="webdriver implementation.",
        metavar="str",
    )
    group._addoption(
        "--driver-path", metavar="path", help="path to the driver executable."
    )
    group._addoption(
        "--capability",
        action="append",
        default=[],
        dest="capabilities",
        metavar=("key", "value"),
        nargs=2,
        help="additional capabilities.",
    )
    group._addoption(
        "--event-listener",
        metavar="str",
        help="selenium eventlistener class, e.g. "
        "package.module.EventListenerClassName.",
    )
    group._addoption(
        "--host",
        metavar="str",
        help="DEPRECATED host that the selenium server is listening on, "
        "which will default to the cloud provider default "
        "or localhost.",
    )
    group._addoption(
        "--port",
        type=int,
        metavar="num",
        help="DEPRECATED port that the selenium server is listening on, "
        "which will default to the cloud provider default "
        "or localhost.",
    )
    group._addoption(
        "--selenium-host",
        metavar="str",
        help="host that the selenium server is listening on, "
        "which will default to the cloud provider default "
        "or localhost.",
    )
    group._addoption(
        "--selenium-port",
        type=int,
        metavar="num",
        help="port that the selenium server is listening on, "
        "which will default to the cloud provider default "
        "or localhost.",
    )
