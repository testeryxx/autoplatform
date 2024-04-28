from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from test_history.models import TestReport


# Register your models here.
class TestReportAdmin(admin.ModelAdmin):
    # model = TestReport
    list_display = ['id', 'created_time', 'report_type', 'title', 'desc', 'view_detail']
    List_display_links = None # 禁用编辑按钮


admin.site.register(TestReport, TestReportAdmin)
