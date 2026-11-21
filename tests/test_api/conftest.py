import pytest
from tests.common.factory import product_factory

# 场景 fixture：工厂造数据 + 业务层创建 → 返回「已创建好的商品」，用例直接用，不关心怎么造怎么建
@pytest.fixture
def created_product(business_api_logged_in):
    data = product_factory()                      # ① 工厂造一份新鲜商品数据
    business_api_logged_in.create_product(**data) # ② 业务层创建（302）
    return data                                   # ③ 返回已存在的商品数据




