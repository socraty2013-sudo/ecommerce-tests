from tests.pages.login import LoginPage
from tests.pages.products import ProductPage


def test_product_list(page, live_server):
    page.goto(f"{live_server}/login")
    login_page = LoginPage(page, live_server)
    login_page.login()
    assert "商品列表" in page.content()

def test_add_product(page, live_server):
    page.goto(f"{live_server}/login")  # 打开登录页
    login_page = LoginPage(page, live_server)   # 登录类实例化
    login_page.login()   # 执行登录

    product_page = ProductPage(page, live_server)      # 商品类实例化
    product_page.open_add()
    count = product_page.get_product_count()
    product_page.add_product("测试商品3", "1.00", "100")
    assert product_page.get_product_count()  == count +1
    # 商品名现在包在 <a> 链接里（td 的直接文本是空的）→ td:text 匹配不到，改用 td:has-text 找「后代里有这个名字」的格子
    assert page.locator("td:has-text('测试商品3')").is_visible()



"""
allure 测试报告生成步骤及打开

pytest --alluredir=allure-results    →   执行全量符合条件的测试用例。生成原始 JSON 数据
allure generate allure-results -o allure-report  →  把 JSON 转成 HTML——不会浏览器打开
allure serve allure-results          →  一步到位：生成（相当于上一行代码的作用） + 打开浏览器展示报告
"""