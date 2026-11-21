import pika

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = conn.channel()
channel.queue_declare(queue="q_order", durable=True)

method, _, body = channel.basic_get(queue="q_order")
if method:
    print("❌ 取到了消息，但不 ack：", body.decode())
    print("   连接直接关闭……消息会被 MQ 放回队列")
else:
    print("队列是空的")

conn.close()   # 关键：关连接时这条消息没 ack，MQ 会把它重新放回队列