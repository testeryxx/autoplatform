import os
import sys
import pytest

from seleniumrunner.cli.ReadCasePlugin import ReadCasePlugin


def main():
    # 获取 python运行参数
    # 1. 读取命令行传入的参数
    pytest_cmd_config = []
    for index in range(1, len(sys.argv)):
        pytest_cmd_config.append(sys.argv[index])

    # 2. 构建pytest参数
    pytest_args = ["-s", "-v", "--capture=sys"
                    ,"--driver=REMOTE"
                    , "--selenium-host=192.168.1.103"
                    , "--selenium-port=4444"
                    , "--capability", "browserName", "chrome",""
                    ,"--html=./report/report.html"
                    ,"--self-contained-html",
                   os.path.join(os.path.dirname(__file__), "TestBootStrap.py")]
    pytest_args.extend(pytest_cmd_config)

    print("run pytest：", pytest_args)

    pytest.main(pytest_args, plugins=[ReadCasePlugin()])
