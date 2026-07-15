from tests.helpers import login

# 数据库连接，判断用户是否存在
def test_admin_user_exists(db):
    cursor = db.cursor()

    # 这里 admin 后面必须加逗号，不加的话就是字符串了,加了是元组
    # cursor.execute() 的第二个参数要求是可迭代对象。如果传 ("admin")，Python 就把字符串当成 5 个字符 'a', 'd', 'm', 'i', 'n' 传给 SQL，直接报错——参数数量对不上
    cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))      # 数据库执行查询，结果集挂在 cursor 内部
    user = cursor.fetchone()       # 从 cursor 的内部结果集里取【第一行】，具体：user = (1, "admin", "123456")
    assert user is not None
    assert user[1] == "admin"      # 这里取下标第二的数据，也就是 admin


# 通过接口新增商品，再用 db 直连数据库验证数据真的落表了
def test_add_product_written_to_db(client, db):
    login(client)
    client.post("/products/add", data = {"name":"测试商品2", "price":"2.00", "stock":"100"})

    cursor =db.cursor()
    cursor.execute("SELECT * FROM products WHERE name = ?", ("测试商品2",))
    product = cursor.fetchone()
    assert product is not None
    assert product[2] == 2.00   #
    assert product[3] == 100