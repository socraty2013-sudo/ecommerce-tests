# 统一管理数据库路径、端口等
import os

class Config:
    # abspath拿到完整目录，然后通过两次dirname网上找两级，到达项目根目录，即：/Users/yaben/PycharmProjects/ecommerce-tests/
    # 通过 join, 拼接根目录+执行路径：ecommerce.db
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE = os.path.join(BASE_DIR, "ecommerce.db")