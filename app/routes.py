from app import app
from flask import render_template, request,session,redirect
from app.models import get_user, get_all_products, create_product  # 这里必须得加【app.】 ，即使在同目录下也要加


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


@app.route("/logout")
def logout():

    # 删掉 session 里的 user 键，第二个参数 None 表示如果 user 不存在也不报错。
    session.pop("user", None)
    return redirect("/login")

@app.route("/products/add", methods =["GET","POST"])  # 接口存在多个请求方式时，需用methods。必须加s
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])   # 拿到的是字符串，通过float转成浮点型后再存
        stock = int(request.form["stock"])     # 拿到的是字符串，通过int转成整型后再存

        create_product(name, price, stock)
        return redirect("/")
    else:
        return render_template("product_add.html")




