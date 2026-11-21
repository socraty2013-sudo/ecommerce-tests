import requests
from tests.common.logger import new_trace_id, logger, mask

class ApiClient:

    def __init__(self, client=None, base_url=None):
        self.client = client
        self.base_url = base_url
        self.headers = {}

    def get(self, path, **kwargs):
        tid = new_trace_id()
        self.headers["X-Trace-Id"] = tid
        if self.client:
           res = self.client.get(path,headers=self.headers, **kwargs)
        else:
           res = requests.get(self.base_url + path, headers=self.headers, **kwargs)
        logger.info(f"GET {path} -> {res.status_code}")  # 打日志：方法+路径+状态码
        return  res


    def post(self, path, data=None, **kwargs):
        tid = new_trace_id()
        self.headers["X-Trace-Id"] = tid
        if self.client:
            res = self.client.post(path, data =data, headers=self.headers, **kwargs)
        else:
            res = requests.post(self.base_url+path, data =data, headers=self.headers, **kwargs)
        logger.info(f"POST {path} 入参：{mask(data)} -> {res.status_code}" )
        return res