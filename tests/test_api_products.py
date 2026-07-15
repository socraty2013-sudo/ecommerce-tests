from tests.helpers import login
import allure

@allure.feature("商品管理")    # Allure 通过装饰器给测试加元数据，报告里就能按层次展示
@allure.story("商品列表")
@allure.severity(allure.severity_level.MINOR)    # severity 有五个级别（从高到低）：BLOCKER > CRITICAL > NORMAL > MINOR > TRIVIAL
def test_product_list(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "商品列表" in res.get_data(as_text=True)

@allure.feature("商品管理")
@allure.story("添加商品")
@allure.title("添加商品测试--标题")  # 如果不加，则默认为函数名
def test_add_product(client):
    with allure.step("先登录"):   # ⬅️写在函数内部的写法。写在前面的写法类似于：@allure.step("登录操作")
        login(client)

    with allure.step("提交新增商品请求"):    # allure.
        res = client.post("/products/add", data = {"name":"测试商品2", "price":"1.00", "stock":"100"})

    with allure.step("验证重返回 302定向"):
        assert res.status_code == 302

    with allure.step("验证重新定到首页"):
        assert res.headers["Location"] == "/"

@allure.feature("商品管理")
@allure.story("MOCK 商品数据")
def test_product_list_with_mock(client, monkeypatch):
    # 造两条假数据，跳过数据库查询
    fake_products = [(1, "Mock商品", 9.99, 50), (2, "Mock商品2", 19.99, 30)]
    monkeypatch.setattr("app.routes.get_all_products", lambda: fake_products)

    res = client.get("/")
    assert res.status_code == 200
    assert "Mock商品" in res.get_data(as_text=True)
    assert "Mock商品2" in res.get_data(as_text=True)
    assert "商品列表" in res.get_data(as_text=True)