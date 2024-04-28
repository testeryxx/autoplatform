from django.db import models


# Create your models here.

class Env(models.Model):
    """
    不同的环境
    """
    envcode = models.CharField('环境', max_length=64)  # 设置名称
    remark = models.CharField('备注', max_length=200, null=True, blank=True)  # 备注
    create_time = models.DateTimeField('创建时间', auto_now=True)  # 创建时间-自动获取当前时间

    class Meta:
        verbose_name = '环境'
        verbose_name_plural = '环境'

    def __str__(self):
        return self.envcode


class EnvSet(models.Model):
    """
    环境变量
    """
    Env = models.ForeignKey('Env', on_delete=models.CASCADE, verbose_name="环境")  # 关联环境id
    setname = models.CharField('配置项', max_length=64)  # 设置名称
    setvalue = models.CharField('配置值', max_length=200)  # 设置值

    class Meta:
        verbose_name = '环境变量'
        verbose_name_plural = '环境变量'

    def __str__(self):
        return ''


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


class HttpRequest(models.Model):
    """
    接口定义 - http请求模板
    """
    REQUEST_METHOD_CHOICE = (
        ('POST', 'POST'),
        ('GET', 'GET'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE')
    )

    HTTP_CHOICE = (
        ('http', 'http'),
        ('https', 'https')
    )
    BODY_TYPE_CHOICE = (
        ('json', 'json格式数据'),
        ('data', '普通键值对')
    )
    Product = models.ForeignKey(
        'Product', on_delete=models.CASCADE, verbose_name="所属项目")
    HeaderTemplate = models.ForeignKey(
        'HeaderTemplate', on_delete=models.CASCADE, verbose_name="请求头", null=True, blank=True)
    CookieTemplate = models.ForeignKey(
        'CookieTemplate', on_delete=models.CASCADE, verbose_name="Cookie信息", null=True, blank=True)
    apiName = models.CharField('接口名称', max_length=128, null=True)
    method = models.CharField('请求类型', max_length=128,
                              choices=REQUEST_METHOD_CHOICE)
    bodyType = models.CharField('Post参数类型(可选)', max_length=128,
                                choices=BODY_TYPE_CHOICE, null=True, blank=True)
    url = models.CharField('完整URL地址', max_length=2048, null=True)
    create_time = models.DateTimeField('创建时间', auto_now=True)

    class Meta:
        verbose_name = '接口信息'
        verbose_name_plural = '接口信息'

    def __str__(self):
        return self.apiName


class QueryParamInfo(models.Model):
    """ URL拼接参数 """
    HttpRequest = models.ForeignKey(
        'HttpRequest', on_delete=models.CASCADE, verbose_name="URL参数")
    key = models.CharField('参数名', max_length=1024)
    value = models.CharField('参数值', max_length=1024)

    class Meta:
        verbose_name = 'URL拼接参数'
        verbose_name_plural = 'URL拼接参数'

    def __str__(self):
        return ''


class RequestBodyData(models.Model):
    """ Post提交参数 """
    HttpRequest = models.ForeignKey(
        'HttpRequest', on_delete=models.CASCADE, verbose_name="请求")  # 关联环境id
    key = models.CharField('参数名', max_length=1024)
    value = models.CharField('参数值', max_length=4096)

    class Meta:
        verbose_name = 'Body参数'
        verbose_name_plural = 'Body参数'

    def __str__(self):
        return ''


class HeaderTemplate(models.Model):
    """ 请求头模板 """
    templateName = models.CharField('模板名称', max_length=64)  # 模板名称
    templateDesc = models.CharField('模板描述', max_length=200, null=True, blank=True)  # 模板描述

    class Meta:
        verbose_name = '请求头模板'
        verbose_name_plural = '请求头模板'

    def __str__(self):
        return self.templateName


class Header(models.Model):
    """ 请求头 """
    HeaderTemplate = models.ForeignKey(
        'HeaderTemplate', on_delete=models.CASCADE, verbose_name="请求头模板")  # 关联模板id
    key = models.CharField('请求头名称', max_length=1024)
    value = models.CharField('请求头内容', max_length=1024)

    class Meta:
        verbose_name = '请求头'
        verbose_name_plural = '请求头'

    def __str__(self):
        return ''


class CookieTemplate(models.Model):
    """ 请求头模板 """
    templateName = models.CharField('Cookie模板名称', max_length=64)  # Cookie模板名称
    templateDesc = models.CharField('Cookie模板描述', max_length=200, null=True, blank=True)  # Cookie模板描述

    class Meta:
        verbose_name = 'Cookie信息模板'
        verbose_name_plural = 'Cookie信息模板'

    def __str__(self):
        return self.templateName


class Cookie(models.Model):
    """ Post提交参数 """
    CookieTemplate = models.ForeignKey(
        'CookieTemplate', on_delete=models.CASCADE, verbose_name="Cookie模板")  # 关联环境id
    key = models.CharField('参数名', max_length=1024)
    value = models.CharField('参数值', max_length=4096)

    class Meta:
        verbose_name = 'Cookie信息'
        verbose_name_plural = 'Cookie信息'

    def __str__(self):
        return ''



class ApiCase(models.Model):
    """
    接口测试用例 - 组合接口形成用例
    """
    # 用例名称
    caseName = models.CharField('用例名称', max_length=64)  # 用例名称
    # 环境变量 - 全局
    Env = models.ForeignKey('Env', on_delete=models.CASCADE, verbose_name="环境")  # 关联环境id

    class Meta:
        verbose_name = '接口测试用例'
        verbose_name_plural = '接口测试用例'

    def __str__(self):
        return self.caseName


class DdtData(models.Model):
    """
    数据驱动数据
    """
    ApiCase = models.ForeignKey('ApiCase', on_delete=models.CASCADE, verbose_name="测试用例")  # 关联测试用例
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


class ApiCaseStep(models.Model):
    """
    接口测试步骤
    """
    ApiCase = models.ForeignKey('ApiCase', on_delete=models.CASCADE, verbose_name="测试用例")  # 关联测试用例
    # 序号
    sort = models.IntegerField('执行顺序', null=False, default=1)
    # 接口
    HttpRequest = models.ForeignKey('HttpRequest', on_delete=models.CASCADE, verbose_name="请求接口")

    class Meta:
        verbose_name = '接口测试步骤'
        verbose_name_plural = '接口测试步骤'
        ordering = ('sort',)

    def __str__(self):
        return ''


class AssertOptions(models.Model):
    """
    断言配置信息
    """
    VALIDATE_CHOICE = (
        ('contains', '包含'),
        ('equals', '相同文本'),
        ('eq', '等于'),
        ('ne', '不等于'),
        ('lt', '小于'),
        ('le', '小于等于'),
        ('gt', '大于'),
        ('ge', '大于等于')
    )
    ApiCaseStep = models.ForeignKey('ApiCaseStep', on_delete=models.CASCADE, verbose_name="测试步骤")
    type = models.CharField('断言类型', max_length=64, choices=VALIDATE_CHOICE)
    errorMsg = models.CharField('断言提示', max_length=1024)
    target = models.CharField('目标值', max_length=1024)
    value = models.CharField('匹配值', max_length=1024)

    class Meta:
        verbose_name = '断言配置'
        verbose_name_plural = '断言配置'

    def __str__(self):
        return ''


class ExtractOptions(models.Model):
    """
    数据抽取项
    """
    ApiCaseStep = models.ForeignKey('ApiCaseStep', on_delete=models.CASCADE, verbose_name="测试步骤")
    target = models.CharField('抽取项(jsonpath/正则)', max_length=512)
    varname = models.CharField('变量名称', max_length=128)
    desc = models.CharField('备注', max_length=512, null=True, blank=True)

    class Meta:
        verbose_name = '数据抽取项'
        verbose_name_plural = '数据抽取项'

    def __str__(self):
        return ''
