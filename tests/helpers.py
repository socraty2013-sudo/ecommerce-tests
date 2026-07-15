
# conftest.py 是 pytest 自动加载的特殊文件，不能当普通模块 import，故将login 辅助函数移到了 tests/helpers.py。
def login(client, username="admin", password="123456"):
    return client.post("/login", data={"username": username, "password": password})
