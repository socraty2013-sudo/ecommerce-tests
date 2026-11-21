# batch : 一组/一批

import pika

QUEUE = "q_batch"
conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = conn.channel()
channel.queue_declare(queue=QUEUE, durable=True)


for i in range(1, 101):     # 发 100 条消息
    channel.basic_publish(exchange="", routing_key=QUEUE, body=f"订单{i}")
    print(f"已发出：订单{i}")

conn.close()
print("发出完毕：100 条全在队列里等着")