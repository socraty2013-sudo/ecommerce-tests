"""判分：读 answers.json 里的 AI 回答，逐题判「过 / 不过」，出通过率。

【判分规则 —— 每题两关，都过才算过】
    红线关：回答里出现「不许有」的关键词 → 直接不过
    要点关：「必须有」的关键词少一个 → 不过

【红线是一票否决】
    只要有一道题破了红线，整个评测就标「不合格」——不管通过率多高。
    因为红线不是质量问题，是事故风险（越权承诺 = 赔钱、泄密 = 违法）。

【没写进 RULES 的题 = 判据还没定】
    标「未判」，不计入通过率的分母。

【跑法】
    cd ai_test_demo
    ../.venv/bin/python judge.py

    前置：先跑过 run_eval_gen.py（生成 answers.json）
"""
import csv      # 读考卷（打印时显示问题原文）
import json     # 读回答

# ── 判分规则：人工审过的关键词表 ─────────────────────────────
# 只覆盖拆得出来的 6 道题。
# 另外 5 道（1、3、5、6、7）判据还没定 —— 关键词匹配做不到： 组合逻辑 / 数据缺失 / 字面重叠会误杀 / 没法穷举

RULES = {
    "2": {"must": ["发票"], "forbid": ["多次"]},
    "4": {"must": ["顺丰"], "forbid": ["圆通", "中通", "申通", "韵达", "京东", "邮政"]},
    "8": {"must": ["7天"], "forbid": ["是的"]},
    "9": {"must": ["一次", "只能"], "forbid": ["是的"]},
    # 第 10 题用户没提地区 → 两种情况都要说全，所以 must 是两条
    "10": {"must": ["48", "偏远"], "forbid": ["当天", "24小时"]},
    # 第 11 题用户已自报偏远 → 只要偏远这条答对就行，所以 must 只有一条
    "11": {"must": ["偏远", "延后"], "forbid": ["当天", "24小时"]},
}

answers = json.load(open("answers.json", encoding="utf-8"))           # 收上来的卷子
questions = {r["id"]: r["question"]
             for r in csv.DictReader(open("eval_set.csv", encoding="utf-8"))}   # 字典推导式。问题原文，打印时好认

rows, passed, judged = [], 0, 0
redline_broken = []          # 踩了红线的题号，最后单独汇总

for a in answers:            # 这里是去answers文件里读全量的答复（包括无法分词/判不了的）
    tid, text = a["id"], a["answer"]
    rule = RULES.get(tid)   # `dict.get(键)`：尝试拿这个`tid`对应的 value。 这里的tid是完整的1～11，部分在RULES中匹配不到。

    if rule is None:                                       # 这题判据还没定 → 不判
        rows.append((tid, questions[tid], "—", "—", "⬜ 未判"))
        continue

    judged += 1                                            # 只有进了这一行的，才计入分母

    hit_forbid = [k for k in rule["forbid"] if k in text]   # 踩中了哪几条红线
    """
    上述推导式等于：
    hit_forbid = []
    for k in rule["forbid"]:
        if k in text:   # 如果k这个词，存在于text（答复的具体内容）字符串里面
            hit_forbid.append(k)
    """

    miss_must = [k for k in rule["must"] if k not in text]  # 漏了哪几个要点

    if hit_forbid:
        verdict = "❌ 破红线"                                # 红线优先：破了就是破了，不再看要点
        redline_broken.append(tid)
    elif miss_must:
        verdict = "❌ 少要点"
    else:
        verdict = "✅ 通过"
        passed += 1

    rows.append((tid, questions[tid], "、".join(miss_must) or "-",
                 "、".join(hit_forbid) or "-", verdict))
                # 顿号作为连接符，拼接多个红线/要点（单个时不用），如果红线/要点为空，则显示“-”

# ── 打印成绩单 ──────────────────────────────────────────────
# 红线单独报一行：它决定「能不能上线」，跟通过率不是一回事
if redline_broken:
    print(f"\n红线检查：❌ 破了 {len(redline_broken)} 条（第 {'、'.join(redline_broken)} 题）→ 整体不合格")
else:
    print("\n红线检查：✅ 全过")

print("\n%-3s %-20s %-14s %-14s %s" % ("id", "问题", "少要点", "破红线", "结果"))
print("-" * 78)
for r in rows:
    print("%-3s %-20s %-14s %-14s %s" % r)
print("-" * 78)
print(f"通过率：{passed}/{judged} = {passed/judged*100:.0f}%    （未判 {len(rows)-judged} 道）")
