from config import config

def test_env():
    print("当前环境 =", config["env"], "| base_url =", config["base_url"])

