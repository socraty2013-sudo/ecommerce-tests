from tests.pages.login import LoginPage

def test_login_success(page, live_server):
    page.goto (f"{live_server}/login")    # 从 live_server fixture 拿到 "http://localhost:5555"(macOS 的 AirPlay Receiver 占用了 Flask的5000 端口)
    login_page = LoginPage(page, live_server)   # 实例化
    login_page.login()    # 这里是 login.py 里的 LoginPage 类的方法
    assert login_page.get_current_user() == "admin"

def test_login_fail(page, live_server):
    page.goto(f"{live_server}/login")
    login_page = LoginPage(page, live_server)
    login_page.login(username="admin", password="wrongpassword")  # 传错误密码，断言页面出现错误提示
    assert login_page.get_error_message() == "用户名或密码错误"



"""
allure 测试报告生成步骤及打开

pytest --alluredir=allure-results    →   执行全量符合条件的测试用例。生成原始 JSON 数据
allure generate allure-results -o allure-report  →  把 JSON 转成 HTML——不会浏览器打开
allure serve allure-results          →  一步到位：生成（相当于上一行代码的作用） + 打开浏览器展示报告
"""