import os
import subprocess
import uuid

import nested_admin
import yaml
from django.contrib import admin

# Register your models here.
from test_history.models import TestReport
from . import models


# 1. 项目配置
from .models import EnvSet, DdtData, DdtParams, ApiCaseStep, AssertOptions, ExtractOptions, HttpRequest, QueryParamInfo, \
    RequestBodyData, Cookie, CookieTemplate, HeaderTemplate


class ProductAdmin(admin.ModelAdmin):
    model = models.Product
    list_display = ['productName', 'productDesc','producter','create_time','id']


admin.site.register(models.Product,ProductAdmin)


# 2. cookie配置
class CookieAdmin(admin.TabularInline):
    model = models.Cookie
    extra=1


class CookieTemplateAdmin(admin.ModelAdmin):
    model = models.CookieTemplate
    inlines = [CookieAdmin]


admin.site.register(models.CookieTemplate, CookieTemplateAdmin)


# 3. 请求头配置
class HeaderAdmin(admin.TabularInline):
    model = models.Header
    extra=1


class HeaderTemplateAdmin(admin.ModelAdmin):
    model = models.HeaderTemplate
    inlines = [HeaderAdmin]


admin.site.register(models.HeaderTemplate, HeaderTemplateAdmin)


# 4. 接口配置
# url参数内容
class QueryParamInfoAdmin(admin.TabularInline):
    model = models.QueryParamInfo


class RequestBodyDataAdmin(admin.TabularInline):
    model = models.RequestBodyData


class HttpRequestAdmin(admin.ModelAdmin):
    model = models.HttpRequest
    inlines = [QueryParamInfoAdmin,RequestBodyDataAdmin]


admin.site.register(models.HttpRequest, HttpRequestAdmin)


# 5. 测试用例配置
# 5.1 环境变量
class EnvSetAdmin(admin.TabularInline):
    list_display = ['setname', 'setvalue','id','Env']
    model = models.EnvSet
    extra=1


class EnvAdmin(admin.ModelAdmin):
    model = models.Env
    inlines = [EnvSetAdmin]


admin.site.register(models.Env, EnvAdmin)


# 5.2
# 5.1 DDT配置
class DdtParamsAdmin(nested_admin.NestedTabularInline):
    extra = 0
    model = models.DdtParams


# 5.1.1 DDT参数配置
class DdtDataAdmin(nested_admin.NestedStackedInline):
    extra=1
    model = models.DdtData
    inlines = [DdtParamsAdmin]


# 5.2 测试步骤
# 5.2.1 断言配置
class AssertOptionsAdmin(nested_admin.NestedTabularInline):
    extra = 0
    model = models.AssertOptions


# 5.2.2 数据抽取配置
class ExtractOptionsAdmin(nested_admin.NestedTabularInline):
    extra = 0
    model = models.ExtractOptions


# 5.2.3 接口配置
class ApiCaseStepAdmin(nested_admin.NestedStackedInline):
    extra = 1
    model = models.ApiCaseStep
    inlines = [AssertOptionsAdmin, ExtractOptionsAdmin]


