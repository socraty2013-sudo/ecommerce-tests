# Dockerfile = 一份"机器可执行的安装文档"，执行 docker build -t myapp . 把参与打包的文件做成镜像
# 有 compose 时不用该命令，直接使用 docker compose up -d


# 设置基础镜像：基于 Python 3.13 精简版镜像。选该镜像是因为在本地跑，浏览器也在本地。
#             如果用playwright/python 这类镜像，则镜像中包含了浏览器，适合在 docker 环境中跑。
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 把 requirements.txt的内容拷贝进容器
# 从本地拷贝到容器当前目录，注意：点号（.）指当前目录(即前面设置的工作目录/app)
COPY requirements.txt .

# 承接上一步，安装 requirements.txt 中的依赖，考虑到网络问题，这里使用清华源。
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 把整个项目拷贝到容器
# 当前目录（项目根目录）所有内容 → 容器内 /app（因为 WORKDIR 设过了）
# 这一步会把.dockerignore的内容自动忽略，不拷贝
COPY . .

# EXPOSE 只是声明，不是动作。声明容器监听哪个端口，告诉读 Dockerfile 的人/工具："这个容器监听 5000 端口"
EXPOSE 5000

# CMD 是容器启动时执行的命令，将 flask 启动起来，且后台常驻
# --host=0.0.0.0 必须加，不然外部访问不到
# 括号内的命令词写法：Docker 分两种 CMD 写法——exec 形式（列表）和 shell 形式（字符串：python -m flask run --host=0.0.0.0），当前写法更符合官方，信号传递更干净
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]

# 这里不能写 pytest相关指令，原因：Docker 设计原则 —— 一个容器一个职责，好管理、好调试。CMD 只定义一条命令，所以 Flask 和 pytest 要分开。