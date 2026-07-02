#!/usr/bin/env python3
"""Monthly cluster drift report — compare current distribution vs baseline."""
import json, sys
from datetime import datetime

BASELINE = "./data/drift-baseline.json"
CURRENT = "./data/cluster-experience.json"

def load_notes(path):
    with open(path) as f:
        return json.load(f)

def report():
    baseline_data = load_notes(BASELINE) if BASELINE else None
    current = load_notes(CURRENT)
    
    total = sum(c.get('sessions', 0) for c in current.values())
    noise = current.get('13', {}).get('sessions', 0)
    real = total - noise
    
    lines = [f"📊 簇漂移月报 — {datetime.now().strftime('%Y-%m-%d')}"]
    lines.append(f"{'='*50}")
    lines.append(f"  真实对话: {real} (上月 baseline: ?)")
    
    for cid in sorted(current.keys(), key=lambda x: -current[x].get('sessions', 0)):
        c = current[cid]
        s = c.get('sessions', 0)
        if s < 5:
            continue
        pct = round(s / real * 100, 1) if real else 0
        kw = ', '.join(c.get('top_keywords', [])[:3])
        
        # Compare with baseline
        delta = ""
        if baseline_data:
            old_cluster = baseline_data.get('clusters', {}).get(f"C{cid}", {})
            old_pct = old_cluster.get('pct_of_real', 0)
            diff = round(pct - old_pct, 1)
            if diff > 2:
                delta = " ▲▲ 增长"
            elif diff > 0.5:
                delta = " ▲ 微增"
            elif diff < -2:
                delta = " ▼▼ 下降"
            elif diff < -0.5:
                delta = " ▼ 微降"
        
        bar = '█' * int(pct / 2)
        lines.append(f"  C{cid}: {s:>4}次 ({pct:>4.1f}%) {bar} {kw}{delta}")
    
    lines.append(f"\n  噪声 C13: {noise} 次")
    return '\n'.join(lines)

if __name__ == "__main__":
    print(report())
