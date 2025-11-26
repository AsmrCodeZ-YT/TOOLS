#!/usr/bin/env python3
import re
from collections import Counter
from datetime import datetime
import sys

# Settings
TYPO_THRESHOLD = 2          # Max Levenshtein distance to detect typo
SESSION_GAP = 300           # 5 minutes in seconds → new session
TOP_N = 10                  # Number of top commands to show

# Levenshtein distance (for typo detection)
def levenshtein(a, b):
    if len(a) < len(b):
        a, b = b, a
    if len(b) == 0:
        return len(a)
    previous_row = list(range(len(b) + 1))
    for i, c1 in enumerate(a):
        current_row = [i + 1]
        for j, c2 in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

# Load history file
def load_history(filename="zshrc_history"):
    entries = []
    pattern = re.compile(r": (\d+):(\d+);(.*)")
    try:
        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or not line.startswith(":"):
                    continue
                match = pattern.match(line)
                if match:
                    ts, duration, cmd = match.groups()
                    entries.append({
                        "ts": int(ts),
                        "duration": int(duration),
                        "cmd": cmd.strip(),
                        "dt": datetime.fromtimestamp(int(ts))
                    })
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    return entries

# Main analysis
def analyze_history(entries):
    if not entries:
        print("No commands found in history.")
        return

    print("="*60)
    print("           ZSH HISTORY FULL ANALYSIS")
    print("="*60)

    # 1. Total commands
    total = len(entries)
    print(f"1. Total Commands: {total}")

    # 2. Unique commands
    commands = [e["cmd"] for e in entries]
    cmd_counter = Counter(commands)
    unique_count = len(cmd_counter)
    print(f"2. Unique Commands: {unique_count}")

    # 3. Top N most frequent commands
    print(f"\n3. Top {TOP_N} Most Frequent Commands:")
    top_n = cmd_counter.most_common(TOP_N)
    max_count = top_n[0][1] if top_n else 1
    for cmd, count in top_n:
        bar_length = int(50 * count / max_count)
        bar = "#" * bar_length
        print(f"   {cmd[:40]:<40} | {bar} ({count})")

    # 4. Time analysis
    timestamps = [e["ts"] for e in entries]
    first_ts = min(timestamps)
    last_ts = max(timestamps)
    total_duration = last_ts - first_ts
    hours_active = total_duration / 3600

    print(f"\n4. Time Analysis:")
    print(f"   First command:  {datetime.fromtimestamp(first_ts)}")
    print(f"   Last command:   {datetime.fromtimestamp(last_ts)}")
    print(f"   Total span:     {total_duration//3600}h {(total_duration%3600)//60}m")
    print(f"   Avg commands/hour: {total / max(1, hours_active):.2f}")

    # Hourly distribution
    hour_dist = Counter(e["dt"].hour for e in entries)
    print(f"   Hourly activity (0-23):")
    max_hour_count = max(hour_dist.values(), default=1)
    for h in range(24):
        count = hour_dist[h]
        bar = "█" * (count * 50 // max(1, max_hour_count))
        print(f"     {h:02d}:00 | {bar} {count}")

    # 5. Editor usage
    print(f"\n5. Editor Usage:")
    editors = {"nvim": 0, "nano": 0, "vi": 0, "vim": 0, "emacs": 0}
    for cmd in commands:
        for editor in editors:
            if cmd.startswith(editor + " ") or cmd == editor:
                editors[editor] += 1
    for editor, count in editors.items():
        if count > 0:
            print(f"   {editor}: {count} time(s)")

    # 6. Typo detection (mistake → correction within 10 seconds)
    print(f"\n6. Likely Typos (corrected within 10s):")
    typos = []
    for i in range(len(entries) - 1):
        cmd1 = entries[i]["cmd"]
        cmd2 = entries[i+1]["cmd"]
        time_diff = entries[i+1]["ts"] - entries[i]["ts"]
        if time_diff < 10:
            distance = levenshtein(cmd1, cmd2)
            if 1 <= distance <= TYPO_THRESHOLD and len(cmd1) > 3 and len(cmd2) > 3:
                typos.append((cmd1, cmd2, time_diff))
    if typos:
        for bad, good, diff in typos[:10]:
            print(f"   '{bad}' → '{good}' (in {diff}s)")
    else:
        print("   No clear typos detected.")

    # 7. Time gaps between commands
    gaps = [entries[i+1]["ts"] - entries[i]["ts"] for i in range(len(entries)-1)]
    avg_gap = sum(gaps) / len(gaps) if gaps else 0
    max_gap = max(gaps) if gaps else 0
    print(f"\n7. Command Gaps:")
    print(f"   Average gap: {avg_gap:.1f} seconds")
    print(f"   Max gap:     {max_gap} seconds (~{max_gap//60} minutes)")

    # 8. Work sessions (gap > SESSION_GAP)
    sessions = []
    current = [entries[0]]
    for i in range(1, len(entries)):
        if entries[i]["ts"] - entries[i-1]["ts"] > SESSION_GAP:
            sessions.append(current)
            current = [entries[i]]
        else:
            current.append(entries[i])
    sessions.append(current)

    print(f"\n8. Work Sessions (gap > {SESSION_GAP//60} min): {len(sessions)} session(s)")
    for i, sess in enumerate(sessions[:5], 1):
        start = sess[0]["dt"]
        end = sess[-1]["dt"]
        count = len(sess)
        duration_min = (sess[-1]["ts"] - sess[0]["ts"]) // 60
        print(f"   Session {i}: {start.strftime('%H:%M')} → {end.strftime('%H:%M')} | {count} cmds | {duration_min} min")
    if len(sessions) > 5:
        print(f"   ... and {len(sessions)-5} more session(s)")

    # 9. ~/.zshrc behavior
    zshrc_edits = [e for e in entries if "~/.zshrc" in e["cmd"] and any(ed in e["cmd"] for ed in ["nvim", "nano", "vi", "vim"])]
    zshrc_sources = [e for e in entries if e["cmd"] in ["source ~/.zshrc", "suorce ~/.zshrc"]]

    print(f"\n9. ~/.zshrc Behavior:")
    print(f"   Edits:     {len(zshrc_edits)} time(s)")
    print(f"   Sources:   {len(zshrc_sources)} time(s)")

    # Did user source after edit (within 30s)?
    good_behavior = 0
    for edit in zshrc_edits:
        edit_time = edit["ts"]
        for src in zshrc_sources:
            if src["ts"] > edit_time and src["ts"] - edit_time < 30:
                good_behavior += 1
                break
    print(f"   Good behavior (edit → source < 30s): {good_behavior}/{len(zshrc_edits)}")

    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60)

# Run
if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "zshrc_history"
    entries = load_history(filename)
    analyze_history(entries)