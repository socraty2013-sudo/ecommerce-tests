import pytest

def test_login_page(business_api):   # api是封装的fixture，其返回了ApiClient实例化。
    res = business_api.open_login_page()
    assert res.status_code == 200

# 手动跳转测试
def test_login_redirect_manual(business_api):
    res = business_api.login()
    assert res.status_code == 302
    assert res.headers["Location"]  == "/"   # 302 响应的 Location 头告知浏览器接下来跳去哪。

# 跟随跳转测试，跟随调整
# 需要在请求参数中加 follow_redirects=True。即跳到新页面后，对新页面进行断言。
@pytest.mark.smoke
def test_login_follow_redirect(business_api):
    res_new_page =business_api.login(follow_redirects=True)
    assert res_new_page.status_code == 200
    # ⬇️ res.get_data() 拿到的是响应体，也就是页面的 HTML 源码。默认返回 bytes（二进制），加 as_text=True 转成字符串。字符串再去断言
    # 这里没用 json
    assert "admin" in res_new_page.get_data(as_text=True)

# 登录失败
def test_login_fail(business_api):
    res = business_api.login ("minad", "123456")

    # ⬇️ 当前这个项目是服务端渲染（Flask 直接回 HTML），登录失败返回的是 200 + 一个带错误信息的页面。所以断言 200 是正确的。
    # REST API 项目里，登录失败通常返回 401（Unauthorized）+ JSON 错误信息。这时候才断言 401。
    assert res.status_code ==200
    assert "用户名或密码错误" in res.get_data(as_text=True)

# 退出登录
def test_logout(business_api):
    business_api.login()
    res =business_api.logout()
    assert res.status_code == 302
    assert res.headers["Location"] == "/login"