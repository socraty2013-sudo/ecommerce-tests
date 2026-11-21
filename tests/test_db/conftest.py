import pytest
import sqlite3
from tests.helpers import TEST_DB


@pytest.fixture
# db 里传 app 参数的作用是保证执行顺序——pytest 先跑完 app（建库、建表、插用户），再跑 db（开一个新连接给测试用）。
# 不能直接用前面的 app 里的数据库连接，因为它在 yield 之前就 conn.close() 关掉了。所以这里要重新连。
# 这两个 fixture 各开各的连接，互不影响。
def db(app):
    conn =sqlite3.connect(TEST_DB)
    yield conn
    conn.close()

