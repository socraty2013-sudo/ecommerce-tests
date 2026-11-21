# 消费 + 扣库存
import pika

# 模拟库存表（真实项目库存存在数据库，这里用字典假装）
STOCK = {"手机": 100, "电脑": 50}


def deduct_stock(product, qty):
    """扣库存：够就扣，不够返回 False。返回 True 才允许 ack。"""
    if product not in STOCK:
        print(f"❌ 商品{product} 不存在")
        return False
    if STOCK[product] < qty:    # 通过商品键去对应商品库存，然后判断剩余库存是否＜需要下单的商品数量，库存不够，则返回 False
        print(f"❌ 库存不足：{product} 只剩 {STOCK[product]}，要扣 {qty}")
        return False
    STOCK[product] -= qty       # 只有上面两个判断都不通过，才会走到这，然后把字典里的库存减去，减去的数量即传入的 qty
    print(f"✅ 扣减成功：{product} -{qty}，剩余 {STOCK[product]}")
    return True


conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = conn.channel()
# 声明队列：消费端也会声明，保证一定存在；durable 对齐之前学的持久化
channel.queue_declare(queue="q_order", durable=True)

while True:
    method, _, body = channel.basic_get(queue="q_order")
    if method is None:
        break
    order_id, product, qty = body.decode().split("|")     # 拆消息：按 | 分成 3 段
    print(f"收到订单 {order_id}：{product} ×{qty}")

    # 从 MQ 读到的消息拆出来，调用deduct_stock() 传入拆出来的【商品名】和【购买数量（需减去的库存）】，让其内部先做判断
    # 返回 True 或 False，True 代表可正常减去相应的库存，走 ack。否则走 nack
    # int(qty) ：上面拆消息得到的变量都是字符串，需转成整型
    if deduct_stock(product,int(qty)):
        channel.basic_ack(delivery_tag=method.delivery_tag)
    else:
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)     # 扣库存失败，不重试