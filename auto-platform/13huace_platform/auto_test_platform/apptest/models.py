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


PLATFORM_CHOICE = (
    ('Android', 'Android'),
    ('IOS', 'IOS')
)


class AppiumServer(models.Model):
    name = models.CharField('名称', max_length=200)
    hostinfo = models.CharField('远程地址', max_length=200)
    create_time = models.DateTimeField('创建时间', auto_now=True)  # 创建时间-自动获取当前时间

    class Meta:
        verbose_name = 'AppiumServer管理'
        verbose_name_plural = 'AppiumServer管理'

    def __str__(self):
        return self.name


class Device(models.Model):
    deviceremark = models.CharField('设备标题', max_length=200)
    platformName = models.CharField('设备平台', max_length=200, choices=PLATFORM_CHOICE, default='Android')
    platformVersion = models.CharField('版本', max_length=200)
    deviceName = models.CharField('设备名称', max_length=200)
    AppiumServer = models.ForeignKey('AppiumServer', on_delete=models.CASCADE, verbose_name="AppiumServer信息")
    create_time = models.DateTimeField('创建时间', auto_now=True)  # 创建时间-自动获取当前时间

    class Meta:
        verbose_name = '设备管理'
        verbose_name_plural = '设备管理'

    def __str__(self):
        return self.deviceremark


class AppManage(models.Model):
    appname = models.CharField('应用名称', max_length=200)
    appversion = models.CharField('应用版本', max_length=200)
    platformVersion = models.CharField('平台', max_length=200, choices=PLATFORM_CHOICE, default='Android')
    create_time = models.DateTimeField('创建时间', auto_now=True)  # 创建时间-自动获取当前时间

    class Meta:
        verbose_name = '应用管理'
        verbose_name_plural = '应用管理'

    def __str__(self):
        return self.appname + '_' + self.appversion


class AppParams(models.Model):
    """
        应用参数
    """
    AppManage = models.ForeignKey('AppManage', on_delete=models.CASCADE, verbose_name="应用")
    setname = models.CharField('参数名', max_length=64)
    setvalue = models.CharField('参数值', max_length=1024)

    class Meta:
        verbose_name = '应用参数项'
        verbose_name_plural = '应用参数项'

    def __str__(self):
        return ''


class AppCase(models.Model):
    """
    测试用例
    """
    # 用例名称
    # 执行A测试用例的时候，要分析它是否有前置流程要求。如果配置了前置用例步骤 B，则在A用例的流程之前，添加B用例的流程
    AppCase = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="前置用例步骤")
    AppManage = models.ForeignKey('AppManage', on_delete=models.CASCADE, verbose_name="所属应用")
    Device = models.ForeignKey('Device', on_delete=models.CASCADE, verbose_name="运行设备")
    caseName = models.CharField('用例名称', max_length=128)  # 用例名称

    class Meta:
        verbose_name = 'APP测试用例'
        verbose_name_plural = 'APP测试用例'

    def __str__(self):
        return self.caseName


class CaseContext(models.Model):
    """
    上下文参数定义
    """
    AppCase = models.ForeignKey('AppCase', on_delete=models.CASCADE, verbose_name="测试用例")  # 关联数据驱动项
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
    ('assert_variable', 'assert_variable'),
    ('assert_activity', 'assert_activity'),
    ('assert_text', '判断元素文本'),
    ('assert_text_contains', 'assert_text_contains'),
    ('assert_tag_name', 'assert_tag_name'),
    ('background_app', 'background_app'),
    ('back', 'back'),
    ('click', 'click'),
    ('clear', 'clear'),
    ('send_keys', 'send_keys'),
    ('store_attribute', 'store_attribute'),
    ('store_css_property', 'store_css_property'),
    ('wait_implicitly', 'wait_implicitly'),
    ('wait_time', 'wait_time'),
    ('wait_activity', '等待activity加载')
)


class AppCaseStep(models.Model):
    """
    测试步骤
    """
    AppCase = models.ForeignKey('AppCase', on_delete=models.CASCADE, verbose_name="测试用例")  # 关联测试用例
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
    AppCase = models.ForeignKey('AppCase', on_delete=models.CASCADE, verbose_name="测试用例")  # 关联测试用例
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
