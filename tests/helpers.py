import os

# 测试用公共常量。
# 注：原 login() 辅助函数已由业务封装层 BusinessApi.login() 取代（2026-08-18 全项目不再调用），
#     故 helpers.py 只保留公共常量 TEST_DB。
TEST_DB = os.path.join(os.path.dirname(__file__), "test_ecommerce.db")  # os.path.dirname 指当前文件所在的目录
