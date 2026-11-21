# 下单+发消息

import pika

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = conn.channel()

# 声明队列：消费端也会声明，保证一定存在；durable 对齐之前学的持久化
channel.queue_declare(queue="q_order", durable=True)

# 模拟 3 笔订单。格式：订单号|商品|数量（用 | 分隔，好拆）
orders = [
    "1001|手机|2",
    "1002|电脑|1",
    "1003|手机|1",
    "1004|手机|1000",
]

for order in orders:
    channel.basic_publish(
        exchange="",
        routing_key="q_order",
        body=order,
        properties=pika.BasicProperties(delivery_mode=2)  # 持久化：重启消息不丢失
    )
    print(f"下单成功：{order} → 已发到 MQ")        # 循环一次，打印一次

conn.close()
print(f"下单完成，共发{len(orders)} 条订单消息")     # 打印循环完后，共发送了多少条消息给到 MQ