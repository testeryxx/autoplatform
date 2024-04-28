from django.db import models


# Create your models here.
class Product(models.Model):
    """
    项目/产品
    """
    productName = models.CharField('项目名称', max_length=64)  # 项目名称
    productDesc = models.CharField('项目描述', max_length=200, null=True, blank=True)  # 项目描述
    producter = models.CharField('项目负责人', max_length=200, null=True, blank=True)  # 项目负责人
    create_time = models.DateTimeField('创建时间', auto_now=True)  # 创建时间-自动获取当前时间

    class Meta:
        verbose_name = '项目管理'
        verbose_name_plural = '项目管理'

    def __str__(self):
        return self.productName


class SeleniumHubServer(models.Model):
    name = models.CharField('名称', max_length=200)
    hostinfo = models.CharField('远程地址', max_length=200)
    create_time = models.DateTimeField('创建时间', auto_now=True)  # 创建时间-自动获取当前时间

    class Meta:
        verbose_name = 'SeleniumHUB管理'
        verbose_name_plural = 'SeleniumHUB管理'

    def __str__(self):
        return self.name


# 浏览器选项
BROWSER_CHOICE = (
    ('chrome', 'chrome'),
    ('firefox', 'firefox'),
    ('ie', 'ie'),
    ('edge', 'edge')
)


class WebCase(models.Model):
    """
    测试用例
    """
    # 用例名称
    # 执行A测试用例的时候，要分析它是否有前置流程要求。如果配置了前置用例步骤 B，则在A用例的流程之前，添加B用例的流程
    WebCase = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="前置用例步骤")
    Product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="所属项目")
    SeleniumHubServer = models.ForeignKey('SeleniumHubServer',
                                          on_delete=models.CASCADE, verbose_name="SeleniumServer服务器")
    caseName = models.CharField('用例名称', max_length=128)  # 用例名称
    browser = models.CharField('浏览器', max_length=64, choices=BROWSER_CHOICE)

    class Meta:
        verbose_name = 'WEB测试用例'
        verbose_name_plural = 'WEB测试用例'

    def __str__(self):
        return self.caseName


class CaseContext(models.Model):
    """
    上下文参数定义
    """
    WebCase = models.ForeignKey('WebCase', on_delete=models.CASCADE, verbose_name="测试用例")  # 关联数据驱动项
    setname = models.CharField('参数名', max_length=64)
    setvalue = models.CharField('参数值', max_length=1024)

    class Meta:
        verbose_name = '上下文参数定义'
        verbose_name_plural = '上下文参数定义'

    def __str__(self):
        return ''


# 这里命令 对应 框架封装里面的命令
# 后面这一个就是页面显示内容
COMMANDS = (
    ('click', '点击'),
    ('close', 'close'),
    ('double_click', 'double_click'),
    ('drag_and_drop_to_object', 'drag_and_drop_to_object'),
    ('execute_script', 'execute_script'),
    ('execute_async_script', 'execute_async_script'),
    ('mouse_over', 'mouse_over'),
    ('open', 'open'),
    ('pause', 'pause'),
    ('select', 'select'),
    ('select_frame', 'select_frame'),
    ('switch_to_parent_frame', 'switch_to_parent_frame'),
    ('select_window', 'select_window'),
    ('send_keys', 'send_keys'),
    ('store', 'store'),
    ('store_text', 'store_text'),
    ('store_title', 'store_title'),
    ('store_value', 'store_value'),
    ('store_xpath_count', 'store_xpath_count'),
    ('add_cookie', 'add_cookie'),
    ('submit', 'submit'),
    ('wait_for_element_not_visible', 'wait_for_element_not_visible'),
    ('wait_for_element_present', 'wait_for_element_present'),
    ('wait_for_element_visible', 'wait_for_element_visible'),
    ('assert_variable', 'assert_variable'),
    ('assert_title_is', 'assert_title_is'),
    ('assert_title_contains', 'assert_title_contains'),
    ('assert_url_contains', 'assert_url_contains'),
    ('assert_url_matches', 'assert_url_matches'),
    ('assert_url_to_be', 'assert_url_to_be'),
    ('assert_url_changes', 'assert_url_changes'),
    ('assert_presence_of_element_located', 'assert_presence_of_element_located'),
    ('assert_presence_of_all_elements_located', 'assert_presence_of_all_elements_located'),
    ('assert_visibility_of_element_located', 'assert_visibility_of_element_located'),
    ('assert_invisibility_of_element_located', 'assert_invisibility_of_element_located'),
    ('assert_invisibility_of_element', 'assert_invisibility_of_element'),
    ('assert_visibility_of', 'assert_visibility_of'),
    ('assert_visibility_of_any_elements_located', 'assert_visibility_of_any_elements_located'),
    ('assert_visibility_of_all_elements_located', 'assert_visibility_of_all_elements_located'),
    ('assert_element_to_be_clickable', 'assert_element_to_be_clickable'),
    ('assert_staleness_of', 'assert_staleness_of'),
    ('assert_text_to_be_present_in_element', 'assert_text_to_be_present_in_element'),
    ('assert_text_to_be_present_in_element_value', 'assert_text_to_be_present_in_element_value'),
    ('assert_frame_to_be_available_and_switch_to_it', 'assert_frame_to_be_available_and_switch_to_it'),
    ('assert_element_to_be_selected', 'assert_element_to_be_selected'),
    ('assert_element_located_to_be_selected', 'assert_element_located_to_be_selected'),
    ('assert_element_located_selection_state_to_be', 'assert_element_located_selection_state_to_be'),
    ('assert_number_of_windows_to_be', 'assert_number_of_windows_to_be'),
    ('assert_alert_is_present', 'assert_alert_is_present'),
    ('assert_text_of_alert', 'assert_text_of_alert')
)


class WebCaseStep(models.Model):
    """
    测试步骤
    """
    WebCase = models.ForeignKey('WebCase', on_delete=models.CASCADE, verbose_name="测试用例")  # 关联测试用例
    # 序号
    sort = models.IntegerField('执行顺序', null=False, default=1)

    command = models.CharField('步骤调用命令', max_length=255, choices=COMMANDS)
    desc = models.CharField('步骤描述', max_length=255, null=True, blank=True)
    target = models.CharField('操作对象[页面元素、具体值..]', max_length=255, null=True, blank=True)
    value = models.CharField('数据项', max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = '测试步骤'
        verbose_name_plural = '测试步骤'
        ordering = ('sort',)

    def __str__(self):
        return ''


class DdtData(models.Model):
    """
    数据驱动数据
    """
    WebCase = models.ForeignKey('WebCase', on_delete=models.CASCADE, verbose_name="测试用例")  # 关联测试用例
    desc = models.CharField('说明', max_length=255)

    class Meta:
        verbose_name = '数据驱动'
        verbose_name_plural = '数据驱动'

    def __str__(self):
        return ''


class DdtParams(models.Model):
    """
    数据驱动数据项
    """
    DdtData = models.ForeignKey('DdtData', on_delete=models.CASCADE, verbose_name="数据驱动项")  # 关联数据驱动项
    setname = models.CharField('参数名', max_length=64)
    setvalue = models.CharField('参数值', max_length=1024)

    class Meta:
        verbose_name = '数据驱动数据项'
        verbose_name_plural = '数据驱动数据项'

    def __str__(self):
        return ''
