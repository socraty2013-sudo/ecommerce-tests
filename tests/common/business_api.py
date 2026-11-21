# 业务封装层：把「业务动作」收成方法，用例只调方法名，不碰 URL
from config import config    #  后面的 config 指的是文件中的变量 config，而非文件

class BusinessApi :
    def __init__(self, api):
        self.api = api

    def login(self, username=None, password=None, **kwargs):
        # ⬇️or 短路语法：有传入则使用入参（左），入参为假值(None/""/0)则使用配置默认值（右）
        # username = username or config["user"]["username"]
        # password = password or config["user"]["password"]

        # 上面两行可以写为下方形式，同效果（除了入参为空值 "" 时。"" 不是 None，保留空字符串，不读 config。但当前场景不存在该情况）
        # 利用 config ，读取相应环境的基础账号密码，避免后续暴露数据信息
        if username is None:
            username = config["user"]["username"]
        if password is None:
            password = config["user"]["password"]
        return self.api.post("/login", data={"username": username, "password": password}, **kwargs)

    def open_login_page(self, **kwargs):  # GET /login，看登录页
        return self.api.get("/login", **kwargs)

    def logout(self, **kwargs):
        return self.api.get("/logout",**kwargs)

    def get_products(self,**kwargs):
        return self.api.get("/",**kwargs)

    def create_product(self, name, price, stock, **kwargs):
        return self.api.post("/products/add", data={"name": name, "price": price, "stock": stock}, **kwargs)

    def delete_product(self, product_id, **kwargs):
        return self.api.post(f"/products/{product_id}/delete", **kwargs)

    def get_product_detail(self, product_id, **kwargs):
        return self.api.get(f"/products/{product_id}", **kwargs)
