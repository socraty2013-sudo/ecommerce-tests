"""第二层判分：让 AI 当裁判，判断客服答复的语义对不对、全不全。

【为什么要这一层】
    第一层（judge.py）只查词在不在，读不懂意思 —— 会误杀：
    比如「不能多次修改」里有"多次"，被当成破红线。

【它在链路里的位置】
    answers.json（客服 AI 的答复）
        ↓
    eval_set.csv（题目 + 要点 + 红线）
        ↓  本文件把它们拼成一段话
    DeepSeek（当裁判）→ 通过 / 不通过 + 理由
        ↓
    judge_ai_results.json

【跑法】
    cd ai_test_demo
    ../.venv/bin/python judge_ai.py

【注意】
    · 每题真发一次 API，11 题约 1~2 分钟
    · 复用 rag.py 的 .env 加载和接口配置，key 还是 DEEPSEEK_API_KEY
"""
import csv       # 读考卷
import json      # 读答复、存结果
import os        # 读 API key
import requests  # 发 HTTP 请求

import rag       # 复用它的：.env 加载、接口地址、模型名

rag._load_env()  # 先把 .env 里的 key 读进环境变量

# ── 裁判的指令 ─────────────────────────────────────────────
# 这段就是判分口径 —— 想让裁判按别的标准判，改这里
PROMPT = """你是裁判。下面是一道客服题、判分标准、以及客服的答复。
请判断这条答复的语义是否正确且周全。

【题目】{question}
【要点】必须说到：{must}
【红线】绝对不能出现：{forbid}
【客服答复】{answer}

严格按这个格式回复：
第一行只写「通过」或「不通过」
第二行起写理由"""


def ask_judge(prompt):
    """把 prompt 发给 DeepSeek，拿回裁判的判词。"""
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise SystemExit("请先设置环境变量 DEEPSEEK_API_KEY")

    r = requests.post(
        rag.API_URL,
        headers={
            "Authorization": f"Bearer {key}",     # 身份凭证
            "Content-Type": "application/json",
        },
        json={
            "model": rag.MODEL,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    r.raise_for_status()                          # 状态码不是 2xx 就报错
    return r.json()["choices"][0]["message"]["content"]


answers = json.load(open("answers.json", encoding="utf-8"))             # 客服 AI 的答复
standards = {r["id"]: r for r in
             csv.DictReader(open("eval_set.csv", encoding="utf-8"))}    # 题目 + 判分标准，按 id 索引

results = []     # 收集结果，最后一起存盘
passed = 0

for a in answers:
    tid = a["id"]
    std = standards.get(tid)
    if std is None:                            # 考卷里没这道题 → 跳过
        continue

    prompt = PROMPT.format(
        question=std["question"],
        must=std["要点"],
        forbid=std["红线"],
        answer=a["answer"],
    )
    reply = ask_judge(prompt).strip()

    first = reply.splitlines()[0] if reply else ""        # 第一行是结论
    verdict = "不通过" if "不通过" in first else "通过"    # 先判"不通过"：否则「不通过」里的"通过"会被误认成通过
    if verdict == "通过":
        passed += 1
    reason = "\n".join(reply.splitlines()[1:]).strip() or reply   # 第一行之后的都是理由

    results.append({"id": tid, "question": std["question"],
                    "answer": a["answer"], "verdict": verdict, "reason": reason})

    print("=" * 72)
    print("【id=%s】%s" % (tid, std["question"]))
    print("  客服答复：", a["answer"])
    print("  裁判判定：", "✅ 通过" if verdict == "通过" else "❌ 不通过")
    print("  理　由　：", reason.replace("\n", "\n            "))   # 理由多行时缩进对齐

with open("judge_ai_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)   # ensure_ascii=False：中文原样存

print("=" * 72)
print(f"AI 裁判通过率：{passed}/{len(results)} = {passed/len(results)*100:.0f}%")
print("结果已存 → judge_ai_results.json")
