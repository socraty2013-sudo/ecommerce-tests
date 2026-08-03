# ⬇️ 用 Locust 模拟大量用户每隔 1 秒循环访问指定网站首页做压力测试。

from locust import HttpUser, task, constant, LoadTestShape
import sqlite3

# ===== 定义模拟用户类，继承 HTTP 压测用户 =====
class MyUser(HttpUser):     # HttpUser：模拟一个「用户」，能做多个任务

    # on_start 是 Locust 预留的方法名（固定名），框架自动识别——每个用户对象创建后自动调用一次（不重复）。如果加了 @task 反而把它变成了普通循环任务，逻辑就错了。
    def on_start(self):
        self.client.post("/login", data={"username":"admin", "password":"123456"})

    # 标记下方函数是压测执行的业务任务，即每个用户具体干什么事（发请求）
    # 5 代表权重，数字越大，权重越高，性能测试过程中相应操作占比就越多。不写(N)，则默认为权重 1
    @task(5)
    def browse_products(self):    # 任务函数，模拟访问首页（商品列表页）
        self.client.get("/")      # 发起 GET 请求访问网站根路径。具体目标域名 / IP 不在代码里写，启动命令中 --host 传入：locust -f 你的脚本名.py --host=http://127.0.0.1:5000

    wait_time = constant(1)     # 单个虚拟用户做完一件事后，休息1s，再执行下一次请求，最左侧的 icon（同心圆+箭头），代表：「重写父类属性」。

    @task(1)
    def add_product(self):
        self.client.post("/products/add", data={"name":"压测商品", "price":"99", "stock":"100"})

    def on_stop(self):   # 该方法在分布式时，需注释/删除，以避免 worker A完成了压测，但 B 没完成时，把 B 所需的数据给删除了。
        conn = sqlite3.connect("ecommerce.db")
        conn.execute("DELETE FROM products WHERE name = '压测商品'")
        conn.commit()
        conn.close()

# ===== LoadTestShape：用代码定义多阶段压测场景 =====
# 用了 LoadTestShape后，CLI 的 -u -r --run-time 就不用传了——一切由 tick() 接管

class MyShape(LoadTestShape):
    # 阶段列表：按时间顺序依次执行
    # stages ：类属性，属于整个类，类下方法引用时，需要用self.stages（惯例。当然也能用）
    # stages =[
    #     {"duration": 30, "users": 10, "spawn_rate": 5},     # 阶段1：预热，30秒内爬到 10 用户
    #     {"duration": 60, "users": 50, "spawn_rate": 10},    # 阶段2：加压，60秒内爬到 50 用户
    #     {"duration": 60, "users": 100, "spawn_rate": 10},   # 阶段3：高压，30秒内爬到 100 用户
    # ]

    # 摸高参数⬇️
    stages = [
        {"duration": 30, "users": 80, "spawn_rate": 10},  # 热身
        {"duration": 30, "users": 120, "spawn_rate": 10},  # 加压——执行了 locust -f locustfile.py --headless --host=http://127.0.0.1:5000 --html=surge_report.html，得到临界峰值在 120 用户
        {"duration": 30, "users": 150, "spawn_rate": 10},  # 逼近
        {"duration": 30, "users": 170, "spawn_rate": 10},  # 摸高
        {"duration": 30, "users": 190, "spawn_rate": 10},  # 冲击
    ]

    def tick(self):
        """
        Locust 每秒调用一次这个方法，不需要手动调用
        返回 (目标用户数, 爬升率) → Locust 自动调整并发
        返回 None → 测试结束
        """
        run_time = self.get_run_time()           # 测试已运行的秒数。get_run_time 是 MyShape(LoadTestShape) 继承过来的，直接能用，不需要自己声明

        accumulated = 0                          # 累加 duration，找到当前处于哪个阶段。accumulated（累计的）：局部变量（全局变量卸载类的外层）。函数每次被调用，进来都执行这一行时，accumulated 永远是全新的 0。
        for stage in self.stages:                # 【类方法】使用【类变量】时，需要用self.xxx，活用MyShape.xxxx
            accumulated += stage["duration"]
            if run_time < accumulated:           # 该判断不成立，则不 return，继续一个 for 循环的参数；该判断成立，则走return，且不再进行下一个for循环
                return (stage["users"],stage["spawn_rate"] )

        return None  # 三轮 if 都不成立，for循环没有可读参数了。自然往下走到这，return None。Locust 收到 None 就停止测试。



"""
关于上述tick()方法的执行流程，数据流转理解及注释：

第1轮：前30s内，
 1.每秒钟滴调用一次调用tick()，accumulated 都会重置为0，故accumulated这段区间内，一直都是0+30。
 2.run_time前 30s 内，一定小于30，故一直return 用户数为10，爬坡率为5。也就是第一阶段。
 3.run_time < accumulated 的对比一直成立，然后走下面return，且不再继续下一轮的for循环。

第二轮:到了30s--89s
 1.假设到了30s，则run_time(30s) < accumulated(0+30)-->不成立-->下一轮-->读取到 duration = 60s。
 2.因函数没有停止，故accumulated不会重置。此时已为accumulated = 30+60 = 90。然后再比对run_time(30s) < accumulated(90)，成立。return第二阶段的参数，结束当前函数，不进行下一轮的for循环
 3.30s--89s重复上述动作，for循环两轮后终止函数执行
 4.90s--150s同上。
 
第三轮:三轮都已执行完
 1. 三轮参数if判断都不通过的时候，for循环就无入参了，跳出了for循环，方法继续往下走到return None 
"""

