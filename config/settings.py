# 统一管理数据库路径、端口等
import os
from config import ENV

class Config:
    # abspath拿到完整目录，然后通过两次dirname网上找两级，到达项目根目录，即：/Users/yaben/PycharmProjects/ecommerce-tests/
    # 通过 join, 拼接根目录+执行路径：ecommerce.db
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 按环境拼数据库文件名：dev → ecommerce_dev.db，prod → ecommerce_prod.db
    DATABASE = os.path.join(BASE_DIR, f"ecommerce_{ENV}.db")