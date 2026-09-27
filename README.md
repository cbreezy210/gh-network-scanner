# 🕵️‍♂️ GitHub Network Scanner

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-success.svg?style=flat-square)]()

A zero-dependency, safety-first Python script to discover high-signal developers in your second-degree GitHub network. 

Stop relying on algorithmic feeds. Map the hidden connections. Find the peers your peers trust.

## 🚀 Why this exists

GitHub's native "Explore" feed is full of noise. If you want to find true domain experts—C++ reverse engineers, local-AI builders, systems architects—you need to look at the intersection of the people *you* trust and the people *they* trust.

This is the exact tool recently used to discover and connect with Switch homebrew legends (ClusterM, fincs, WinterMute) and local-AI architects, proving the zero-dependency, safety-first architecture in the wild.

This script crawls your network, cross-references the "following" lists of your connections, and applies a strict **Quality Gate** to filter out bots, mass-followers, and tutorial-grinders.

## ✨ Features

- **Zero Dependencies:** Uses only Python's standard library (`urllib`, `json`, `pickle`). No `pip install` hell.
- **Safety-First:** Never hardcodes your Personal Access Token. Pulls strictly from environment variables.
- **Smart Quality Gate:** Automatically filters out accounts with `>800` following or `<3` public repos.
- **Intelligent Caching:** Saves API responses locally. Re-runs are instant and won't burn your 5,000/hr rate limit.
- **Language Enrichment:** Fetches the top languages of your final recommendations so you know *what* they build.
- **Rate-Limit Aware:** Automatically pauses and resumes if you hit the GitHub API ceiling.

## 🛠️ Setup

### 1. Generate a Read-Only Token
1. Go to GitHub **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**.
2. Generate a new token. Name it `network-scanner`.
3. **Crucial:** ONLY check the `read:user` scope. Do not grant repo access.
4. Copy the generated token (starts with `ghp_...`).

### 2. Inject the Token
Open your terminal and inject the token into your session's memory. **Do not paste it into the script.**

**Mac / Linux / WSL:**
```bash
export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"
```

**Windows PowerShell:**
```powershell
$env:GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"
```

**Windows CMD:**
```cmd
set GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
```

## 📖 Usage

Run the script directly from your terminal.

```bash
# Basic scan (scans 30 peers, max 300 following per peer)
python gh_network_scanner.py

# Scan a specific user's network
python gh_network_scanner.py -u torvalds

# Deep scan: 50 peers, 500 following per peer, export to JSON
python gh_network_scanner.py -s 50 -c 500 -o results.json

# Clear the cache and fetch entirely fresh data
python gh_network_scanner.py --no-cache
```

### CLI Arguments
| Flag | Description | Default |
| :--- | :--- | :--- |
| `-u`, `--user` | Target GitHub username to scan | `cbreezy210` |
| `-s`, `--sample` | Number of peers to scan from your network | `30` |
| `-c`, `--cap` | Max "following" to scan per peer (prevents API burn) | `300` |
| `-o`, `--output` | File path to export the final results as JSON | `None` |
| `--no-cache` | Ignore `.gh_scanner_cache.pkl` and fetch fresh API data | `False` |

## 📊 Example Output

```text
🚀 Initializing GitHub Network Scanner for [cbreezy210]...
🔍 Scanning second-degree connections of 30 peers (cap: 300/peer)...

[██████████████████████████████] 30/30

⚙️  Enriching top candidates with repository data...

======================================================================
🎯 HIGH-SIGNAL RECOMMENDATIONS FOR [cbreezy210] (Filtered)
======================================================================
Username                  | Score  | Top Languages
----------------------------------------------------------------------
ra3orblade                | 5      | TypeScript, Rust, Go
PIsberg                   | 4      | Java, Shell
plutooo                   | 2      | C, C++, Assembly
nibor1896                 | 2      | C#, Python
MyShiLingStar             | 2      | C++, C#

✅ Scan complete. Zero dependencies. Stay sharp. ☕🔥
```

## 🧠 The Quality Gate Logic

The script assumes that high-signal engineers curate their networks, while bots and engagement-farmers mass-follow. 
A candidate is **rejected** if:
- They are following more than **800** people.
- They have fewer than **3** public repositories.

*Note: If you want to tweak the strictness of the gate, edit the `bad = ...` boolean logic inside the `get_profile` check in the source code.*

## 📜 License

MIT License. Build with it, break it, improve it.
