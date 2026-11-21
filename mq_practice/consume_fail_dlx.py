import pika
import time

# ===== 三个名字 =====
DLX = "dlx_demo"          # 死信交换机名
DEAD_QUEUE = "q_dead"     # 死信队列名
MAIN_QUEUE = "q_dlx_main" # 主队列名（全新名字，避免和旧队列参数冲突 406）

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = conn.channel()

# ===== 1. 建死信交换机 =====
# 之前你声明队列用 queue_declare；声明交换机用 exchange_declare，多一个 exchange_type 指定类型
channel.exchange_declare(exchange=DLX, exchange_type="direct")

# ===== 2. 建死信队列 + 绑定 =====
# 死信队列就是普通队列
channel.queue_declare(queue=DEAD_QUEUE, durable=True)
# 绑定：把死信队列挂到 DLX 交换机上，路由键 dead
# 之后 DLX 用「dead」这个路由键，把消息送进死信队列
channel.queue_bind(queue=DEAD_QUEUE, exchange=DLX, routing_key="dead")

# ===== 3. 建主队列，带上死信参数（关键）=====
# arguments 告诉 MQ：「主队列里被判死的消息，投给 dlx_demo，路由键用 dead」
channel.queue_declare(queue=MAIN_QUEUE, arguments={
    "x-dead-letter-exchange": DLX,
    "x-dead-letter-routing-key": "dead",
})

# ===== 4. 发 5 条消息到主队列 =====
for i in range(1, 6):
    channel.basic_publish(exchange="", routing_key=MAIN_QUEUE, body=f"订单{i}")
print("已发送 订单1~订单5 到主队列")

# ===== 5. 消费主队列：订单5 判死，其余 ack（和 consume_fail.py 几乎一样）=====
while True:
    method, _, body = channel.basic_get(queue=MAIN_QUEUE)
    if method is None:
        break
    text = body.decode()
    if text == "订单5":
        print(f"❌ 处理失败：{text}，requeue=False → 判死 → 进死信队列")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # ← 只改这一个参数！
        time.sleep(0.3)
    else:
        print(f"✅ 处理成功：{text}")
        channel.basic_ack(delivery_tag=method.delivery_tag)

# ===== 6. 死信消费者：从死信队列取消息（模拟人工处理）=====
print("\n===== 死信消费者 =====")
while True:
    method, _, body = channel.basic_get(queue=DEAD_QUEUE)
    if method is None:
        break
    print(f"🟡 死信里的消息：{body.decode()}  ← 人工排查/补偿/修bug后重发")
    channel.basic_ack(delivery_tag=method.delivery_tag)

conn.close()