import logging
import uuid
import contextvars

# ① 储物柜：存「当前请求」的 trace_id
trace_id_var = contextvars.ContextVar("trace_id", default="-")  # trace_id_var 是线程本地存储容器

def new_trace_id():
    tid = uuid.uuid4().hex[:8]   # hex 去掉所有分隔线
    trace_id_var.set(tid)
    return tid   # set() 返回 Token 不是 tid；留给 ApiClient 写请求头 X-Trace-Id 用

# ② 打印机：每条日志生成时，自动把柜子里的 id 印上去
class TraceIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = trace_id_var.get()
        return True

# ③ 配置 logger
logger = logging.getLogger("ecommerce")
logger.setLevel(logging.INFO)
h = logging.StreamHandler()
h.setFormatter(logging.Formatter("%(asctime)s [%(trace_id)s] %(levelname)s %(message)s"))
h.addFilter(TraceIdFilter())
logger.addHandler(h)


SENSITIVE_KEYS = {"password", "token", "secret", "access_token"}  # 设置一个敏感变量的【集合】（比列表块，且不重复、无序）
def mask(data):
    # isinstance：判断数据（data）类型是不是 dict（字典）
    # 整句意思：判断入参是否为字典，如果不是字典，则直接返回 data。是字典，则不直接返回，继续走下方代码。
    # 兼容字典和非字典。以后万一有人在没 data 的地方调 mask，传个 None 进来不会炸。
    # not isinstance(x, dict) → 对「判断结果」取反（当前用法）。而 x is not ... → 比「两个对象是不是同一个」。
    if not isinstance(data, dict):
        return data
    out={}
    for key, value in data.items():
        if key in SENSITIVE_KEYS:
            out[key] = "****"
        else:
            out[key] = value
    return out