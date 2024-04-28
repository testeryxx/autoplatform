import os
import subprocess
import uuid

import nested_admin
import yaml
from django.contrib import admin

from . import models

# Register your models here.
# 1. 项目配置
from .models import CaseContext, DdtData, DdtParams, AppCaseStep, AppCase, AppiumServer, Device, AppParams
from test_history.models import TestReport


class ProductAdmin(admin.ModelAdmin):
    model = models.Product
    list_display = ['productName', 'productDesc', 'producter', 'create_time', 'id']


admin.site.register(models.Product, ProductAdmin)


# 2. AppiumServer 服务器配置
class AppiumServerAdmin(admin.ModelAdmin):
    model = models.AppiumServer
    list_display = ['id', 'name', 'hostinfo']


admin.site.register(models.AppiumServer, AppiumServerAdmin)


# 3. Device 配置
class DeviceAdmin(admin.ModelAdmin):
    model = models.Device
    list_display = ['id', 'deviceremark', 'platformName', 'platformVersion', 'deviceName']


admin.site.register(models.Device, DeviceAdmin)


# 4. App 配置
class AppParamsAdmin(nested_admin.NestedTabularInline):
    extra = 0
    model = models.AppParams


class AppManageAdmin(nested_admin.NestedModelAdmin):
    model = models.AppManage
    list_display = ['id', 'appname', 'appversion','platformVersion']
    inlines = [AppParamsAdmin]


admin.site.register(models.AppManage, AppManageAdmin)


# 5. 用例配置
# 5.1 DDT配置
class DdtParamsAdmin(nested_admin.NestedTabularInline):
    extra = 0
    model = models.DdtParams


# 5.1.1 DDT参数配置
class DdtDataAdmin(nested_admin.NestedStackedInline):
    extra = 0
    model = models.DdtData
    inlines = [DdtParamsAdmin]


# 5.2 参数配置
class CaseContextAdmin(nested_admin.NestedTabularInline):
    extra = 0
    model = models.CaseContext


# 5.3 用例步骤
class AppCaseStepAdmin(nested_admin.NestedTabularInline):
    extra = 1
    model = models.AppCaseStep


# 5.4 用例配置
class AppCaseAdmin(nested_admin.NestedModelAdmin):
    model = models.AppCase
    inlines = [CaseContextAdmin, AppCaseStepAdmin, DdtDataAdmin]
    list_display = ['id','appName',  'deviceInfo', 'caseName']

    def appName(self,obj):
        return obj.AppManage

    def deviceInfo(self,obj):
        return obj.Device.deviceremark

    appName.short_description = "应用"
    deviceInfo.short_description = "设备"


    actions = ['run_case']
    
    @admin.action(permissions=['change'])
    def run_case(modeladmin, clientRequest, queryset):
        try:
            appcase = queryset[0]
            test_id = uuid.uuid1().hex
            # 开始组装用例执行所需要的yaml文件，先组装dict，再导出yaml
            caseinfo = {}
            # 1. 查询环境对应的变量信息
            context = {}  # 表：apitest_envset
            contexts = CaseContext.objects.filter(AppCase_id=appcase.id)
            for c in contexts:
                context.update({c.setname: c.setvalue})
            caseinfo.update({"context": context})

            # 2. 查询 数据驱动信息
            ddts = []
            ddt_datas = DdtData.objects.filter(AppCase_id=appcase.id)
            for d in ddt_datas:
                ddt = {"desc": d.desc}
                dps = DdtParams.objects.filter(DdtData_id=d.id)
                for dp in dps:
                    ddt.update({dp.setname: dp.setvalue})
                ddts.append(ddt)

            caseinfo.update({"ddts": ddts})

            # 3. 查询测试步骤信息

            steps = []
            case_steps = AppCaseStep.objects.filter(AppCase_id=appcase.id)
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
            pid = appcase.AppCase_id
            while pid is not None:
                psteps = []
                pcase = AppCase.objects.filter(id=pid).first()
                case_steps = AppCaseStep.objects.filter(AppCase_id=pcase.id)
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
                pid = pcase.AppCase_id

            caseinfo.update({"steps": steps})

            # 4. 导出执行信息到临时文件
            path = "/tmp/auto_test_platform/" + test_id
            filename = path + "/test_" + test_id + ".yaml"
            os.makedirs(path)
            wfile = open(filename, "w+", encoding='utf-8')
            yaml.dump(caseinfo, wfile, encoding="utf-8", allow_unicode=True)
            wfile.close()

            # 5. 执行测试 -- 用的 工具封装里面 apprun命令
            cmd = "apprun --cases=" + path
            # 测试报告文件位置
            reportfile = path + "/" + test_id + ".html"
            cmd = cmd + " --html=" + reportfile + " --self-contained-html"
            # 设备信息、服务器信息、应用信息
            device = Device.objects.filter(id=appcase.Device_id).first()
            server =  AppiumServer.objects.filter(id=device.AppiumServer_id).first()
            appparams = AppParams.objects.filter(AppManage_id=appcase.AppManage_id)

            cmd = cmd + " --driver=Appium"
            cmd = cmd + " --selenium-host=" + server.hostinfo.split(":")[0]
            cmd = cmd + " --selenium-port=" + server.hostinfo.split(":")[1]
            cmd = cmd + " --capability platformName " + device.platformName
            cmd = cmd + " --capability platformVersion " + device.platformVersion
            cmd = cmd + " --capability deviceName " + device.deviceName
            for ap in appparams:
                cmd = cmd + " --capability {} {}".format(ap.setname, ap.setvalue)

            retcode = subprocess.call(cmd)

            # 6. 保存测试执行记录及报告信息
            testReport = TestReport(
                title=appcase.caseName,
                report_type='APP自动化测试',
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


admin.site.register(models.AppCase, AppCaseAdmin)
