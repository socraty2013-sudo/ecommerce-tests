# 多环境配置核心：按环境读对应的 yaml 文件，返回一个字典，全项目共用
import os
import yaml

# ① 当前环境：从环境变量 ENV 读，没设置时默认 dev
ENV = os.environ.get("ENV", "dev")

# ② config 包所在目录（即 config/），用它拼 yaml 路径，不写死相对路径
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config():
    path = os.path.join(CONFIG_DIR, f"{ENV}.yaml")   # ③ 拼 "config/dev.yaml"
    with open(path, encoding="utf-8") as f:          # ④ 打开文件
        return yaml.safe_load(f)                     # ⑤ 解析成字典返回

    # 举例：如 ENV = dev，则：
    # config 现在
    #  = {'env': 'dev',
    #     'base_url': 'http://127.0.0.1:8000',
    #     'user': {'username': 'admin', 'password': '123456'}}


# 模块加载时就读一次，全项目共用这一份配置（在init文件内，python就会自动初始化，相当于其他import时，直接拿初始化好的去用，无需重新每个文件都进行一次实例化）
config = load_config()
