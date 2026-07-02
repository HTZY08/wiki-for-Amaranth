#!/usr/bin/env python3
"""Cluster experience notes system.
 
Each cluster accumulates wisdom over time.
Cron updates this automatically; the agent reads it at conversation start.
"""
import json, os, re, sys
from collections import defaultdict, Counter

BASE = "./data"
NOTES_FILE = os.path.join(BASE, "cluster-experience.json")
HISTORY = os.path.join(BASE, "session-history.jsonl")
CLUSTERS = os.path.join(BASE, "session-clusters.json")

KEYWORD_CLUSTERS = {
    "工程": [18], "代码": [18], "编码": [18], "配置": [18],
    "yaml": [18], "docker": [18], "部署": [18], "git": [18],
    "查询": [10, 19], "搜索": [10, 19], "找": [10, 19],
    "推荐": [19], "攻略": [19], "价格": [19],
    "模型": [1], "api": [1, 8], "token": [1], "provider": [1],
    "架构": [8], "设计": [8], "脑暴": [8],
    "skill": [8], "收集": [8], "链接": [8],
    "primrose": [1], "gateway": [1],
    "kanban": [18], "调度": [18],
    "论文": [10], "文献": [10], "综述": [10],
    "爬": [10], "抓取": [10], "采集": [10],
    "ppt": [19], "求职": [19],
}

def extract_keywords(text: str) -> list[str]:
    text = text.lower()
    found = []
    for kw in sorted(KEYWORD_CLUSTERS.keys(), key=len, reverse=True):
        if kw in text:
            found.append(kw)
    return found[:5]

def predict_clusters(keywords: list[str]) -> list[int]:
    scores = Counter()
    for kw in keywords:
        for cid in KEYWORD_CLUSTERS.get(kw, []):
            scores[cid] += 1
    return [c for c, _ in scores.most_common(3)]

def build_experience_notes():
    if not os.path.exists(CLUSTERS):
        return {}
    with open(CLUSTERS) as f:
        clusters = json.load(f)
    with open(HISTORY) as f:
        sessions = [json.loads(l) for l in f if l.strip()]
    by_cluster = defaultdict(list)
    for i, s in enumerate(sessions):
        key = str(i)
        if key in clusters:
            cid = clusters[key]["cluster"]
            by_cluster[cid].append(s["text"])
    notes = {}
    for cid, sess_list in by_cluster.items():
        all_text = " ".join(sess_list).lower()
        keywords_found = Counter()
        for kw in KEYWORD_CLUSTERS:
            keywords_found[kw] = all_text.count(kw)
        top_kws = [kw for kw, _ in keywords_found.most_common(5) if kw]
        cluster_wisdom = {
            18: [
                "[动手] pip 装包用 uv + 清华镜像，不走代理",
                "[动手] Docker 容器无 systemd，用 s6-overlay 管理进程",
                "[动手] Profile 的 SOUL.md 用 5 段结构",
                "[卡住] config.yaml 用 key_env 而非 api_key_env — 否则静默 401",
                "[解决] git clone 加 --depth 1 避免大仓库超时",
            ],
            10: [
                "[动手] 中文查询优先用 web_extract 读内容，不用 web_search 搜标题",
                "[卡住] 知乎内容结构化差 — API 只返回 3 条评论",
                "[解决] 文献 DOI 在 crossref.org 解析元数据",
            ],
            8: [
                "[解决] 多 Agent 协作用枝叶通道文件 IPC，不建中心调度",
                "[解决] Skill 写好后冻结不动提高前缀缓存命中率",
                "[动手] 共振引擎三平面：SOUL/MEMORY/SKILL",
            ],
            1: [
                "[卡住] DeepSeek thinking mode 需回传 reasoning_content — 否则 400",
                "[卡住] Gemini 用 Google 原生 /v1beta，OpenAI 兼容会 500",
                "[卡住] 小米 MiMo: tp- 前缀用 token-plan.cn 端点，sk- 用 api 端点",
            ],
            19: [
                "[动手] 知乎搜就业口碑用 developer.zhihu.com API",
                "[动手] 高考数据走 MiniMax coding_plan 并发搜索",
            ],
        }
        notes[str(cid)] = {
            "cluster": cid,
            "sessions": len(sess_list),
            "top_keywords": top_kws,
            "experience": cluster_wisdom.get(cid, []),
            "last_session": sess_list[-1][:80] if sess_list else ""
        }
    return notes

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    
    if cmd == "predict":
        query = " ".join(sys.argv[2:])
        kws = extract_keywords(query)
        cls = predict_clusters(kws)
        if cls:
            notes = build_experience_notes()
            cid = cls[0]
            info = notes.get(str(cid), {})
            print(f"C{cid}")
            for exp in info.get("experience", []):
                print(exp)
        else:
            print("C?")
            print("无匹配经验")
    
    elif cmd == "log":
        kw = " ".join(sys.argv[2:])
        entry = {"text": kw[:200], "ts": __import__('datetime').datetime.now().isoformat()}
        with open(HISTORY, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"→ Logged: {kw[:50]}")
    
    else:  # build
        notes = build_experience_notes()
        with open(NOTES_FILE, "w") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
        print(f"✅ Cluster experience notes saved ({len(notes)} clusters)")
        for cid_str, info in sorted(notes.items(), key=lambda x: -x[1]["sessions"]):
            if info["experience"]:
                print(f"  C{cid_str} ({info['sessions']} ses): " + info["experience"][0][:50])