# 5.2 用例配置
class ApiCaseAdmin(nested_admin.NestedModelAdmin):
    model = models.ApiCase
    inlines = [DdtDataAdmin,ApiCaseStepAdmin]
    actions = ['run_case']

    @admin.action(permissions=['change'])
    def run_case(modeladmin, clientRequest, queryset):
        try:
            apicase = queryset[0]
            test_id = uuid.uuid1().hex
            # 开始组装用例执行所需要的yaml文件，先组装dict，再导出yaml
            caseinfo = {}
            # 1. 查询环境对应的变量信息
            context = {}  # 表：apitest_envset
            contexts = EnvSet.objects.filter(Env_id = apicase.Env_id)
            for c in contexts:
                context.update({c.setname: c.setvalue})
            caseinfo.update({"context": context})

            # 2. 查询 数据驱动信息
            ddts = []
            ddt_datas = DdtData.objects.filter(ApiCase_id = apicase.id)
            for d in ddt_datas:
                ddt = {"desc": d.desc}
                dps = DdtParams.objects.filter(DdtData_id = d.id)
                for dp in dps:
                    ddt.update({dp.setname: dp.setvalue})
                ddts.append(ddt)

            caseinfo.update({"ddts": ddts})

            # 3. 查询测试步骤信息
            steps = []
            case_steps = ApiCaseStep.objects.filter(ApiCase_id = apicase.id)
            for s in case_steps:
                step = {}
                # 3.1 断言信息
                assert_options = []
                sos = AssertOptions.objects.filter(ApiCaseStep_id = s.id)
                for asserts in sos:
                    assert_options.append({
                        "target": asserts.target,
                        "value": asserts.value,
                        "type": asserts.type,
                        "errorMsg": asserts.errorMsg
                    })
                if len(assert_options) > 0:
                    step.update({"assert_options": assert_options})

                # 3.2 数据抽取信息
                extract_options = []
                eos = ExtractOptions.objects.filter(ApiCaseStep_id=s.id)
                for extract in eos:
                    extract_options.append({
                        "target": extract.target,
                        "varname": extract.varname
                    })

                if len(extract_options) > 0:
                    step.update({"extract_options": extract_options})

                # 3.3 请求信息
                request = HttpRequest.objects.filter(id = s.HttpRequest_id).first()
                # 3.3.1 基本信息
                step.update({
                    "url": request.url,
                    "method": request.method
                })
                # 3.3.4 data 信息 / json 信息
                body = {}
                bs = RequestBodyData.objects.filter(HttpRequest_id = request.id)
                for b in bs:
                    body.update({b.key: b.value})
                step.update({
                    request.bodyType: body
                })
                # 3.3.2 cookies信息
                if request.CookieTemplate_id is not None:
                    cookies = {}
                    ct = CookieTemplate.objects.filter(id = request.CookieTemplate_id).first()
                    cs = Cookie.objects.filter(CookieTemplate_id = ct.id)
                    for c in cs:
                        cookies.update({c.key: c.value})
                    step.update({
                        "cookies": cookies
                    })
                # 3.3.3 headers信息
                if request.HeaderTemplate_id is not None:
                    headers = {}
                    ht = HeaderTemplate.objects.filter(id = request.HeaderTemplate_id).first()
                    hs = QueryParamInfo.objects.filter(HeaderTemplate_id = ht.id)
                    for h in hs:
                        params.update({h.key: h.value})
                    step.update({
                        "headers": headers
                    })
                # 3.3.5 params 信息
                params = {}
                ps = QueryParamInfo.objects.filter(HttpRequest_id = request.id)
                for p in ps:
                    params.update({p.key: p.value})
                step.update({
                    "params": params
                })

                # 4. 加入集合
                steps.append(step)

            caseinfo.update({"steps": steps})

            # 4. 导出执行信息到临时文件
            path = "/tmp/auto_test_platform/" + test_id
            filename = path+"/test_" + test_id + ".yaml"
            os.makedirs(path)
            wfile = open(filename, "w+", encoding='utf-8')
            yaml.dump(caseinfo, wfile, encoding="utf-8", allow_unicode=True)
            wfile.close()

            # 5. 执行测试
            reportfile = path + "/"+ test_id + ".html"
            subprocess.call("apirun --cases=" + path + " --html=" + reportfile)

            # 6. 保存测试执行记录及报告信息
            testReport = TestReport(
                title = apicase.caseName,
                report_type='接口自动化测试',
                desc='执行状态：完毕',
                report_detail= test_id + "/" + test_id + ".html"
            )
            testReport.save()


            print(caseinfo)
        except Exception as e:
            modeladmin.message_user(clientRequest, e)
        else:
            modeladmin.message_user(clientRequest, '执行完毕，请前往指定页面查看测试报告')

    run_case.short_description = '执行用例'
    run_case.confirm = '执行用例需要一定时间，请耐心等候，勿重复点击~'

admin.site.register(models.ApiCase, ApiCaseAdmin)