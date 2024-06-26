import time

from pytest_selenium import SeleniumAdapter
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import ui


class SeleniumCommand:
    """
        封装 selenium 操作 - 降低使用门槛
    """

    commands = {
        "判断变量": "assert_variable",
    }

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

    def assert_title_is(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.title_is(value)(self.driver), desc)

    def assert_title_contains(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.title_contains(value)(self.driver), desc)

    def assert_url_contains(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.url_contains(value)(self.driver), desc)

    def assert_url_matches(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.url_matches(value)(self.driver), desc)

    def assert_url_to_be(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.url_to_be(value)(self.driver), desc)

    def assert_url_changes(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.url_changes(value)(self.driver), desc)

    def assert_presence_of_element_located(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.presence_of_element_located((By.XPATH, target))(self.driver), desc)

    def assert_presence_of_all_elements_located(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.presence_of_all_elements_located((By.XPATH, target))(self.driver), desc)

    def assert_visibility_of_element_located(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.visibility_of_element_located((By.XPATH, target))(self.driver), desc)

    def assert_invisibility_of_element_located(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.invisibility_of_element_located((By.XPATH, target))(self.driver), desc)

    def assert_invisibility_of_element(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.invisibility_of_element(self.driver.find_element(By.XPATH, target))(self.driver), desc)

    def assert_visibility_of(self, desc, target, value):
        """
            判断某个元素是否页面上可见
        """
        self.selenium_adapter.assert_true(
            EC.visibility_of(self.driver.find_element(By.XPATH, target))(self.driver), desc)

    def assert_visibility_of_any_elements_located(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.visibility_of_any_elements_located((By.XPATH, target))(self.driver), desc)

    def assert_visibility_of_all_elements_located(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.visibility_of_all_elements_located((By.XPATH, target))(self.driver), desc)

    def assert_element_to_be_clickable(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.element_to_be_clickable((By.XPATH, target))(self.driver), desc)

    def assert_staleness_of(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.staleness_of(self.driver.find_element(By.XPATH, target))(self.driver), desc)

    def assert_text_to_be_present_in_element(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.text_to_be_present_in_element((By.XPATH, target), value)(self.driver), desc)

    def assert_text_to_be_present_in_element_value(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.text_to_be_present_in_element_value((By.XPATH, target), value)(self.driver), desc)

    def assert_frame_to_be_available_and_switch_to_it(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, target))(self.driver), desc)

    def assert_element_to_be_selected(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.element_to_be_selected(self.driver.find_element(By.XPATH, target))(self.driver), desc)

    def assert_element_located_to_be_selected(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.element_located_to_be_selected((By.XPATH, target))(self.driver), desc)

    def assert_element_located_selection_state_to_be(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.element_located_selection_state_to_be((By.XPATH, target))(self.driver), desc)

    def assert_number_of_windows_to_be(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.number_of_windows_to_be(value)(self.driver), desc)

    def assert_alert_is_present(self, desc, target, value):
        self.selenium_adapter.assert_true(
            EC.alert_is_present()(self.driver), desc)

    def assert_text_of_alert(self, desc, target, value):
        self.selenium_adapter.assert_true(
            self.driver.switch_to.alert.text == value
            , desc)

    def click(self, desc, target, value):
        """
        单击目标元素
        """
        self.driver.find_element(By.XPATH, target).click()

    def close(self, desc, target, value):
        """
        关闭当前窗口
        """
        self.driver.close()

    def double_click(self, desc, target, value):
        """
        双击元素（例如，链接、按钮、复选框或单选按钮）。
        """
        ActionChains(self.driver).double_click(self.driver.find_element(By.XPATH, target)).perform()

    def drag_and_drop_to_object(self, desc, target, value):
        """
        拖动一个元素并将其放在另一个元素上。
        """
        ActionChains(self.driver).drag_and_drop(self.driver.find_element(By.XPATH, target),
                                   self.driver.find_element(By.XPATH, value)).perform()


    def execute_script(self, desc, target, value):
        """
        在当前选定的框架或窗口的上下文中执行一段 JavaScript
        """
        self.driver.execute_script(target, value)



    def execute_async_script(self, desc, target, value):
        """
        在当前选定的框架或窗口的上下文中执行 JavaScript 的异步片段。
        """
        self.driver.execute_async_script(target, value)

    def mouse_over(self, desc, target, value):
        """
        模拟用户将鼠标悬停在指定元素上。
        """
        ActionChains(self.driver).move_to_element(self.driver.find_element(By.XPATH, target)).perform()


    def open(self, desc, target, value):
        """
        在继续之前打开一个 URL 并等待页面加载。这接受相对和绝对 URL。
        """
        self.driver.get(target)

    def pause(self, desc, target, value):
        """
        等待指定的时间。
        """
        time.sleep(value)


    def select(self, desc, target, value):
        """
        使用选项定位器从下拉菜单中选择一个元素
        """
        Select(self.driver.find_element(By.XPATH, target)).select_by_value(value)

    def select_frame(self, desc, target, value):
        """
        在当前窗口中选择一个框架
        """
        self.driver.switch_to.frame(self.driver.find_element(By.XPATH, target))

    def switch_to_parent_frame(self,desc, target, value):
        """
        切换到上级iframe
        """
        self.driver.switch_to.parent_frame()

    def select_window(self, desc, target, value):
        """
        使用窗口定位器选择一个弹出窗口。选择弹出窗口后，所有命令都将转到该窗口。窗口定位器使用句柄来选择窗口。
        """
        self.driver.switch_to_window(target)

    def send_keys(self, desc, target, value):
        """
        模拟指定元素上的击键事件，就像您逐键键入值一样。
        """
        ActionChains(self.driver).send_keys_to_element(self.driver.find_element(By.XPATH, target),value).perform()


    def store(self, desc, target, value):
        """
        将目标字符串保存为变量以便于重复使用
        """
        self.context.update({value: target})

    def store_text(self, desc, target, value):
        """
        获取元素的文本并存储以备后用
        """
        self.context.update({value: self.driver.find_element(By.XPATH, target).text})

    def store_title(self, desc, target, value):
        """
        获取当前页面的标题。
        """
        self.context.update({value: self.driver.title})

    def store_value(self, desc, target, value):
        """
        获取元素的值并存储以备后用。这适用于任何输入类型元素。
        """
        self.context.update({
            value: self.driver.find_element(By.XPATH, target).get_attribute('value')
        })


    def store_xpath_count(self, desc, target, value):
        """
        获取与指定 xpath 匹配的节点数
        """
        self.context.update({
            value: len(self.driver.find_elements(By.XPATH, target))
        })

    def add_cookie(self,desc, target, value):
        """
            添加cookie
        """
        self.driver.add_cookie({
            "name": target,
            "value": value
        })

    def submit(self, desc, target, value):
        """
        提交指定的表格。这对于没有提交按钮的表单特别有用，例如单输入“搜索”表单。
        """
        self.driver.find_element(By.XPATH, target).submit()



    def wait_for_element_not_visible(self, desc, target, value):
        """
        等待目标元素在页面上不可见。
        """
        ui.WebDriverWait(self.driver, int(value), 0.5).until(
            EC.invisibility_of_element_located((By.XPATH, target)), message=desc
        )

    def wait_for_element_present(self, desc, target, value):
        """
        等待目标元素出现在页面上。
        """
        ui.WebDriverWait(self.driver, int(value), 0.5).until(
            EC.presence_of_element_located((By.XPATH, target)), message=desc
        )

    def wait_for_element_visible(self,target, value, desc):
        """
        等待目标元素在页面上可见。
        """
        ui.WebDriverWait(self.driver, int(value), 0.5).until(
            EC.visibility_of_element_located((By.XPATH, target)), message=desc
        )
