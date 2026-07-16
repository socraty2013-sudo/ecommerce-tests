#!/bin/bash
# ⬆️ 第一行，告诉系统「用 bash 来跑这个脚本」

set -e   # 脚本里任何一步报错立刻停止（如果没这一步，举例：执行pip 时，里面的 pytest 安装失败，后续的 pytest 命令仍会执行）。

pip install -r requirements.txt
pytest tests/ -v --ignore-glob=tests/test_ui_*.py --alluredir=allure-results

