# -*- coding: utf-8 -*-
"""删除商品接口测试 —— AI-claude 根据「开发新交付的接口」生成，接进本工程框架。

被测规则（来自需求）：
  1. 删除必须登录；未登录访问 → 302 踢回登录页
  2. 登录后删除存在的商品 → 302 回首页，且列表里不再有它
  3. 删除不存在的商品 → 不报错，照样 302 回首页
  4. 删除必须用 POST

工程约定（AI-claude 读了 conftest/common 后遵守）：
  - 已登录用 business_api_logged_in，未登录用 business_api
  - 造数用 product_factory()，删除动作走 BusinessApi.delete_product()
  - 首页 HTML 恰好渲染了 ID 列 → 用商品名反查它的 id（create 接口不回 id）
"""
import re
import allure
import pytest
from tests.common.factory import product_factory


def _grab_product_id(html_text, name):
    """从首页 HTML 按商品名反查 id。表格每行：<td>id</td><td><a href...>name</a></td>..."""
    m = re.search(rf"<td>(\d+)</td>\s*<td><a[^>]*>{re.escape(name)}</a></td>", html_text)
    return int(m.group(1)) if m else None


@allure.feature("商品管理")
@allure.story("删除商品")
def test_登录后删除商品_列表不再显示(business_api_logged_in):
    with allure.step("先造一个商品"):
        product = product_factory()
        business_api_logged_in.create_product(**product)

    with allure.step("从列表页反查它的 id"):
        html = business_api_logged_in.get_products().get_data(as_text=True)
        pid = _grab_product_id(html, product["name"])
        assert pid is not None, f"列表里找不到刚建的商品：{product['name']}"

    with allure.step("登录态删除"):
        res = business_api_logged_in.delete_product(pid)
        assert res.status_code == 302
        assert res.headers["Location"] == "/"

    with allure.step("列表里不再有它"):
        html_after = business_api_logged_in.get_products().get_data(as_text=True)
        assert product["name"] not in html_after


@allure.feature("商品管理")
@allure.story("删除商品")
def test_未登录删除_被踢回登录页(business_api):
    # 拦截发生在 login_required（进业务逻辑之前），商品 id 存不存在无所谓
    with allure.step("未登录直接删 → 踢回登录页"):
        res = business_api.delete_product(999999)
        assert res.status_code == 302
        assert res.headers["Location"] == "/login"


@allure.feature("商品管理")
@allure.story("删除商品")
def test_删除不存在的商品_不报错(business_api_logged_in):
    res = business_api_logged_in.delete_product(999999)   # 不存在的 id
    assert res.status_code == 302
    assert res.headers["Location"] == "/"
