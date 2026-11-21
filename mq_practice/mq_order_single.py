import pika, time


QUEUE = "q_seq"
conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = conn.channel()
channel.queue_declare(queue=QUEUE, durable=True)

# 解法一：单消费者串行
# while True 取一条 → 处理 → ack → 再取下一条

count = 0
while True:   # 无限循环，取到队列空为止
    method, _, body = channel.basic_get(queue=QUEUE)   # 拉一条（每次只取一条）
    if method is None:          # 队列空了取不到，退出循环
        break
    time.sleep(0.5)             # 假装处理 0.5 秒
    count += 1
    print(f"第{count}条 处理完成：{body.decode()}")
    channel.basic_ack(delivery_tag=method.delivery_tag)   # 处理完才 ack，再取下一条

print("队列已清空，全部按 FIFO 顺序处理完毕")
conn.close()
