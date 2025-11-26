#!/usr/bin/env python3
"""
Advanced ZSH History Analyzer – Full English
10+ Cool Analyses + Visualizations + Export
"""

import re
import sys
import json
import csv
from collections import Counter, defaultdict, deque
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import networkx as nx
from itertools import islice
import numpy as np

# === CONFIG ===
TYPO_THRESHOLD = 2
SESSION_GAP = 300
TOP_N = 10
EXPORT_JSON = "zsh_analysis.json"
EXPORT_CSV = "zsh_commands.csv"
PLOT_DIR = "zsh_plots"
# =================

def levenshtein(a, b):
    if len(a) < len(b): a, b = b, a
    if not b: return len(a)
    prev = list(range(len(b) + 1))
    for i, c1 in enumerate(a):
        curr = [i + 1]
        for j, c2 in enumerate(b):
            curr.append(min(
                prev[j + 1] + 1,
                curr[j] + 1,
                prev[j] + (c1 != c2)
            ))
        prev = curr
    return prev[-1]

def load_history(filename="zshrc_history"):
    entries = []
    pattern = re.compile(r": (\d+):(\d+);(.*)")
    try:
        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or not line.startswith(":"): continue
                m = pattern.match(line)
                if m:
                    ts, dur, cmd = m.groups()
                    entries.append({
                        "ts": int(ts),
                        "duration": int(dur),
                        "cmd": cmd.strip(),
                        "dt": datetime.fromtimestamp(int(ts))
                    })
    except FileNotFoundError:
        print(f"[ERROR] File '{filename}' not found.")
        sys.exit(1)
    return sorted(entries, key=lambda x: x["ts"])

# === PARSE COMMAND: base + args ===
def parse_command(cmd):
    parts = cmd.strip().split()
    if not parts: return None, []
    base = parts[0]
    args = parts[1:]
    return base, args

# === 1. COMMAND SEQUENCES & MARKOV CHAIN ===
def analyze_sequences(entries):
    print("\n=== 1. Command Sequences & Markov Chain ===")
    seqs = [(entries[i]["cmd"], entries[i+1]["cmd"]) for i in range(len(entries)-1)]
    chain = defaultdict(lambda: defaultdict(int))
    for prev, nxt in seqs:
        chain[prev][nxt] += 1

    # Top transitions
    print(f"Top {TOP_N} command transitions:")
    transitions = []
    for prev, nxts in chain.items():
        total = sum(nxts.values())
        for nxt, cnt in nxts.items():
            transitions.append((prev, nxt, cnt, cnt/total))
    transitions.sort(key=lambda x: x[2], reverse=True)
    for prev, nxt, cnt, prob in transitions[:TOP_N]:
        print(f"  '{prev}' → '{nxt}' : {cnt} times ({prob:.2%})")

    # Build graph
    G = nx.DiGraph()
    for prev, nxt, cnt, _ in transitions:
        if cnt >= 2:  # filter noise
            G.add_edge(prev, nxt, weight=cnt)
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, k=1, iterations=50)
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue",
            font_size=8, font_weight="bold", arrows=True,
            edge_color="gray", width=[d["weight"]/5 for u,v,d in G.edges(data=True)])
    plt.title("Command Transition Graph (weight = frequency)")
    plt.savefig(f"{PLOT_DIR}/transition_graph.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  → Graph saved: {PLOT_DIR}/transition_graph.png")

    return chain

# === 2. COMMAND PARSING: base + args ===
def analyze_parsing(entries):
    print("\n=== 2. Command Parsing (base + args) ===")
    base_counter = Counter()
    arg_counter = defaultdict(Counter)
    for e in entries:
        base, args = parse_command(e["cmd"])
        if not base: continue
        base_counter[base] += 1
        for arg in args:
            arg_counter[base][arg] += 1

    print(f"Top {TOP_N} base commands:")
    for base, cnt in base_counter.most_common(TOP_N):
        print(f"  {base}: {cnt}")

    print(f"\nTop arguments per command (sample):")
    for base in list(base_counter.keys())[:5]:
        top_args = arg_counter[base].most_common(3)
        if top_args:
            print(f"  {base}: {[a for a,_ in top_args]}")

    return base_counter, arg_counter

