#!/usr/bin/env python3
"""
Live session logger — appends current conversation to live.jsonl in real-time.
Each assistant response writes: user message + response summary.
When session ends, merge into session-history.jsonl and clear live.
"""
import json, os, time

LIVE_FILE = "./data/live.jsonl"
HISTORY_FILE = "./data/session-history.jsonl"
LOCK_FILE = "./data/.live.lock"

def log_turn(user_msg: str, my_response_summary: str, source: str = "weixin"):
    """Append a conversational turn to the live file."""
    os.makedirs(os.path.dirname(LIVE_FILE), exist_ok=True)
    ts = time.strftime("%Y-%m-%d %H:%M")
    
    entries = [
        {"ts": ts, "type": "user", "source": source, "text": user_msg[:200]},
        {"ts": ts, "type": "assistant", "source": source, "text": my_response_summary[:200]},
    ]
    
    with open(LIVE_FILE, "a") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

def finalize():
    """Merge live.jsonl into session-history.jsonl, rebuild clusters, clear live."""
    if not os.path.exists(LIVE_FILE) or os.path.getsize(LIVE_FILE) == 0:
        return
    
    with open(LIVE_FILE) as f:
        live_lines = [l.strip() for l in f if l.strip()]
    
    if not live_lines:
        return
    
    user_msgs = sum(1 for l in live_lines if '"user"' in l)
    first = json.loads(live_lines[0])
    last = json.loads(live_lines[-1])
    
    source = first.get("source", "unknown")
    title = first.get("text", "live session")[:60]
    summary = {
        "ts": first["ts"],
        "text": f"[{first['ts']}] {source}: {title} ({user_msgs} msgs)",
        "source": source,
        "msgs": user_msgs,
    }
    
    # Append to history
    with open(HISTORY_FILE, "a") as f:
        f.write(json.dumps(summary, ensure_ascii=False) + "\n")
    
    # Clear live file
    os.remove(LIVE_FILE)
    
    # Trigger immediate rebuild (local computation, no API cost)
    import subprocess
    build_chain = [
        "python3 ./data/cluster-experience.py build",
        "python3 ./data/inject-experience.py",
        "python3 ./data/error-collector.py scan",
    ]
    for cmd in build_chain:
        try:
            subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
        except:
            pass
    
    print(f"✅ 会话已归档 ({user_msgs} 条) + 经验笔记已重建")

def live_count():
    """Count live entries."""
    if not os.path.exists(LIVE_FILE):
        return 0
    with open(LIVE_FILE) as f:
        return len([l for l in f if l.strip()])

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "finalize":
        finalize()
    elif len(sys.argv) > 1 and sys.argv[1] == "count":
        print(live_count())
    elif len(sys.argv) > 1 and sys.argv[1] == "log" and len(sys.argv) >= 4:
        log_turn(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "weixin")
        print("ok")
    else:
        print("Usage: live-logger.py [finalize|count|log <user_msg> <summary> [source]]")
