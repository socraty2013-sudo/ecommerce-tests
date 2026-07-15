class LoginPage:
    # page 是 Playwright 的 pytest 插件 自动提供的 fixture。
    # 安装 pytest-playwright 后，直接在测试函数参数里写 page，pytest 就会自动注入一个浏览器页面对象进来
    def __init__(self, page, base_url):
        self.page = page
        self.base_url = base_url

    def open(self):
        self.page.goto(f"{self.base_url}/login")

    def login(self, username = "admin", password = "123456"):
        self.page.fill("input[name='username']" ,username)
        self.page.fill("input[name = 'password']" ,password)
        self.page.click("button[type=submit]")

    def get_error_message(self):
        # html: <p style="color:red">{{ error }}</p>. text_content() 就是取标签里的纯文字内容
        # 按属性找：找 style 属性值等于 "color:red" 的 p 标签
        return self.page.text_content('p[style="color: red;"]')

    def get_current_user(self):
        # <p>当前用户：admin | …………
        text = self.page.text_content('p:has-text("当前用户")')  # 当前标签<p>下没有 id/name 等属性，故只能用 has-text 按文字定位——它是没属性可用的备用方案
        return text.split("：")[1].split(" ")[0]