# === 3. PRODUCTIVITY TRENDS ===
def analyze_productivity(entries):
    print("\n=== 3. Productivity Trends (Daily/Weekly) ===")
    daily = Counter(e["dt"].date() for e in entries)
    hourly = Counter(e["dt"].hour for e in entries)
    dow = Counter(e["dt"].weekday() for e in entries)  # 0=Mon

    print("Daily command count (last 7 days):")
    recent = sorted(daily.items(), reverse=True)[:7]
    for date, cnt in recent:
        print(f"  {date}: {cnt} cmds")

    print("\nAverage commands per day of week:")
    dow_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for d in range(7):
        days = sum(1 for date in daily if date.weekday() == d)
        avg = sum(cnt for date, cnt in daily.items() if date.weekday() == d) / max(1, days)
        print(f"  {dow_names[d]}: {avg:.1f} cmds/day")

    # Heatmap: hour vs day
    dates = sorted({e["dt"].date() for e in entries})
    if len(dates) > 1:
        matrix = np.zeros((24, 7))
        for e in entries:
            h, d = e["dt"].hour, e["dt"].weekday()
            matrix[h, d] += 1
        plt.figure(figsize=(8, 6))
        plt.imshow(matrix, cmap="YlOrRd", aspect="auto")
        plt.colorbar(label="Commands")
        plt.xticks(range(7), dow_names)
        plt.yticks(range(0, 24, 2))
        plt.xlabel("Day of Week")
        plt.ylabel("Hour")
        plt.title("Command Heatmap")
        plt.savefig(f"{PLOT_DIR}/heatmap.png", dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  → Heatmap saved: {PLOT_DIR}/heatmap.png")

# === 4. ANOMALY DETECTION ===
def detect_anomalies(entries, cmd_counter):
    print("\n=== 4. Anomaly Detection ===")
    # Rare commands
    rare = [cmd for cmd, cnt in cmd_counter.items() if cnt == 1]
    print(f"Rare commands (used once): {len(rare)} → e.g., {rare[:5]}")

    # Unusual times
    hours = [e["dt"].hour for e in entries]
    mean_h, std_h = np.mean(hours), np.std(hours)
    outliers = [e for e in entries if abs(e["dt"].hour - mean_h) > 2*std_h]
    print(f"Time outliers (beyond 2σ): {len(outliers)} commands")
    if outliers:
        print(f"  Example: {outliers[0]['cmd']} at {outliers[0]['dt'].strftime('%H:%M')}")

# === 7. PREDICTIVE INSIGHTS ===
def predictive_insights(chain, zshrc_edits, zshrc_sources):
    print("\n=== 7. Predictive Insights ===")
    # After edit → source?
    good = sum(1 for e in zshrc_edits
               if any(s["ts"] > e["ts"] and s["ts"] - e["ts"] < 30 for s in zshrc_sources))
    print(f"  Auto-source after edit: {good}/{len(zshrc_edits)}")

    # Common next command
    common_next = max(chain.items(), key=lambda x: sum(x[1].values()), default=(None, {}))
    if common_next[0]:
        nxt = max(common_next[1].items(), key=lambda x: x[1])[0]
        print(f"  Most predictable: '{common_next[0]}' → '{nxt}'")

# === 8. EXPORT DATA ===
def export_data(entries, base_counter):
    print(f"\n=== 8. Exporting Data ===")
    # JSON
    data = {
        "total": len(entries),
        "commands": [e["cmd"] for e in entries],
        "timestamps": [e["ts"] for e in entries],
        "top_commands": dict(base_counter.most_common(TOP_N))
    }
    with open(EXPORT_JSON, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  → JSON: {EXPORT_JSON}")

    # CSV
    with open(EXPORT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "datetime", "command", "duration"])
        for e in entries:
            writer.writerow([e["ts"], e["dt"].isoformat(), e["cmd"], e["duration"]])
    print(f"  → CSV: {EXPORT_CSV}")

# === MAIN ===
def main():
    import os
    os.makedirs(PLOT_DIR, exist_ok=True)

    filename = sys.argv[1] if len(sys.argv) > 1 else "zshrc_history"
    entries = load_history(filename)
    if not entries:
        return

    cmd_counter = Counter(e["cmd"] for e in entries)
    zshrc_edits = [e for e in entries if "~/.zshrc" in e["cmd"] and any(x in e["cmd"] for x in ["nvim", "nano", "vi", "vim"])]
    zshrc_sources = [e for e in entries if e["cmd"] in ["source ~/.zshrc", "suorce ~/.zshrc"]]

    # Run all advanced analyses
    chain = analyze_sequences(entries)
    analyze_parsing(entries)
    analyze_productivity(entries)
    detect_anomalies(entries, cmd_counter)
    predictive_insights(chain, zshrc_edits, zshrc_sources)
    export_data(entries, Counter(parse_command(e["cmd"])[0] for e in entries if parse_command(e["cmd"])[0]))

    print(f"\nAll analyses complete! Check '{PLOT_DIR}/' for plots.")

if __name__ == "__main__":
    main()