# -*- coding: utf-8 -*-
"""商品详情页测试 —— 测试工程师按五要素喂 AI-claude 后，AI-claude 读工程产出。

被测规则（来自喂的规则，逐条落地）：
  1. 商品列表显示商品名 —— 【不重写】已有 test_product_list_contains_factory_product 覆盖
  2. 点商品列表名跳到 /products/<id> —— 用例 A
  3. 详情页显示名称/价格/库存            —— 用例 B（访问时带登录态 → 顺带验了规则5登录半边）
  4. 已删除商品 → 404 友好提示、无报错    —— 用例 C
  5. 登录/未登录都能打开详情页           —— 用例 B(登录) + 用例 D(未登录)

工程约定（读了 conftest/common 后遵守）：
  - create 接口不回商品 id → 造完去首页用商品名反查它的 id（同 delete 测试的招）
  - 未登录用例不能和登录 fixture 混用（同 client 登录态污染）→ 走「造数→登出→再访问」
"""
import re
import allure
from tests.common.factory import product_factory


def _grab_product_id(html_text, name):
    """从首页 HTML 按商品名反查 id。表格每行：<td>id</td><td><a href...>name</a></td>..."""
    m = re.search(rf"<td>(\d+)</td>\s*<td><a[^>]*>{re.escape(name)}</a></td>", html_text)
    return int(m.group(1)) if m else None


def _create_then_grab_id(bapi, data):
    """造一个商品 → 从列表反查它的 id → 返回 id。create 不回 id，这是工程现实。"""
    bapi.create_product(**data)
    html = bapi.get_products().get_data(as_text=True)
    pid = _grab_product_id(html, data["name"])
    assert pid is not None, f"列表里找不到刚建的商品：{data['name']}"
    return pid


@allure.feature("商品管理")
@allure.story("商品详情页")
def test_列表点商品名_跳到对应详情页(business_api_logged_in):
    product = product_factory(name="点我进详情")
    with allure.step("造商品并从列表反查它的链接"):
        pid = _create_then_grab_id(business_api_logged_in, product)

    with allure.step("商品名是链接，且指向 /products/<自己的id>"):
        html = business_api_logged_in.get_products().get_data(as_text=True)
        assert f'<a href="/products/{pid}">{product["name"]}</a>' in html

    with allure.step("点它 → 详情页 200"):
        res = business_api_logged_in.get_product_detail(pid)
        assert res.status_code == 200


@allure.feature("商品管理")
@allure.story("商品详情页")
def test_详情页_显示该商品的名称价格库存(business_api_logged_in):
    product = product_factory(name="详情页专用商品", price=88.8, stock=7)
    with allure.step("造商品并从列表反查它的 id"):
        pid = _create_then_grab_id(business_api_logged_in, product)

    with allure.step("详情页把这一件的名称/价格/库存都渲染出来"):
        html = business_api_logged_in.get_product_detail(pid).get_data(as_text=True)
        assert f"名称：{product['name']}" in html
        assert f"价格：{product['price']}" in html
        assert f"库存：{product['stock']}" in html


@allure.feature("商品管理")
@allure.story("商品详情页")
def test_删除后访问详情页_友好提示404(business_api_logged_in):
    product = product_factory(name="删我后别崩")
    with allure.step("造商品 → 反查 id → 删掉它"):
        pid = _create_then_grab_id(business_api_logged_in, product)
        res = business_api_logged_in.delete_product(pid)
        assert res.status_code == 302

    with allure.step("再访问它的详情 → 404 友好提示，不带报错堆栈"):
        res = business_api_logged_in.get_product_detail(pid)
        assert res.status_code == 404
        html = res.get_data(as_text=True)
        assert "商品不存在" in html
        assert "Traceback" not in html


@allure.feature("商品管理")
@allure.story("商品详情页")
def test_未登录也能打开详情页(business_api_logged_in):
    product = product_factory(name="不登录也让我看")
    with allure.step("登录造一个商品 → 登出，回到未登录态"):
        pid = _create_then_grab_id(business_api_logged_in, product)
        business_api_logged_in.logout()

    with allure.step("未登录访问详情页 → 照样 200 看得到"):
        res = business_api_logged_in.get_product_detail(pid)
        assert res.status_code == 200
        assert product["name"] in res.get_data(as_text=True)
