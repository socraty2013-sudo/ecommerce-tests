#!/bin/bash
# ⬆️告诉操作系统「用 /bin/bash 这个程序来解释执行这个文件」
# #! 两个字符连在一起叫 shebang，读作「史邦」或「谁帮」。

PROJECT_DIR="/Users/yaben/PycharmProjects/ecommerce-tests"
APP_PORT="5001"

REPORT_DIR="${PROJECT_DIR}/reports"
mkdir -p "${REPORT_DIR}"

echo "========================================"
echo "电商项目自动化测试开始"
echo "项目目录: ${PROJECT_DIR}"
echo "========================================"

set -e          # 放在变量定义之后、命令开始之前。任何一条命令失败（退出码非 0），脚本立刻终止，不再执行后面的命令。

trap 'kill ${APP_PID} 2>/dev/null' EXIT    # 捕获任何方式的退出（正常跑完、set -e 报错退出、手动 exit、Ctrl+C）,退出前强制执行的清理命令

START_TIME=$(date +"%Y-%m-%d %H:%M:%S")   # date 支持一个 【+】参数，让你自己指定输出格式。+ 后面跟的 %Y %m %d... 是格式占位符
echo "开始时间：${START_TIME}"

# 判断依赖是否存在，后安装依赖
if [ ! -f "${PROJECT_DIR}/requirements.txt" ];then
  echo "❌ requirements.txt 不存在，无法安装依赖"
  exit 1
fi
echo "requirements.txt 存在，继续"  # 这里不写在 else 里，是因为：加 else 是把「失败分支」和「成功分支」并列；不加 else 是「失败立即退出 + 成功自然流入主线」。CI 脚本偏向后一种，因为一旦前置条件不满足，后面再跑都是浪费，且 exit 1 让 CI 直接变红。

pip install -r "${PROJECT_DIR}/requirements.txt" > "${REPORT_DIR}/pip_install.log" 2>&1
echo "✅ 依赖安装完成"


# 输出环境变量（写死）
# export TEST_ENV="test"

# 根据传入参数下选择环境
ENV="${1:-test}"     # 如果没传参数，默认环境为 test；1读的是位置参数 $1，传了则用 $1 的值
export TEST_ENV="${ENV}"
echo "当前环境为：${ENV}"

# 根据上面的环境匹配端口号，并在没匹配的环境时，进行兜底
case "${ENV}" in          # ① 开头：case + 要判断的值 + in
    test)                 # ② 分支1：test)
        APP_PORT=5001     #    分支体
        ;;                # ③ 分号结尾：;;
    prod)                 # ④ 分支2
        APP_PORT=5002
        ;;
    *)                    # ⑤ 兜底分支
        echo "❌ 未知环境：${ENV}"
        exit 1
        ;;
esac                      # ⑥ 结尾：esac = case 倒过来写


# 后台启动 Flask
start_flask(){
  echo "启动 Flask 服务（后台）..."
  cd "${PROJECT_DIR}"   # 因脚本可能在别的目录运行，所以要 cd 到项目目录，Python 才能找到 app 模块。
  python -c "from app import app; app.run(host='127.0.0.1', port=${APP_PORT})" &    # & ：把这个命令丢到后台让它继续执行，立刻返回，终端继续执行下一行。
  APP_PID=$!        # $! = 上一个后台进程的 PID
  echo "Flask 已后台启动，PID=${APP_PID}"
}

start_flask    # 执行整个函数体



# 等待 Flask 就绪（最多 15 秒）
READY=0      # 先默认：没就绪
for i in $(seq 1 15); do
    if curl -s http://localhost:${APP_PORT}/ > /dev/null 2>&1; then
        echo "✅ Flask 第 ${i} 秒就绪"
        READY=1  # 一旦成功，翻成 1。拿着 READY去判断是否就绪
        break
    fi
    echo "第 ${i} 秒，Flask 还没起来..."
    sleep 1
done


# 检查是否就绪
if [ "${READY}" -eq 0 ]; then     # 因 READY是一个变量，已经存起来了，所以无需“紧挨着”
    echo "❌ Flask 未在 15 秒内启动，退出"
    exit 1
fi


# 跑测试，输出存到日志
pytest tests/ -v \
    --ignore-glob=tests/test_ui_*.py \
    --alluredir="${REPORT_DIR}/allure-results" \
    > "${REPORT_DIR}/test_output.log" 2>&1

echo "===== 测试结果 ====="
# grep "passed\|failed\|error" "${REPORT_DIR}/test_output.log" | tail -3    # 老式：一次搜三个词：用 \|（在双引号里 = 「或」。）把它们连起来，命中任意一个或多个都选中
grep -E "passed|failed|error" "${REPORT_DIR}/test_output.log" | tail -3     # 新式：加 -E，竖杠不用转义

# 清理：停 Flask
echo "停止 Flask 服务..."
kill ${APP_PID} && echo "✅ Flask 已停止" || echo "⚠️ Flask 可能已提前退出"