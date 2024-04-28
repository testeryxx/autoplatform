import pytest

from seleniumrunner.cli.DataCenter import DataCenter
from seleniumrunner.ui_framework.UIExecutor import execute


class TestBootStrap:
    # pytest 参数化 - 由它去完成多组用例的执行
    # 启动测试之后，读取配置文件 -- 知道有多少测试用例需要执行 -- 信息保存起来
    # 基于pytest参数机制， 实现多次执行
    # ids = 每次测试的时候 编号/标题
    @pytest.mark.parametrize("caseinfo", DataCenter.caseinfos, ids=DataCenter.ids)
    def test_start(self, selenium_adapter, caseinfo):
        """
        这是唯一的pytest测试方法 -- 执行不同的参数
        """
        execute(caseinfo, selenium_adapter)