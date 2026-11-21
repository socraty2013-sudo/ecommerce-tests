import pika
import time

QUEUE = "q_batch"
conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = conn.channel()
channel.queue_declare(queue=QUEUE, durable=True)

count = 0
while True:
    method, _, body = channel.basic_get(queue=QUEUE)
    if method is None:
        break
    count += 1     # ← 在这里：只要「取到」就 +1，不管成败
    text = body.decode()
    if text == "订单5":                                 # 模拟这条消息处理失败
        print(f"❌ 处理失败：{text}，放回队列重试")

        # basic_nack = 否定确认（negative ack），跟 basic_ack 相反，告诉 MQ「这条我没处理好」
            # requeue = True = 放回队列重新排队（队首）；
            # requeue = False = 不放回（丢弃/或投进死信队列留档）—— 真实生产绝不允许无限重投——必须「重试 N 次后放弃」，否则一条脏数据能拖垮整个队列。
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        time.sleep(0.3)
    else:
        print(f"✅ 处理成功：{text}")
        channel.basic_ack(delivery_tag=method.delivery_tag)

print(f"处理了 {count} 条")