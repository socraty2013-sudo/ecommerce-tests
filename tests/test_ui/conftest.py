import threading
import time

import allure
import requests
import pytest


# 创建子线程（起 flask 服务），为了与主线程（跑 pytest 断言）做出线程的区分
@pytest.fixture(scope="module")     # 加了 scope="module" 解决锁表
def live_server(app):
    port = 5555
    # 登记一个「子线程」，它的活 = 执行 app.run。干活的参数 = 监听 5555 端口，关热重载
    server = threading.Thread(target=app.run, kwargs={"port": port, "use_reloader": False})
    server.daemon = True   # 标记：主线程一结束，程序直接退出，子线程被硬拽走、强制中断，不让他赖着不走。
    server.start()

    # 等服务器真正启动完毕再返回地址
    url = f"http://localhost:{port}"
    for _ in range(30):
        try:
            requests.get(url, timeout=0.1)
            break
        except requests.ConnectionError:
            time.sleep(0.1)

    yield url

    # 测试结束后停掉线程——daemon 线程在主进程退出时自动关闭，这里可以不做额外处理
    # 但用 yield 保证测试执行完才退出，server 生命周期和测试绑定



# 失败自动截图(hook 钩子函数)：UI 用例失败时，把页面当时的样子截下来存盘
# hook 名字 pytest_runtest_makereport 是 pytest 写死的，不能改（pytest 靠名字到点自动调它）
# 每个用例的每个阶段结束，pytest 都会调一次本 hook。入参 (item, call) 顺序也是 pytest 规定，不能动：
#   item = 当前这个用例对象（身份：函数名、用了哪些 fixture）
#   call = 这次执行的结果（当次运行：哪一阶段、抛没抛异常）
# 所以 hook 里一个用例会被调 3 次：setup（前置）→ call（测试函数本体）→ teardown（清理），靠 call.when 区分
def pytest_runtest_makereport(item, call):
    # call.when 是本次的阶段："setup"前置 / "call"测试本体 / "teardown"清理
    # 只有 "call" 才算测试函数本体失败；setup 失败（fixture 炸）或 teardown 失败都不该截图
    if call.when == "call" and call.excinfo is not None:
        # call.excinfo = 异常信息容器。非空 = 这次抛了异常 = 失败（没抛就是 None）
        # 上面两个条件都满足 = 「测试函数本体」且「确实失败了」，才截图
        if "page" in item.funcargs:
            # item.funcargs = 这个用例实际用到的 fixture 字典，key 是 fixture 名
            # "page" in ... 先确认这用例确实用了 page（纯 API 用例没要 page，直接取会 KeyError 崩掉）
            page = item.funcargs["page"]   # funcargs["page"] ：取出那个 page 对象
            # page.screenshot() = Playwright 自带截图。item.name = 用例函数名，当文件名不重名
            png =page.screenshot()   # 不带 path → 返回字节，不写盘。之前是 page.screenshot(path=...) 存盘自己找文件；现在 attach 进报告，报告里直接看
            allure.attach(png, name =f"{item.name} 失败截图", attachment_type=allure.attachment_type.PNG)


