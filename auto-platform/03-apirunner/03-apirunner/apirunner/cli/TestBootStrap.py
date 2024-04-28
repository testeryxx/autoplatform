import pytest

from apirunner.ApiTestFramework.ApiExecutor import execute
from apirunner.cli.DataCenter import DataCenter


class TestBootStrap:
    # pytest 参数化 - 由它去完成多组用例的执行
    # 启动测试之后，读取配置文件 -- 知道有多少测试用例需要执行 -- 信息保存起来
    # 基于pytest参数机制， 实现多次执行
    @pytest.mark.parametrize("caseinfo", DataCenter.caseinfos, ids=DataCenter.ids)
    def test_start(self, caseinfo):
        execute(caseinfo)