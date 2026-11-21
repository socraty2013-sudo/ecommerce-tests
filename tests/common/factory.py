import uuid
import factory

# 数据工厂函数，根据需求灵活生成参数数据。—— 手写版
def product_factory(**kwargs):
    product = {"name":f"默认商品{uuid.uuid4().hex[:6]}","price":9.99,"stock":50}
    product.update(**kwargs)    # 调用者传了什么字段就覆盖什么，没传保持默认
    return product



# ⬇️当前模块完全学不进去，没懂！

# factory_boy 版：声明式类。Meta.model = dict 表示「造出来的是字典」
# 不写 Meta.model 会报错：model 为空 → 强制抽象，build() 拒绝生成
class ProductFactory(factory.Factory):
    class Meta:
        model = dict
    name = factory.Faker("pystr", max_chars=8)
    price = 9.99
    stock = 50