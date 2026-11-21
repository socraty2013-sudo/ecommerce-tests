import pika

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = conn.channel()

# 打开 q_order（参数必须和现有队列一致：durable=True，否则又 406）
channel.queue_declare(queue="q_order", durable=True)

# method, properties, body 是 rabbitmq 协议封装出来的三层协议返回值，有值时可以直接解包赋值给左侧。
    # method：投递信息（里面有 delivery_tag，是这条消息的编号）
    # properties：附加属性（暂时用不上）——所以这里暂时用_下划线占位即可（必须是三个参数，否则对不上 MQ 返回的内容）
    # body：消息内容（就是「下单：订单123」）
method, _, body = channel.basic_get(queue="q_order")
if method:     # 等价于 if method is not None:
    print("✅ 取到消息：", body.decode())  # body.decode() ，把取出来的字节转成 python 字符串
    # 关键一行：ack 确认 —— 告诉 MQ 「我处理完了，可以删了」
    channel.basic_ack(delivery_tag=method.delivery_tag)
    print("✅ 已 ack，消息将从队列删除")
else:
    print("队列为空")

conn.close()
