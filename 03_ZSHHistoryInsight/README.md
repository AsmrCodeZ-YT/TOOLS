# 📊 ZSH History Insight

> **Unlock the secrets of your terminal usage.** > A powerful Python tool to visualize, analyze, and extract deep insights from your ZSH history file.



**ZSH History Insight** parses your `.zsh_history` file to generate advanced statistics, including productivity trends, command transition graphs (Markov chains), and anomaly detection. It helps you understand your workflow and optimize your shell usage.

## ✨ Features

- **🔍 Deep Sequence Analysis:** Uses Markov Chains to analyze which commands usually follow others.
- **📈 Visualizations:** Generates:
  - **Transition Graphs:** Visual network of your command flows.
  - **Heatmaps:** Activity density by Hour vs. Day of Week.
- **⏱ Productivity Trends:** Daily and weekly command usage statistics.
- **🚨 Anomaly Detection:** Identifies rare commands and activity at unusual hours.
- **🛠 Parsing:** Breaks down commands into base commands vs. arguments.
- **💾 Export Data:** Exports parsed data to `JSON` and `CSV` for further analysis.
- **📝 Typo Detection:** Identifies corrected typos (e.g., `git stats` -> `git status`).

