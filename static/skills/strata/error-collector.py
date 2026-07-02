#!/usr/bin/env python3
"""
Error Collector — record tool failures per cluster.
Errors hang off the same cluster as the successful operation they relate to.
"""
import json, os, sys
from datetime import datetime

BASE = "./data/errors"
INDEX_FILE = os.path.join(BASE, "INDEX.json")

def log_error(cluster: int, tool: str, action: str, error_type: str, 
              error_msg: str, solution: str = "", phase: str = ""):
    """Record a tool failure, linked to its success cluster."""
    os.makedirs(BASE, exist_ok=True)
    
    entry = {
        "ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "cluster": cluster,
        "tool": tool,
        "action": action,
        "error_type": error_type,
        "error_msg": error_msg[:300],
        "solution": solution[:300],
        "phase": phase,
    }
    
    # Write to cluster file
    cfile = os.path.join(BASE, f"C{cluster}.json")
    if os.path.exists(cfile):
        with open(cfile) as f:
            data = json.load(f)
    else:
        data = {"cluster": cluster, "errors": []}
    
    data["errors"].append(entry)
    with open(cfile, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Update index
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE) as f:
            idx = json.load(f)
    else:
        idx = {"version": 1, "created": datetime.now().strftime("%Y-%m-%d"), 
               "total_errors": 0, "clusters": {}}
    
    idx["total_errors"] += 1
    idx["clusters"].setdefault(str(cluster), {"count": 0})
    idx["clusters"][str(cluster)]["count"] += 1
    idx["clusters"][str(cluster)]["last"] = entry["ts"]
    
    with open(INDEX_FILE, "w") as f:
        json.dump(idx, f, indent=2, ensure_ascii=False)
    
    return entry


def check_errors(cluster: int) -> list:
    """Look up known errors for a cluster. Returns list of error entries."""
    cfile = os.path.join(BASE, f"C{cluster}.json")
    if not os.path.exists(cfile):
        return []
    with open(cfile) as f:
        data = json.load(f)
    return data.get("errors", [])


def scan_cron_logs():
    """Bootstrap: scan cron logs for historical errors."""
    log_dir = "./cron-logs"
    count = 0
    if not os.path.exists(log_dir):
        return count
    
    for job_dir in os.listdir(log_dir):
        job_path = os.path.join(log_dir, job_dir)
        if not os.path.isdir(job_path):
            continue
        for log_file in os.listdir(job_path):
            if log_file.endswith(".md") or log_file.endswith(".txt"):
                log_path = os.path.join(job_path, log_file)
                try:
                    with open(log_path) as f:
                        content = f.read()
                    if "error" in content.lower() or "traceback" in content.lower() or "exit code" in content.lower():
                        log_error(
                            cluster=13,  # cron noise cluster
                            tool="cron",
                            action=job_dir,
                            error_type="cron_failure",
                            error_msg=content[:300],
                            phase="卡住"
                        )
                        count += 1
                except:
                    pass
    return count


def summary():
    """Print error summary."""
    if not os.path.exists(INDEX_FILE):
        return "No errors recorded yet"
    with open(INDEX_FILE) as f:
        idx = json.load(f)
    
    lines = [f"📊 错误收集总览 (共 {idx['total_errors']} 条)"]
    for cid, info in sorted(idx["clusters"].items(), key=lambda x: -x[1]["count"]):
        lines.append(f"  C{cid}: {info['count']} 次")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "scan":
        n = scan_cron_logs()
        print(f"✅ 扫描完成，收录 {n} 条历史错误")
    elif len(sys.argv) > 1 and sys.argv[1] == "summary":
        print(summary())
    elif len(sys.argv) > 3:
        # Manual: python3 error-collector.py <cluster> <tool> <error_type> [solution]
        cluster = int(sys.argv[1])
        tool = sys.argv[2]
        error_type = sys.argv[3]
        solution = sys.argv[4] if len(sys.argv) > 4 else ""
        e = log_error(cluster, tool, "", error_type, "", solution)
        print(f"✅ 已记录: C{cluster} | {tool} | {error_type}")
    else:
        print("Usage: error-collector.py [scan|summary|cluster tool error_type solution]")
