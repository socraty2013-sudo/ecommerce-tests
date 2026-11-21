# 模拟依赖场景下单+取消，然后通过传入的延迟时间，模拟去消息「序」的问题，会出现【取消订单】的消费比【下单】的消费快。

import threading, time
import pika


QUEUE = "q_seq"    # 用新队列，不污染 q_order

def consume(name, delay):
    # 每个消费者实例：各自的连接（pika 的连接不能多线程共用）
    conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = conn.channel()
    # 作用：告诉 RabbitMQ，我要这个队列存在；不存在就创建，已经存在就什么都不干，不会报错。——确保队列存在
    channel.queue_declare(queue=QUEUE, durable=True)

    method, _, body = channel.basic_get(queue=QUEUE)
    if method :
        time.sleep(delay)   # 模拟处理耗时：慢/快
        print(f"{name} 处理完成：{body.decode()}")     # body.decode()：pika 拿到的是 bytes 字节对象（二进制），并把对象 → 普通 python 字符串 (str)
        # ⬇️ack 确认——告诉 MQ 「我处理完了，可以删了」
        channel.basic_ack(delivery_tag=method.delivery_tag)
    else:
        print(f"{name}: 队列空")



def send():
    # 每个消费者实例：各自的连接（pika 的连接不能多线程共用）
    conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = conn.channel()
    # 作用：告诉 RabbitMQ，我要这个队列存在；不存在就创建，已经存在就什么都不干，不会报错。——确保队列存在
    channel.queue_declare(queue=QUEUE, durable=True)    # durable=True：队列持久化

    # 按顺序塞，先下单，后取消
    channel.basic_publish(exchange="", routing_key=QUEUE,
                          # delivery_mode=2：【消息持久化】标记 。 = 1 或者不写该行，则为非持久化（瞬态）
                          body="下单：订单 100", properties=pika.BasicProperties(delivery_mode=2))

    channel.basic_publish(exchange="", routing_key=QUEUE,
                          body="取消：订单 100", properties=pika.BasicProperties(delivery_mode=2))

    conn.close()
    print("✅已发送：下单 + 取消(顺序是下单在前)")


send()

# 两个消费者实例并发：实例 A 拿下单（慢2秒），实例 B 拿取消（快0.5秒）
# 调用consume进行消费，开多线程，分别传入时间，但是是取到消息后，在执行 consumer时，才延迟执行消费动作
t1 = threading.Thread(target=consume, args=("实例 A (慢)", 2.0))
t2 = threading.Thread(target=consume, args=("实例 B (快)", 0.5))
t1.start();t2.start()   # 启动多线程
t1.join();t2.join()     # 等待多线程结束

