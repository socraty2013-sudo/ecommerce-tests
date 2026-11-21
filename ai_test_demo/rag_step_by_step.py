"""
把 rag.py 拆开，一步步打印中间结果 —— 看清「AI 到底在哪一步被调用」。

跑法：.venv/bin/python ai_test_demo/rag_step_by_step.py "退货运费谁出？"

先记住这条结论，下面每一步会验证它：
    真正「用 AI」的只有第 6 步；前面 1~5 步全是本地 Python，跟 AI 无关。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rag

question = sys.argv[1] if len(sys.argv) > 1 else "退货运费谁出？"

print("=" * 72)
print(f"用户问题：{question}")
print("=" * 72)

# ── 第 1 步：读知识库、切段 ──────────────────────────────
# 对应 rag.py 的 load_chunks()
print("\n【第 1 步】读知识库文件，按 '## ' 切成一段段")
chunks = rag.load_chunks(rag.KB_PATH)
print(f"  读的文件：{os.path.basename(rag.KB_PATH)}")
print(f"  切成了 {len(chunks)} 段：")
for i, c in enumerate(chunks, 1):
    print(f"    [{i}] {c.splitlines()[0]}    ({len(c)} 字)")
print("  ↑ 这一步只是读文件+切字符串，纯 Python")

# ── 第 2 步：给问题分词 ─────────────────────────────────
# 对应 rag.py 的 _tokens()
print("\n【第 2 步】把用户问题拆成一个个'词'（拿去做字面匹配）")
qt = rag._tokens(question)
print(f"  拆出 {len(qt)} 个词：{qt}")
print("  中文是按 2 个字一组滑窗切的 → '退货运费谁出' 变成 '退货/货运/运费/费谁/谁出'")
print("  ↑ 还是纯 Python，没碰 AI")

# ── 第 3 步：给每段打分 ─────────────────────────────────
# 对应 rag.py 的 retrieve() 前半段
print("\n【第 3 步】拿问题的每个词，去每段里数出现次数，累加成总分")
scores = []
for i, c in enumerate(chunks, 1):
    s = sum(rag._tokens(c).count(t) for t in qt)
    scores.append((s, i, c))
    print(f"    第{i}段 {c.splitlines()[0]:<12} → {s} 分")
print("  ↑ 就是数字符串，纯 Python")

# ── 第 4 步：排序取前 2 段 ──────────────────────────────
# 对应 retrieve() 后半段
print("\n【第 4 步】按分数排序，取前 2 段（top_k=2）")
ranked = sorted(scores, key=lambda x: x[0], reverse=True)
hits = [c for s, i, c in ranked[:2]]
print(f"  选中的 2 段：")
for s, i, c in ranked[:2]:
    print(f"    → 第{i}段（{s} 分）：{c.splitlines()[0]}")
    for line in c.splitlines()[1:]:
        print(f"         {line}")
print("  ↑ 还是纯 Python。注意：就算全是 0 分也会硬选前 2 段（没有阈值）")

# ── 第 5 步：拼出要发给 AI 的文本 ★★★ ─────────────────
# 对应 rag.py 的 ask_deepseek() 里 prompt = (...) 那一段
print("\n【第 5 步】★★★ 把资料和问题拼成一整段文本 —— 这才是 AI 真正看到的")
context = "\n\n".join(hits)
prompt = (
    "你是电商客服。只依据下面【资料】回答用户问题；"
    "资料里没有的，直接回复“这个问题我需要帮你转人工处理”，不要编造。\n\n"
    f"【资料】\n{context}\n\n【用户问题】{question}"
)
print("  ┌" + "─" * 68)
for line in prompt.splitlines():
    print("  │ " + line)
print("  └" + "─" * 68)
print(f"  这一整段（{len(prompt)} 字）就是发给 AI 的全部内容")
print("  ↑ 到这一步为止，还是纯 Python 在拼字符串")

# ── 第 6 步：发请求给 DeepSeek ← 唯一用到 AI 的地方 ────
print("\n【第 6 步】把上面那段文本 POST 给 DeepSeek  ← 唯一用到 AI 的一步")
print(f"  接口：{rag.API_URL}")
print(f"  模型：{rag.MODEL}")
print("  请求体长这样（prompt 塞在 messages[0].content 里）：")
print("    {")
print(f'      "model": "{rag.MODEL}",')
print('      "messages": [{"role": "user", "content": "← 就是上面第 5 步那一整段"}]')
print("    }")
answer = rag.ask_deepseek(question, context)

# ── 第 7 步：拿到回答 ───────────────────────────────────
print("\n【第 7 步】AI 返回的回答：")
print("  " + answer)
print("\n" + "=" * 72)
print("整条链路：读文件 → 切段 → 分词 → 打分 → 排序 → 拼文本 → 【调AI】 → 返回")
print("AI 只出现在倒数第二步。前面全是你的测试脚本能看见、能改的普通代码。")
print("=" * 72)
