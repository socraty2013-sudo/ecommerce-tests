import threading,time

def 打工():
    for i in range(3):
        time.sleep(1)
        print(f"子线程：打工第{i+1}秒")

print("主线程：开工")
t = threading.Thread(target=打工)   # 登记子线程，活=打工
t.start()
print("主线程：我不等他，继续干我的")


# 直接执行当前文件，查看终端输出顺序


import contextvars
v = contextvars.ContextVar("x")
t = v.set(10)        # 放 10 进去
print(t)             # 打印的是 <Token ...>，不是 10
print(v.get())       # 想拿 10，得单独 get()