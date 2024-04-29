import time

from pytest_selenium import SeleniumAdapter
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import ui


class SeleniumCommand:
    """
        封装 appium 操作 - 降低使用门槛
        参考文档： https://appium.io/docs/en/commands
    """

    def __init__(self, selenium_adapter: SeleniumAdapter, context):
        self.selenium_adapter = selenium_adapter
        self.driver = selenium_adapter.driver
        self.context = context

    # ============== 断言操作
    def assert_variable(self, desc, target, value):
        """
        检查变量是否为预期值。变量的值将被转换为字符串进行比较。如果断言失败，测试将停止。
        """
        self.selenium_adapter.assert_true(self.context.get(target, None) == value, desc)

    def assert_activity(self, desc, target, value):
        self.selenium_adapter.assert_true(self.driver.current_activity == value, desc)

    def assert_text(self, desc, target, value):
        self.selenium_adapter.assert_true(self.driver.find_element(By.XPATH, target).text == value, desc)

    def assert_text_contains(self, desc, target, value):
        self.selenium_adapter.assert_true(self.driver.find_element(By.XPATH, target).text.count(value) > 0, desc)

    def assert_tag_name(self, desc, target, value):
        self.selenium_adapter.assert_true(self.driver.find_element(By.XPATH, target).tag_name == value, desc)

    def install_app(self, desc, target, value):
        self.driver.install_app(target);

    def background_app(self, desc, target, value):
        self.driver.background_app(10)

    def back(self, desc, target, value):
        """
        返回
        """
        self.driver.back()

    def click(self, desc, target, value):
        """
            click
        """
        self.driver.find_element(By.XPATH, target).click()

    def clear(self, desc, target, value):
        """
            clear
        """
        self.driver.find_element(By.XPATH, target).clear()

    def send_keys(self, desc, target, value):
        """
            send_keys
        """
        self.driver.find_element(By.XPATH, target).send_keys(value)

    def store_attribute(self,desc, target, value):
        self.context.update({desc: self.driver.find_element(By.XPATH, target).get_attribute(value)})

    def store_css_property(self,desc, target, value):
        self.context.update({desc: self.driver.find_element(By.XPATH, target).value_of_css_property(value)})

    def wait_implicitly(self, desc, target, value):
        self.driver.implicitly_wait(int(value))

    def wait_time(self, desc, target, value):
        time.sleep(int(value))

    def wait_activity(self, desc, target, value):
        self.driver.wait_activity(target, int(value))
