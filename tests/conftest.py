# 测试基础设施

import pytest
import os
from app import app as application   # 这里加 as xxxx。主要是为了和 fixture 中的 app 区分开来（不要出现同名）。如同名，fixture 的优先级更高
from app.models import init_db
import sqlite3

TEST_DB = os.path.join(os.path.dirname(__file__), "test_ecommerce.db")  # os.path.dirname 指当前文件所在的目录

@pytest.fixture(scope="module")      # 加了 scope="module" 解决锁表
def app():
    # 覆盖为测试数据库
    application.config["DATABASE"] = TEST_DB   # application 是导入app实例时，定义的别名

    # 建表
    init_db(TEST_DB)
    # 这里是给测试库（test_ecommerce.db）执行初始化--插入初始化的用户数据（与seed.py中的生产库初始化分开）
    conn = sqlite3.connect(TEST_DB)
    conn.execute("INSERT INTO users(username, password) VALUES (?, ?)", ("admin", "123456"))
    conn.commit()
    conn.close()

    yield application

    # 测试结束，删掉测试数据库
    os.remove(TEST_DB)

@pytest.fixture
def client(app):   # 这里的 app 是上面的 fixture，作为参数传进来，pytest 自动先执行 app fixture，再把结果注入当前函数
    return app.test_client()   # 是 Flask 内置方法，返回一个测试客户端——不需要 flask run，直接就能发 GET/POST 请求。


@pytest.fixture
# db 里传 app 参数的作用是保证执行顺序——pytest 先跑完 app（建库、建表、插用户），再跑 db（开一个新连接给测试用）。
# 不能直接用前面的 app 里的数据库连接，因为它在 yield 之前就 conn.close() 关掉了。所以这里要重新连。
# 这两个 fixture 各开各的连接，互不影响。
def db(app):
    conn =sqlite3.connect(TEST_DB)
    yield conn
    conn.close()

import threading
import time
import requests

@pytest.fixture(scope="module")     # 加了 scope="module" 解决锁表
def live_server(app):
    port = 5555
    server = threading.Thread(target=app.run, kwargs={"port": port, "use_reloader": False})
    server.daemon = True
    server.start()

    # 等服务器真正启动完毕再返回地址
    url = f"http://localhost:{port}"
    for _ in range(30):
        try:
            requests.get(url, timeout=0.1)
            break
        except requests.ConnectionError:
            time.sleep(0.1)

    yield url

    # 测试结束后停掉线程——daemon 线程在主进程退出时自动关闭，这里可以不做额外处理
    # 但用 yield 保证测试执行完才退出，server 生命周期和测试绑定

