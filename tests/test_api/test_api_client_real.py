from tests.common.api_client import ApiClient
from config import config
from types import SimpleNamespace


def test_real_mode_uses_base_url(monkeypatch):
    captured ={}
    def fake_get(url, **kwargs):
        captured["url"] = url
        # SimpleNamespace(status_code=200) 造一个轻量对象，它有个 .status_code 属性，值 200（随便填，这个测试不断言状态码，只要代码里 res.status_code 不炸就行）。
        return SimpleNamespace(status_code=200)  # 补上返回值：假响应带 status_code


    monkeypatch.setattr("requests.get", fake_get)   # 把「全局唯一那份 requests.get 名字」临时指到 fake_get

    api = ApiClient(base_url=config["base_url"])   # config 是字典 → dev 环境 → 用 key 取 → "http://127.0.0.1:8000"
    api.get("/products")

    assert captured["url"] == config["base_url"] + "/products"