"""
用「代码」驱动 AI-claude，不是用嘴 —— 需求解析脚本

跟聊天框手打的区别：
    聊天框：一次一个需求、手打、结果在屏幕上、关掉就没了
    脚本：  读文件 → 调 API → 结果落成文件，可批量、可进 CI、可接进 pytest

要真跑，先设 key：
    export DEEPSEEK_API_KEY=sk-xxx
    .venv/bin/python ai_demo/gen_use_cases.py 需求.txt
"""
import os
import sys
import json
import requests

API_URL = "https://api.deepseek.com/chat/completions"

# —— 这就是「挖洞」那段 prompt，只不过它现在住在代码里，不在聊天框里 ——
PROMPT_TMPL = """你是资深测试工程师，擅长需求评审。
下面这段需求可能写得很糙、很多地方没说清。先不要写用例，只做需求解析。

需求原文：
{req}

请输出两份清单：
① 可测点清单（方向级，不展开成用例）
② 待确认问题清单（需求没说清、要问产品/开发的点）
凡不确定、需求又没写明的，全部列出来问；不许自己假设，也不要在清单里给答案。
"""


def analyze(req: str) -> str:
    """把需求交给模型，拿回解析结果"""
    r = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {os.environ['DEEPSEEK_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": PROMPT_TMPL.format(req=req)}],
        },
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def main():
    if len(sys.argv) < 2:
        print("用法：python gen_use_cases.py 需求.txt")
        sys.exit(1)

    req_path = sys.argv[1]
    with open(req_path, encoding="utf-8") as f:
        req = f.read()

    result = analyze(req)

    out_path = req_path.replace(".txt", "") + "-需求解析.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"已写入：{out_path}")
    print(result)


if __name__ == "__main__":
    main()
