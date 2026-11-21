# AI-claude-05 示范：加了「框架背景」后 AI-claude 的典型产出（模拟）
# 说明：这段是示范「AI-claude 接进框架后应长成什么样」，非真喂产物。
# 用真实 fixture：business_api（未登录）/ business_api_logged_in（已登录），全来自根 conftest
import allure
import pytest
from tests.common.factory import product_factory


@allure.feature("商品管理")
@allure.story("商品列表")
def test_product_list_ai(business_api):
    res = business_api.get_products()
    assert res.status_code == 200
    assert "商品列表" in res.get_data(as_text=True)


@allure.feature("商品管理")
@allure.story("新增商品")
def test_add_product_ai(business_api_logged_in):
    product = product_factory()
    res = business_api_logged_in.create_product(**product)
    assert res.status_code == 302
    assert res.headers["Location"] == "/"


@allure.feature("商品管理")
@allure.story("未登录拦截")
def test_add_product_without_login_ai(business_api):
    # 未登录直接新增 → login_required 踢回登录页
    res = business_api.create_product(name="未登录商品", price=1, stock=1)
    assert res.status_code == 302
    assert res.headers["Location"] == "/login"
