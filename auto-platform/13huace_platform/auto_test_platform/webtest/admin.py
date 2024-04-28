import os
import subprocess
import uuid

import nested_admin
import yaml
from django.contrib import admin

from . import models


# Register your models here.
# 1. 项目配置
from .models import CaseContext, DdtData, DdtParams, WebCaseStep, WebCase, SeleniumHubServer
from test_history.models import TestReport


class ProductAdmin(admin.ModelAdmin):
    model = models.Product
    list_display = ['productName', 'productDesc', 'producter', 'create_time', 'id']


admin.site.register(models.Product, ProductAdmin)


# 2. selenium 服务器配置
class SeleniumHubServerAdmin(admin.ModelAdmin):
    model = models.SeleniumHubServer
    list_display = ['id', 'name', 'hostinfo']


admin.site.register(models.SeleniumHubServer, SeleniumHubServerAdmin)


# 3. 用例配置
# 3.1 DDT配置
class DdtParamsAdmin(nested_admin.NestedTabularInline):
    extra = 0
    model = models.DdtParams


# 3.1.1 DDT参数配置
class DdtDataAdmin(nested_admin.NestedStackedInline):
    extra = 0
    model = models.DdtData
    inlines = [DdtParamsAdmin]


# 3.2 参数配置
class CaseContextAdmin(nested_admin.NestedTabularInline):
    extra = 0
    model = models.CaseContext


# 3.3 用例步骤
class WebCaseStepAdmin(nested_admin.NestedTabularInline):
    extra = 1
    model = models.WebCaseStep


# 3.4 用例配置
class WebCaseAdmin(nested_admin.NestedModelAdmin):
    model = models.WebCase
    inlines = [CaseContextAdmin, WebCaseStepAdmin, DdtDataAdmin]
    actions = ['run_case']

    @admin.action(permissions=['change'])
    def run_case(modeladmin, clientRequest, queryset):
        try:
            webcase = queryset[0]
            test_id = uuid.uuid1().hex
            # 开始组装用例执行所需要的yaml文件，先组装dict，再导出yaml
            caseinfo = {}
            # 1. 查询环境对应的变量信息
            context = {}  # 表：apitest_envset
            contexts = CaseContext.objects.filter(WebCase_id=webcase.id)
            for c in contexts:
                context.update({c.setname: c.setvalue})
            caseinfo.update({"context": context})

            # 2. 查询 数据驱动信息
            ddts = []
            ddt_datas = DdtData.objects.filter(WebCase_id=webcase.id)
            for d in ddt_datas:
                ddt = {"desc": d.desc}
                dps = DdtParams.objects.filter(DdtData_id=d.id)
                for dp in dps:
                    ddt.update({dp.setname: dp.setvalue})
                ddts.append(ddt)

            caseinfo.update({"ddts": ddts})

            # 3. 查询测试步骤信息

            steps = []
            case_steps = WebCaseStep.objects.filter(WebCase_id=webcase.id)
            for s in case_steps:
                step = {}
                # 1. 基本信息
                step.update({
                    "command": s.command,
                    "desc": s.desc,
                    "target": s.target,
                    "value": s.value
                })
                # 2. 加入集合
                steps.append(step)

            # 添加前置流程
            pid = webcase.WebCase_id
            while pid is not None :
                psteps = []
                pcase = WebCase.objects.filter(id=pid).first()
                case_steps = WebCaseStep.objects.filter(WebCase_id=pcase.id)
                for s in case_steps:
                    step = {}
                    # 1. 基本信息
                    step.update({
                        "command": s.command,
                        "desc": s.desc,
                        "target": s.target,
                        "value": s.value
                    })
                    # 2. 加入集合
                    psteps.append(step)
                steps = psteps + steps
                pid = pcase.WebCase_id

            caseinfo.update({"steps": steps})

            # 4. 导出执行信息到临时文件
            path = "/tmp/auto_test_platform/" + test_id
            filename = path + "/test_" + test_id + ".yaml"
            os.makedirs(path)
            wfile = open(filename, "w+", encoding='utf-8')
            yaml.dump(caseinfo, wfile, encoding="utf-8", allow_unicode=True)
            wfile.close()

            # 5. 执行测试 -- 用的 工具封装里面 webrun命令
            server = SeleniumHubServer.objects.filter(id = webcase.SeleniumHubServer_id).first()
            reportfile = path + "/" + test_id + ".html"
            retcode = subprocess.call("webrun --cases=" + path
                            + " --html=" + reportfile
                            + " --selenium-host=" + server.hostinfo.split(":")[0]
                            + " --selenium-port=" + server.hostinfo.split(":")[1]
                            + " --capability browserName " + webcase.browser)

            # 6. 保存测试执行记录及报告信息
            testReport = TestReport(
                title=webcase.caseName,
                report_type='WEB自动化测试',
                desc='执行状态：' + str(retcode),
                report_detail=test_id + "/" + test_id + ".html"
            )
            testReport.save()

            print(caseinfo)
        except Exception as e:
            modeladmin.message_user(clientRequest, e)
        else:
            modeladmin.message_user(clientRequest, '执行完毕，请前往指定页面查看测试报告')

    run_case.short_description = '执行用例'
    run_case.confirm = '执行用例需要一定时间，请耐心等候，勿重复点击~'


admin.site.register(models.WebCase, WebCaseAdmin)
