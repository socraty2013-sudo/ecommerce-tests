# partition--分隔/分割

import pika
import time
import threading

QUEUES = [f"q_order_{i}" for i in range(3)]

def consume(name, q):
    conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = conn.channel()       # 复习：pika 连接不能多线程共用，每个消费者自己建连接
    while True:
        method, _, body = channel.basic_get(queue=q)       # 从 q 队列（调用时传入），获取相关的消息
        if method is None:
            break
        time.sleep(0.5)
        print(f"{name} 处理：{body.decode()}")
        channel.basic_ack(delivery_tag=method.delivery_tag)
    conn.close()


# 前面这几行是列表推导式： threads = [ ... for q in QUEUES ]。 q 从 for 循环中取
# for 循环从 QUEUES 中，逐一取出 q_order_N——这是个字符串
# 通过下标-1，取到 0/1/2。最后consume的第一个入参为：消费者-队列 0（但q_order_0 ）
threads = [
    threading.Thread(target=consume, args=(f"消费者-队列{q[-1]}", q))
    for q in QUEUES
]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("三个队列都已清空")
