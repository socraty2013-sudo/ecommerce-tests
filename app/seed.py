# seed：种子数据= 数据库的初始数据，负责塞一条初始数据（admin 用户），不然登录时永远查不到用户
# 启动 Flask--三步：激活环境 → 初始化数据库 → 启动 Flask。—— 当前啊你属于第二步


from app.models import init_db
from config.settings import Config
import sqlite3

db_path = Config.DATABASE

# 建表
init_db(db_path)

# 插一条测试初始用户，这里使用admin
# 当前seed.py是独立脚本，不经过 Flask 请求周期，g 不存在。是独立脚本，不经过 Flask 请求周期，g不存在。故只能用sqlite3
conn = sqlite3.connect(db_path)

# conn.execute() 是 sqlite3 的快捷方式，内部自动创建游标、执行、释放，不硬性要求cursor，具体：
    # INSERT/UPDATE/DELETE 这种不需要取返回结果的场景，可以省一行代码。直接用conn.execute().
    # 但 SELECT 必须用 cursor.execute() + fetch，因为你需要拿数据。比如：cursor.fetchall()
conn.execute("INSERT INTO users(username, password) VALUES(?, ?)", ("admin", "123456"))
conn.commit()
conn.close()

print("	ecommerce.db（生产库）-- 数据库初始化完成")