import pika
import time

QUEUE = "q_batch"
conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = conn.channel()
channel.queue_declare(queue=QUEUE, durable=True)

count = 0
while True:
    # 【拉】模式 basic_get ，进程同时去队列里抢
    # 【推】模式 basic_consume（Round-Robin），MQ 是发牌员，会精确轮流发
    method, _, body = channel.basic_get(queue=QUEUE)
    if method is None:
        break
    count += 1      # ← 只要「取到」就 +1，不管成败
    time.sleep(1)   # 每次循环休息一秒后再发确认——可以看管理页积压的消息逐秒减1
    print(f"第{count}: {body.decode()}")
    channel.basic_ack(delivery_tag=method.delivery_tag)

print(f"共消费 {count} 条，队列已清空")
conn.close()

