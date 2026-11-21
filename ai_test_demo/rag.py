"""
极简 RAG（练手用）：关键词检索 + DeepSeek 生成。

一次问答走 7 步：
    读知识库 → 切段 → 问题分词 → 给每段打分 → 取前2段 → 拼 prompt → 调 DeepSeek
    load_chunks()       _tokens()      retrieve()                ask_deepseek()

关键：只有最后「调 DeepSeek」那一步用到 AI，前面 6 步全是本地 Python 在数数。

本文件 = 「被测系统」，测试代码不要跟它混在一起。
单独跑：.venv/bin/python ai_test_demo/rag.py "退货运费谁出？"
"""
import os        # 读环境变量（API key）、拼文件路径
import re        # 正则：切段用一次、分词用两次
import sys       # 读命令行参数（__main__ 里用）
import requests  # 发 HTTP 请求 —— 「调用 AI」靠的就是它


def _load_env():
    """把 .env 文件里的 key 读进环境变量（Python 不会自动读 .env）。

    优先级：外部环境变量 > .env，所以用 setdefault 而不是直接赋值。
    """
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")   # 用 __file__ 定位 → 绝对路径，从哪儿跑都找得到
    if not os.path.exists(env_path):
        return                        # .env 只是兜底来源：真实部署（CI/Docker）通常直接设系统环境变量，压根没这文件
    for line in open(env_path, encoding="utf-8"):      # 文件对象可以直接 for，一次吐一行
        line = line.strip()                            # 去掉首尾空白和那个换行符（同名接住 = 覆盖旧值）
        if not line or line.startswith("#") or "=" not in line:
            continue                                   # 空行 / 注释行 / 没有等号 → 这行跳过
        k, v = line.split("=", 1)                      # 最多切 1 刀，值里带等号也切不坏
        os.environ.setdefault(k.strip(), v.strip())    # setdefault：没设过才设，不覆盖外部传进来的


_load_env()   # 先加载 key，下面才读得到


# ── 三个配置项 ─────────────────────────────────────────────────
KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.md")   # 知识库文件在哪
API_URL = "https://api.deepseek.com/chat/completions"                    # DeepSeek 接口地址
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")                # 用哪个模型（可用环境变量覆盖）


def load_chunks(path):
    """【第 1 步】读知识库，按 '## ' 切成一段段。

    返回 ['## 退货政策\\n- ...', '## 换货政策\\n- ...', ...] —— 一个小节 = 一个元素。
    """
    text = open(path, encoding="utf-8").read()      # 整个文件读成一个长字符串
    parts = re.split(r"\n(?=## )", text)            # 在「换行 + ## 」的位置切开；(?=) 是前瞻，只定位不吃掉 —— 不加它井号会被切走，小标题就丢了
    return [p.strip() for p in parts                # 列表推导式 = for 循环 + append 压成一行
            if p.strip().startswith("## ")]         # 只要 '## ' 开头的；文件顶端那行大标题（# ...）不满足，正好被扔掉


def _tokens(s):
    """【第 2 步】把一句话拆成词，用来做字面匹配。

    '退货运费谁出？' → ['退货', '货运', '运费', '费谁', '谁出']
    死穴：中文没空格，只能 2 个字一组滑窗切 → 「快递」和「物流」这种同义词互相抓不到。
    """
    s = s.lower()                                   # 统一小写，避免大小写不同被当成两个词
    toks = re.findall(r"[a-z0-9]+", s)              # 英文/数字：连续的一段算一个词
    zh = re.findall(r"[一-鿿]", s)                   # 只捞汉字；没加 + ，所以一次只捞一个字
    toks += [zh[i] + zh[i + 1] for i in range(len(zh) - 1)]   # 相邻两字拼成 2 字词；用 len-1 是因为最后一个字后面没字可配，写 len 会越界
    return toks


def retrieve(question, chunks, top_k=2):
    """【第 3、4 步】检索：给每段打分，返回分最高的 top_k 段。

    输入：问题、所有段落、取几段（默认 2）。输出：选中的段落列表。
    注意：分数是中间值，算完就扔，外部拿不到。
    """
    q = _tokens(question)                           # 问题也拆成词 —— 两边得是同一种东西才能比
    scored = []
    for c in chunks:
        ct = _tokens(c)                             # 这一段也拆成词
        score = sum(ct.count(t) for t in q)         # 分数 = 问题的每个词在这段里出现了几次，加起来
        scored.append((score, c))                   # 打包成元组 (分数, 段落) —— 分数放前面，下一步好排序
    scored.sort(key=lambda x: x[0], reverse=True)   # 按分数从高到低；key 里那个 lambda 就是告诉 sort：拿元组的第 0 个来比
    return [c for s, c in scored[:top_k]]           # 拆包，只要段落不要分数；⚠️ 没有相关性阈值 —— 全是 0 分时也硬取前 2 段


def ask_deepseek(question, context):
    """【第 5、6、7 步】拼 prompt → 调 DeepSeek → 拿回答。

    输入：用户问题 + 上一步选中段落拼成的一整段文本。输出：模型返回的回答字符串。
    """
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise SystemExit("请先设置环境变量 DEEPSEEK_API_KEY")

    # 【第 5 步】拼接：把「指令 + 资料 + 问题」拼成一整段文本 —— 这就是 AI 能看到的全部内容
    prompt = (
        "你是电商客服。只依据下面【资料】回答用户问题；"
        "资料里没有的，直接回复“这个问题我需要帮你转人工处理”，不要编造。\n\n"
        f"【资料】\n{context}\n\n【用户问题】{question}"
    )

    # 【第 6 步】调用：一次普通 HTTP POST ★整个文件唯一用到 AI 的地方
    r = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {key}",        # 身份凭证：告诉服务器我是谁
            "Content-Type": "application/json",      # 声明请求体是 JSON 格式
        },
        json={
            "model": MODEL,                          # 用哪个模型
            "messages": [{"role": "user", "content": prompt}],   # 消息内容就是上面拼的那段
        },
        timeout=60,                                  # 最多等 60 秒
    )
    r.raise_for_status()                             # 状态码不是 2xx 就报错，免得拿着空数据继续往下跑

    # 【第 7 步】取回答：从返回的 JSON 里一层层往里掏，连起来就是 choices[0].message.content
    return r.json()["choices"][0]["message"]["content"]


if __name__ == "__main__":
    chunks = load_chunks(KB_PATH)                                        # ① 切段
    question = sys.argv[1] if len(sys.argv) > 1 else "退货的运费谁出？"    # ② 命令行拿问题，没给就用默认
    hits = retrieve(question, chunks)                                    # ③④ 检索

    print("【用户问题】", question)
    print("【检索到的段落】（这就是要看的东西）")
    for h in hits:
        print("   -", h.splitlines()[0])                                 # 只打印每段的小标题
    print("【客服回答】")
    print(ask_deepseek(question, "\n\n".join(hits)))                     # ⑤⑥⑦ 拼接 + 调用 + 打印
