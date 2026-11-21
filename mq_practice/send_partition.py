import pika

QUEUES = [f"q_order_{i}" for i in range(3)]   # q_order_0 / q_order_1 / q_order_2

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = conn.channel()

for q in QUEUES:
    channel.queue_declare(queue=q, durable=True)

# 4 条消息：(订单号, 动作)，订单100的下单/取消 + 订单101的下单/取消
msgs = [(100, "下单"), (100, "取消"), (101, "下单"), (101, "取消")]

for order_id, action in msgs:
    q = QUEUES[order_id % 3]      # 关键：按订单号取模路由，同一个订单永远进同一个队列。假设order_id =100, 则 QUEUES[order_id % 3] = QUEUES[100 % 3] = QUEUES[1] = q_order_1
    channel.basic_publish(exchange="", routing_key=q, body=f"订单{order_id} {action}")
    print(f"订单{order_id} {action} → 进 {q}")

conn.close()