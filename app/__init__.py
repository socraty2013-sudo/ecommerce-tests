# 创建 Flask 应用实例
# 当前文件中，的1️⃣～4️⃣，是专门针对“活的”/随时需要调整的数据库地址而注释的数据流转笔记，便于自己的理解
# 启动Flask： .venv/bin/python -m flask run --port=5555

from flask import Flask, g, current_app
from config import settings
import sqlite3


# 创建app实例
# 1️⃣ Flask 自动在 app 里面造了一个空字典，叫 app.config。此时它里面什么都没有。
app = Flask(__name__)    # __name__是 Python 内置变量，等于当前模块的名字。Flask 靠它来定位模板（templates）和静态（static）文件的位置。
app.secret_key = "dev"   # session 加密用的密钥，开发环境随便写，后续 Docker 部署走环境变量

# 把 Config 类里的全部大驼峰属性加载为 Flask 配置，之后可以用
# 2️⃣ 把 Config 类里的 DATABASE = "ecommerce.db" 拷贝进那个空字典。app.config = {"DATABASE": "ecommerce.db"}
app.config.from_object(settings.Config)   # from_object 拷贝作用


# 每个请求到来【前】自动执行，在此建立数据库连接并挂在 g.db 上。g 的作用是自动连接/释放生命周期管理。
@app.before_request
def before_request():
    # g 是 Flask 内置的一个全局临时对象，存储本次请求共用资源（数据库连接、用户信息），全路由/装饰器可直接读取，不用反复传参。——每个请求来时拿到同一个连接，请求结束后自动关闭。
    # g.db = sqlite3.connect(settings.Config.DATABASE)   # 拿到数据库地址，连接。并挂给左侧的g.db。——写死了地址，多环境状态下调整麻烦,故用下方的方法


    # 3️⃣ 从字典里通过键：DATABASE，取出 "ecommerce.db" 这个值，用来连接数据库。current_app 就是当前正在运行的 app 的引用，current_app.config 就是上面2️⃣那个字典。
    #     相当于：current_app.config["DATABASE"]  →  "ecommerce.db"
    g.db = sqlite3.connect(current_app.config["DATABASE"])

    # 4️⃣ app.config["DATABASE"] = "test_ecommerce.db"  假设是要创建新的测试数据库。在 conftest 中配置





# 每个请求【结束】（无论成功还是出错）后自动执行，从 g 中取出 db 连接并关闭
@app.teardown_appcontext
def teardown(exception):

    # 取出 g 里键名为 db 的值（也就是数据库连接对象），后直接从 g 里删掉这个 db，避免残留。
    # 参数 None：如果 g 里根本没有 db，不会报错，直接返回 None
    db = g.pop("db", None)

    # 拿到连接就关闭数据库，释放资源；没拿到就什么都不做。
    if db is not None:    # 或写成 if db:
        db.close()


# 1.routes.py 里的 @app.route("xxxx") 是"注册动作（所有都是），但此时仅是定义，Flask并不知道有这些路由
# 2.放在最后的原因是，初始化时，需要先创建app后，才能考虑后续的路由问题，如果放在最前面导入后，其实就是执行routes.py，但此时都没创建app，会直接报错。
# 3. 真实的Flask项目，都要进行这一步的导入
from app import routes
