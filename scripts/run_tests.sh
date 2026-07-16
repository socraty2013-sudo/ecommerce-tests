#!/bin/bash
set -e

pip install -r requirements.txt
pytest tests/ -v --ignore-glob=tests/test_ui_*.py --alluredir=allure-results