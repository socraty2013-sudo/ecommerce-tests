# 所有和 SQLite 打交道的代码封装成函数
import sqlite3
import hashlib
from flask import g


def init_db(db_path):  # 这里不用g.db。因为该方法启动时调用，不在请求上下文里，g 根本不可用，必须自己建连接
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    create_sql1 = """
    CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL,
    stock INTEGER
    )
    """

    create_sql2 = """
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        password_hash TEXT
    )
    """

   # 补充知识点1：如果cursor.execute()执行的sql是查询，且查询的数据需要使用，则之后必须fetchall()/fetchone()/fetchmany(n)
   # 补充知识点2：INSERT、UPDATE、DELETE 之后必须 commit()，否则数据不落盘。当前CREATE TABLE 这类 DDL 语句，SQLite 自动提交，不加commit()也没事
    cursor.execute(create_sql1)
    cursor.execute(create_sql2)

    # 老库兼容：表已存在时 CREATE TABLE IF NOT EXISTS 不会补列，需要手动 ALTER
    cols = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
    if "password_hash" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")

    # 种子数据：确保 admin 账号始终存在（INSERT OR IGNORE 遇到重复 username 时静默跳过，不报错）
    cursor.execute("INSERT OR IGNORE INTO users(username, password) VALUES (?, ?)", ("admin", "123456"))

    # 加密登录账号：库里只存 md5 结果，不存明文
    pwd_hash = hashlib.md5("123456".encode()).hexdigest()
    cursor.execute("INSERT OR IGNORE INTO users(username, password_hash) VALUES (?, ?)", ("admin_enc", pwd_hash))
    conn.commit()

    conn.close()  # 注意，这里用的是conn，不是cursor。这里关闭连接后，游标cursor也会关联失效。


def get_user(username):
    cursor = g.db.cursor()
    # ?：占位符，防止 SQL 注入，代替要传入的值； (username,)：元组，存放对应占位符的数据，逗号不能少，代表是元组
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchone()


def get_all_products():
    cursor = g.db.cursor()
    cursor.execute("SELECT * FROM products")
    return cursor.fetchall()


def get_product(product_id):
    """按 id 查单个商品；没有则返回 None（开发本次交付）。"""
    cursor = g.db.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    return cursor.fetchone()

def create_product(name, price,stock):  # stock：库存
    cursor = g.db.cursor()
    # ? 占位符:防止SQL注入。数据库驱动先把 SQL 模板和参数分开发过去，参数无论是什么内容，都只被当"数据"，不会被当"SQL 命令"执行。DROP TABLE 那一套在这里就失效了。
    # 下面这个写法叫【参数化查询】，防止SQL注入。可以理解为execute(sql,(v1,v2,v3)),sql为形参，等待第二个实参的值进来，然后执行sql
    cursor.execute("INSERT INTO products(name, price,stock) VALUES (?, ?, ?)",(name, price, stock))
    g.db.commit()   # INSERT、UPDATE、DELETE 之后必须 conn.commit()


def delete_product(product_id):
    """删除指定 id 的商品（开发本次交付的新功能）。"""
    cursor = g.db.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    g.db.commit()
    return cursor.rowcount   # 受影响行数：1=删到了，0=没这个商品