"""跑生成层：把每条问题真发给 AI，看它回答了什么，并存进 answers.json。

【它在整条链路里的位置】
    eval_set.csv（考卷）
        ↓  本文件把每道题读出来
    rag.retrieve()      → 选出资料段落
        ↓
    rag.ask_deepseek()  → 拼 prompt、发 AI
        ↓
    拿到回答 → 打印给人看 + 存成 answers.json 给判分脚本用

    本文件【只跑回答、不判分】—— 收卷子的活，改卷子是 judge.py 的事。

【跑法】
    cd ai_test_demo
    ../.venv/bin/python run_eval_gen.py

【注意】
    · 需要 DEEPSEEK_API_KEY
    · 每道题要真发一次 API 请求，9 条约 30~60 秒
    · 因为是 JSON 存盘，回答里的换行、逗号都能原样装下，不用转义
"""
import csv      # 读 CSV 文件（考卷）
import json     # 存回答：JSON 能原样装换行和逗号，比 CSV 省心
import rag      # 被测系统

chunks = rag.load_chunks(rag.KB_PATH)

results = []    # 收集所有回答，最后一次性存盘

for r in csv.DictReader(open("eval_set.csv", encoding="utf-8")):
    q = r["question"]

    hits = rag.retrieve(q, chunks)                  # 第一步：检索（纯本地，不花钱）
    context = "\n\n".join(hits)                     # 把选中的几段拼成一个字符串
    answer = rag.ask_deepseek(q, context)           # 第二步：生成（真发 API 请求，花钱）

    results.append({"id": r["id"], "question": q, "answer": answer})   # 存进列表，等最后一起写盘

    print("=" * 72)
    print("【id=%s｜%s】%s" % (r["id"], r["type"], q))
    print("  应召回　：", r["expected"] or "（无）")
    print("  实际召回：", "、".join(h.splitlines()[0].replace("## ", "") for h in hits))
    print("  要　点　：", r["要点"])                 # 判分依据之一
    print("  红　线　：", r["红线"])                 # 判分依据之二
    print("  ── AI 回答 ──")
    print("  " + answer.replace("\n", "\n  "))      # 把回答的每行都缩进 2 格，跟上面标题对齐
    print()

with open("answers.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)   # ensure_ascii=False：中文原样存，不转成 \uXXXX

print(f"已存 {len(results)} 条回答 → answers.json")
