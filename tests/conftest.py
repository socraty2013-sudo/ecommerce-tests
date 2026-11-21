# 测试基础设施
import os
import sys
import pytest
from tests.common.api_client import ApiClient
from config import config   # 后面的 config 指的是文件中的变量 config，而非文件
from tests.common.business_api import BusinessApi
import allure
from tests.common.logger import trace_id_var
import re   # Python 正则标准库。核心能力：匹配、查找、替换、分割字符串。


# 【必须在 import app 之前】原因：import app 会一路触发 config/__init__.py 执行，
# 而 config 在那一刻就把 ENV 读死了（os.environ.get("ENV", "dev")）。等 import 完再改环境变量就晚了。
# 所以赶在 import 前，先把命令行里的 --env=uat 抠出来、塞进环境变量，config 才能读到 uat。

# 下面 for 循环干的事：从 sys.argv = 命令行的词，切成一个列表，列表里找 "--env=xxx"，把 xxx 抠出来塞进环境变量 ENV。
# 例：敲 `pytest --env=uat -s`，则 sys.argv = ["pytest入口", "--env=uat", "-s"]

for arg in sys.argv:   # arg = 从列表里逐个取出的「词」
    if arg.startswith("--env="):   # 这个词是不是 "--env=" 开头？是就处理，不是（如 "-s"）就跳过
        # 中了 ：把 "=" 后面的值抠出来塞进环境变量（列表下标 1 取获取第二个参数）。
          # "--env=uat".split("=", 1) → ["--env", "uat"]；[1] 取后半 → "uat"
             # 最终效果：os.environ["ENV"] = "uat"
        os.environ["ENV"] = arg.split("=", 1)[1]  # 前面那个 1 是指：第一个=号作为分隔符（当前只有一个=）。


from app import app as application   # 这里加 as xxxx。主要是为了和 fixture 中的 app 区分开来（不要出现同名）。如同名，fixture 的优先级更高
from app.models import init_db
from tests.helpers import TEST_DB

@pytest.fixture(scope="module")      # 加了 scope="module" 解决锁表
def app():
    # 覆盖为测试数据库
    application.config["DATABASE"] = TEST_DB   # application 是导入app实例时，定义的别名

    # 建表
    init_db(TEST_DB)
    # 这里是给测试库（test_ecommerce.db）执行初始化--插入初始化的用户数据（与seed.py中的生产库初始化分开）

    yield application

    # 测试结束，删掉测试数据库
    os.remove(TEST_DB)

@pytest.fixture
def client(app):   # 这里的 app 是上面的 fixture，作为参数传进来，pytest 自动先执行 app fixture，再把结果注入当前函数
    return app.test_client()   # 是 Flask 内置方法，返回一个测试客户端——不需要 flask run，直接就能发 GET/POST 请求。


# 给 pytest「登记」一个新命令行参数 --env（pytest 本来不认识它）。
# pytest 启动时，会自动调用这个「约定好名字」的函数（hook）——你不自己调，pytest 到点自动喊。
# parser 是 pytest 递来的「登记本」，parser.addoption 往上面写一行：
#   参数名 --env；用户没传时默认 dev；help 是敲 --help 时看到的说明。
# 不写这个函数，`pytest --env=uat` 会直接报 "unrecognized arguments"（不认识 --env）。
def pytest_addoption(parser):
    parser.addoption("--env", default="dev", help="运行环境：dev/uat/prod")

@pytest.fixture
def api(client):
    return ApiClient(client)


# 该函数的作用是，通过上方的fixture:api（拿过来时无登录态）的post方法，执行一次登录，然后有登录态了
# 登录态会自动存储到cookie，然后再return “带有登录态的api” 给测试用例函数使用
# 使用当前fixture的测试用例，此时就无需先登录了。比如添加商品，因为已经有登录太了，故直接调用add接口就好了
# 且没写scope，默认范围为funtion，每条使用该夹具的用例，都是新的登录态，互不干扰
@pytest.fixture
def logged_in_api(api):
    # 先登录
    api.post("/login", data={
        "username":config["user"]["username"],
        "password":config["user"]["password"],
    })

    # 登录后，api就有登录态了，再把带有登录态的接口请求工具，返回给测试用例，用例用它直接进行下一步的接口调用
    return api

# 该夹具专门用于无需登录态的接口——比如登录
@pytest.fixture
def business_api(api):
    return BusinessApi(api)

# 用于需要“已登录”状态的接口——比如添加商品
@pytest.fixture
def business_api_logged_in(logged_in_api):
    return BusinessApi(logged_in_api)



def pytest_runtest_makereport(item, call):
    if call.when == "call" and call.excinfo is not None:
        # str(call.excinfo.value) = 把异常转成文字（失败原因）。但这文字里混着「颜色码」——
        # \x1b[0m \x1b[91m 这种看不见的字符，pytest 靠它们把输出染成彩色（红=失败、绿=通过）。
        # 颜色码是给终端看的，浏览器不认，贴进报告就显示成方框乱码。所以要先删掉。
        # re.sub(模式, 替换成什么, 在哪段文字里找) = 按模式找到所有匹配，全换成目标值。
        # 模式 r'\x1b\[[0-9;]*m' 拆开看：
        #   \x1b    = ESC 字符（每个颜色码的开头，就是那个看不见的字符）
        #   \[      = 字面意义的左括号 [（正则里 [ 有特殊含义，加 \ 表示「就是字符 [」）
        #   [0-9;]* = 一坨数字和分号（颜色参数，如 91 / 0 / 39;49;00，数量不定，* 表示任意多个）
        #   m       = 结尾字母 m
        # 整体匹配「\x1b[91m」「\x1b[0m」这种颜色码 → 替换成 ''（空串）= 删掉 → 剩下纯文字
        reason = re.sub(r'\x1b\[[0-9;]*m', '', str(call.excinfo.value))
        allure.attach(
            f"trace_id: {trace_id_var.get()}\n失败原因: {reason}",
            name=f"{item.name} 失败信息",
            attachment_type=allure.attachment_type.TEXT
        )