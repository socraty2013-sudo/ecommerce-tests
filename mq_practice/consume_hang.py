import pika
import time

QUEUE = "q_batch"
conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = conn.channel()
channel.queue_declare(queue=QUEUE, durable=True)

# 模拟「消费者正在处理」：取 5 条，每条都捏在手里不 ack
for i in range(5):
    method, _, body = channel.basic_get(queue=QUEUE)
    if method is None:
        break
    print(f"取了但不 ack：{body.decode()}")
    time.sleep(1)

print("5 条已捏在手里（Unacked）。去管理页看一眼，然后回来 Ctrl+C 杀我。")
time.sleep(60)