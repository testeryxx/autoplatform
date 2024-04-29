import os
import sys
import pytest

from apirunner.cli.ReadCasePlugin import ReadCasePlugin

def main():
    # 获取 python运行参数
    # 1. 读取命令行传入的参数
    pytest_cmd_config = []
    for arg in sys.argv:
        if arg.startswith("-"):
            pytest_cmd_config.append(arg)

    print(os.path.join(os.path.dirname(__file__), "BootStrap.py"))
    # 2. 构建pytest参数
    pytest_args = ["-s", "-v", "--capture=sys",
                   os.path.join(os.path.dirname(__file__), "TestBootStrap.py"),
                   "--html=./report/report.html",
                   "--self-contained-html"]
    pytest_args.extend(pytest_cmd_config)

    print("run pytest：", pytest_args)

    pytest.main(pytest_args, plugins=[ReadCasePlugin()])
