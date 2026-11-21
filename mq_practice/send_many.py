import pika

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = conn.channel()
channel.queue_declare(queue="q_order", durable=True)      # 声明队列，队列持久化标记

# 连发 5 条消息
for i in range(1, 6):    # i=1~5
    channel.basic_publish(
        exchange="",    # ← 使用默认交换机，创建时默认持久化为 True
        routing_key="q_order",
        body=f"订单{i}",
        properties=pika.BasicProperties(delivery_mode=2)     # ← delivery_mode=2：消息持久化标记 。 = 1 或者不写该行，则为非持久化（瞬态）
    )
    print(f"✅ 已发出：订单{i}")

conn.close()