import pika   # pika:连接 RabbitMQ 的 Python 客户端库（客户端库=让自己写的程序去用别人服务器的现成工具包）。java 用：Spring AMQP（或底层 amqp-client）

# 1. 连上 RabbitMQ（localhost = 本机的 my-rabbit 容器，走 5672 端口）
conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))   # 括号内：构造连接参数对象（没连网络）；括号外，才去发起 TCP 连接，返回连接实例
channel = conn.channel()   # conn为TCP的构建，channel 为在这条 TCP 连接里面，开辟一个【逻辑信道】。可以开根据业务开多条

# 2.声明队列：q_order (管理页建的那个，这里只是「打开」它)。参数必须和现有队列一致：durable=True，否则又 406。durable：持久化）
    # 作用：告诉 RabbitMQ，我要这个队列存在；不存在就创建，已经存在就什么都不干，不会报错。——确保队列存在
channel.queue_declare(queue="q_order" ,durable=True)


# 3. 往 q_order 发一条消息
    # 发送消息，用 basic_publish
    # exchange：交换机名字，这里传 `""` → 默认交换机；routing_key：路由键，消息投递的目标队列名；body：真正要发送的消息内容
channel.basic_publish(exchange="", routing_key="q_order", body="下单：订单123")
print("✅ 已发出：下单：订单123")

# 关连接
conn.close()