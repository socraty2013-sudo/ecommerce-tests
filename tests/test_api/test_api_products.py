import allure
import pytest
import yaml
import csv
from tests.common.factory import product_factory, ProductFactory

# 在函数外读一次，模块加载时只读一遍文件（示例，效果同下方读 csv ）
# add_product_cases = yaml.safe_load(open("data/add_product.yaml"))

# 上方是yml读法，下方是csv读法，数据（格式）一样
with open("data/products.csv", encoding="utf-8") as f:
    add_product_cases =  list(csv.DictReader(f))

@pytest.mark.smoke
@allure.feature("商品管理")    # Allure 通过装饰器给测试加元数据，报告里就能按层次展示
@allure.story("商品列表")
@allure.severity(allure.severity_level.MINOR)    # severity 有五个级别（从高到低）：BLOCKER > CRITICAL > NORMAL > MINOR > TRIVIAL
def test_product_list(business_api):
    with allure.step("商品列表-首页"):
        res = business_api.get_products()
        assert res.status_code == 200
        assert "商品列表" in res.get_data(as_text=True)

@allure.feature("商品管理")
@allure.story("添加商品")
@allure.title("添加商品测试--标题")  # 如果不加，则默认为函数名
@pytest.mark.parametrize("case", add_product_cases)
def test_add_product(business_api_logged_in, case):

    with allure.step("提交新增商品请求"):
        res = business_api_logged_in.create_product(
            case["name"],
            case["price"],
            case["stock"],
        )

    with allure.step("验证重返回 302定向"):
        assert res.status_code == 302

    with allure.step("验证重新定到首页"):
        assert res.headers["Location"] == "/"

@allure.feature("商品管理")
@allure.story("MOCK 商品数据")
def test_product_list_with_mock(business_api, monkeypatch):
    # 造两条假数据，跳过数据库查询
    fake_products = [(1, "Mock商品", 9.99, 50), (2, "Mock商品2", 19.99, 30)]
    monkeypatch.setattr("app.routes.get_all_products", lambda: fake_products)

    res = business_api.get_products()
    assert res.status_code == 200
    assert "Mock商品" in res.get_data(as_text=True)
    assert "Mock商品2" in res.get_data(as_text=True)
    assert "商品列表" in res.get_data(as_text=True)


@allure.feature("商品管理")
@allure.story("添加商品-书籍工厂")
def test_add_product_factory(business_api_logged_in):
    product = product_factory(name="薯片", price=5)    # 覆盖 name/price，stock 用默认
    res =business_api_logged_in.create_product(**product)    # **product 把字典拆开，变成独立的关键字参数，拆成：create_product(name="薯片", price=5, stock=50)

    assert res.status_code == 302
    assert res.headers["Location"] == "/"

@allure.feature("商品管理")
@allure.story("商品列表-工厂联动")
def test_product_list_contains_factory_product(created_product, business_api_logged_in):
    res = business_api_logged_in.get_products()

    # ⬇️用工厂造的商品名去列表里找。res.get_data(as_text=True)：把返回的 HTML 页面源码转成文字，用来断言页面里有没有某段内容
    # 目前主流：是接口返回 JSON，此时应直接用 response.json() 拿字典。只是当前 demo 是 flask 直接返回 html，故只能用这个方法
    assert created_product["name"] in res.get_data(as_text=True)


@allure.feature("商品管理")
@allure.story("添加商品-factory_boy")
def test_add_product_factory_boy(business_api_logged_in):
    product = ProductFactory.build(name="薯片", price=5)   # build(传参) 覆盖字段，和手写版用法对齐
    res = business_api_logged_in.create_product(**product)
    assert res.status_code == 302
    assert res.headers["Location"] == "/"
