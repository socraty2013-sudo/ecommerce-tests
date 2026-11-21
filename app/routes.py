import hmac
import hashlib

from app import app
from flask import render_template, request,session,redirect
from app.models import get_user, get_all_products, get_product, create_product, delete_product as delete_product_db
from functools import wraps

# 支付接口的签名密钥（测试环境固定值，生产环境走环境变量）
PAY_SECRET = "ecommerce_test_secret_2026"


def calc_sign(params, secret=PAY_SECRET):
    """签名规则：参数按 key 字典序拼成 k=v&k=v（排除 sign），再用 HMAC-SHA256 加密钥"""
    s = "&".join(f"{k}={params[k]}" for k in sorted(params) if k != "sign")
    return hmac.new(secret.encode(), s.encode(), hashlib.sha256).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated


# 访问 http://localhost:5000/（Flask开发服务器默认地址） → Flask 找到 index() → 返回 product_list.html 页面
@app.route('/')     # / —— 根目录，也就是首页
def index():
    products = get_all_products()  # 获取所有商品数据
    return render_template("product_list.html", products=products)  # 模板渲染，返回html页面

# 登录页
@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":     # request 是Flask内置的接收请求用的（后面没有s）
        username = request.form["username"]     # 取用户提交的取表单数据
        password = request.form["password"]
        user = get_user(username)    # 查数据库

        # if user 先判断是否查到用户，避免空值报错。然后再获取元素第三个字段数据取和传进来的密码比对
        if user and user[2] == password:    # 比对密码。fetchone 返回元组，索引 2 是 password 列
            session["user"] = username   #  比对通过，写 session。记住当前登录用户
            return redirect("/")   # redirect("/xxx")，此后给你定下给你到另一个页面（这里跳转首页）
        else:
            return render_template("login.html", error="用户名或密码错误")
    else:
        return render_template("login.html")


# 【本次新迭代，开发新交付的接口】加密登录：前端已经把密码 md5 过，后端只比对哈希
@app.route("/login_enc", methods=["GET", "POST"])
def login_enc():
    if request.method == "POST":
        username = request.form["username"]
        password_hash = request.form["password"]
        user = get_user(username)

        if user and user[3] == password_hash:   # 索引 3 是 password_hash 列
            session["user"] = username
            return redirect("/")
        else:
            return render_template("login.html", error="用户名或密码错误")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():

    # 删掉 session 里的 user 键，第二个参数 None 表示如果 user 不存在也不报错。
    session.pop("user", None)
    return redirect("/login")

@app.route("/products/add", methods =["GET","POST"])
@login_required   # agent 写了个装饰器，作用是防止越权（鉴定user 是否在 session 中）
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])   # 拿到的是字符串，通过float转成浮点型后再存
        stock = int(request.form["stock"])     # 拿到的是字符串，通过int转成整型后再存

        create_product(name, price, stock)
        return redirect("/")
    else:
        return render_template("product_add.html")


# 【本次新迭代，开发新交付的接口】删除商品：登录后才能删，删完回首页
@app.route("/products/<int:product_id>/delete", methods=["POST"])
@login_required
def product_delete(product_id):
    delete_product_db(product_id)
    return redirect("/")


# 【本次新迭代，开发新交付的接口】商品详情页：看单个商品的完整信息；不存在则 404
@app.route("/products/<int:product_id>")
def product_detail(product_id):
    product = get_product(product_id)
    if product is None:
        return render_template("product_not_found.html"), 404
    return render_template("product_detail.html", product=product)


# 【本次新迭代，开发新交付的接口】支付：必须带合法签名，否则拒绝
@app.route("/pay", methods=["POST"])
def pay():
    params = request.form.to_dict()
    sign = params.pop("sign", None)

    # compare_digest 是定长比较，防止通过响应时间差猜测签名（时序攻击）
    if not sign or not hmac.compare_digest(sign, calc_sign(params)):
        return {"code": 400, "msg": "签名错误"}, 400

    return {"code": 0, "msg": "支付成功", "order_id": params.get("order_id")}
