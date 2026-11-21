"""跑评测集：只看【检索质量】（召回 / 精度），不依赖 API key。

【它在整条链路里的位置】
    比喻：eval_set.csv = 考卷，rag.py = 考生，本文件 = 监考 + 改卷 + 出成绩单。

    eval_set.csv（考卷）
        ↓  本文件逐题读出
    rag.retrieve()  → 拿回「实际召回了哪几段」
        ↓  跟考卷上写的「应该召回」比对
    打印一张表格 + 通过率

    覆盖范围到「检索」为止 —— AI 最后答得对不对，本文件不管（那是 run_eval_gen.py 的活）。

【跑法】
    cd ai_test_demo
    ../.venv/bin/python run_eval.py
"""
import csv      # 读 CSV 文件（考卷）
import rag      # 借用被测系统里的三样东西：KB_PATH（知识库路径）、load_chunks（切段）、retrieve（检索）

chunks = rag.load_chunks(rag.KB_PATH)    # 知识库切成段。只切一次，后面每道题都用这一份

rows, hit = [], 0        # rows：最后要打印的那张表，一行一道题；hit：通过了几道


# ── 逐题跑 ──────────────────────────────────────────────────
# csv.DictReader：把 CSV 的每一行变成一个「字典」，能按【列名】取值
#   循环第一圈时：r = {'id': '1', 'question': '退货运费谁出？', 'expected': '退货政策', ...}
for r in csv.DictReader(open("eval_set.csv", encoding="utf-8")):
    q, exp = r["question"], r["expected"]        # 这道题：问的是什么、应该召回哪一段

    # 让被测系统去检索，把结果整理成「段名」列表
    #   取每段第一行（就是 '## 退货政策'）→ 去掉 '## ' → 只留 '退货政策'
    got = []
    for c in rag.retrieve(q, chunks):
        first_line = c.splitlines()[0]
        clean_title = first_line.replace("## ", "")
        got.append(clean_title)
    # 例：got = ['退货政策', '换货政策']

    # 判这道题对错：
    #   有 expected（正常题）  → 看它有没有出现在实际召回里
    #   没 expected（无关题）  → 要求一段都没召回
    recall_ok = (exp in got) if exp else (len(got) == 0)

    # 挑出「多召回的」：实际召回里不是期望那一段的，就是混进来的（精度问题）
    extra = [g for g in got if g != exp] if exp else got

    # 记一行：id / 问题 / 应召回 / 实际召回 / 对错 / 多召回的
    rows.append((r["id"], q, exp or "（无）", "、".join(got),
                 "✅" if recall_ok else "❌", "、".join(extra) or "-"))
    hit += 1 if recall_ok else 0                 # 这题对了就加 1


# ── 打印成绩单 ──────────────────────────────────────────────
# %-3s 是「老式」字符串格式化：- 表示左对齐，3 表示占 3 个字符宽度 —— 纯粹为了让表格列对齐
print("\n%-3s %-16s %-12s %-20s %-5s %s" % ("id", "问题", "应召回", "实际召回", "召回", "多召回的(精度)"))
print("-" * 90)
for r in rows:
    print("%-3s %-16s %-12s %-20s %-5s %s" % r)     # 把上面存的 6 个值填进同一套格式
print("-" * 90)

print(f"召回通过率: {hit}/{len(rows)} = {hit/len(rows)*100:.0f}%")   # 通过率 = 通过数 ÷ 总数
