# 封装执行流程
import json
import types
from string import Template

from pytest_selenium import SeleniumAdapter

from appiumrunner.ui_framework.UICommand import SeleniumCommand


class MyTemplate(Template):
    delimiter = "!"


def execute(caseinfo, selenium_adapter: SeleniumAdapter):
    """
        UI调用-核心执行器
    """
    steps = caseinfo["steps"]
    context = caseinfo["context"]

    uicommand = SeleniumCommand(selenium_adapter, context)
    for step in steps:
        # 1. 针对step字典的每个参数，进行变量渲染
        refresh(step, context)

        print(step)
        # 2. 调用底层命令，执行具体操作
        uicommand.__getattribute__(step["command"])(
            desc = step.get("desc", None),
            target = step.get("target", None),
            value = step.get("value", None))

def refresh(data, context):
    """
        变量渲染
    """
    if type(data) == dict:
        for key in data.keys():
            value = data.get(key)
            if value is None:
                continue
            if type(value) == str:
                value = MyTemplate(value).substitute(**context)
                data.update({key: value})
            else:
                for item in value:
                    refresh(item, context)





