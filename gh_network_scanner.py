#!/usr/bin/env python3
"""
GitHub Network Radar: Second-degree connection discovery.
Zero dependencies. Safety-first. High-signal filtering.
"""

import json
import os
import sys
import time
import pickle
import argparse
import urllib.request
import urllib.error
from collections import Counter

# --- CLI Configuration ---
parser = argparse.ArgumentParser(description="🕵️‍♂️ Second-degree GitHub network scanner.")
parser.add_argument("-u", "--user", default="cbreezy210", help="Target GitHub username (default: cbreezy210)")
parser.add_argument("-s", "--sample", type=int, default=30, help="Number of peers to scan (default: 30)")
parser.add_argument("-c", "--cap", type=int, default=300, help="Max following to scan per peer (default: 300)")
parser.add_argument("-o", "--output", help="Export results to JSON file")
parser.add_argument("--no-cache", action="store_true", help="Ignore existing cache and fetch fresh data")
args = parser.parse_args()

# --- Safety-First Token Injection ---
TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    print("❌ Error: GITHUB_TOKEN not found in environment variables.")
    print("Run this in your terminal first:")
    print('  Mac/Linux/WSL: export GITHUB_TOKEN="your_actual_token_here"')
    print('  Windows PowerShell: $env:GITHUB_TOKEN="your_actual_token_here"')
    sys.exit(1)

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "gh-network-radar",
}
CACHE_FILE = ".gh_radar_cache.pkl"

# --- Cache Management ---
def load_cache():
    if args.no_cache or not os.path.exists(CACHE_FILE):
        return {"profiles": {}, "followings": {}}
    try:
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)
    except Exception:
        return {"profiles": {}, "followings": {}}

def save_cache(cache):
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)

cache = load_cache()

# --- API Engine ---
def api_get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body), resp.headers.get("Link", "")
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            reset = e.headers.get("X-RateLimit-Reset")
            if reset:
                wait = max(int(reset) - int(time.time()), 5)
                print(f"\n⏳ Rate limit hit. Waiting {wait}s...")
                time.sleep(wait)
                return api_get(url)
        return None, ""
    except Exception as e:
        return None, ""

def next_url(link_header):
    for part in link_header.split(","):
        if 'rel="next"' in part:
            return part.split(";")[0].strip().strip("<>")
    return None

def get_pages(url, max_pages=999):
    results, current_url, pages = [], url, 0
    while current_url and pages < max_pages:
        if current_url in cache["followings"]:
            data, link = cache["followings"][current_url]
        else:
            data, link = api_get(current_url)
            cache["followings"][current_url] = (data, link)
            
        if not data or not isinstance(data, list): break
        results.extend(data)
        current_url = next_url(link)
        pages += 1
        time.sleep(0.2) # Be nice to the API
    return results

def get_profile(login):
    if login in cache["profiles"]:
        return cache["profiles"][login]
    url = f"https://api.github.com/users/{login}"
    data, _ = api_get(url)
    cache["profiles"][login] = data
    return data

def get_top_languages(login):
    url = f"https://api.github.com/users/{login}/repos?sort=updated&per_page=5"
    repos, _ = api_get(url)
    if not repos: return "N/A"
    langs = set(r.get("language") for r in repos if r.get("language"))
    return ", ".join(langs) if langs else "N/A"

# --- Progress Bar ---
def progress(current, total, width=30):
    filled = int(width * current / total)
    bar = "█" * filled + "-" * (width - filled)
    sys.stdout.write(f"\r[{bar}] {current}/{total}")
    sys.stdout.flush()

# --- Main Execution ---
print(f"🚀 Initializing GitHub Network Radar for [{args.user}]...")
my_following = {u["login"] for u in get_pages(f"https://api.github.com/users/{args.user}/following")}
my_followers = {u["login"] for u in get_pages(f"https://api.github.com/users/{args.user}/followers")}
network_pool = list((my_following | my_followers) - {args.user})

sample_size = min(args.sample, len(network_pool))
sample_pool = network_pool[:sample_size]
print(f"🔍 Scanning second-degree connections of {sample_size} peers (cap: {args.cap}/peer)...\n")

recommendations = Counter()
checked_profiles = {}
cap_pages = max(1, args.cap // 100) # 100 items per page

for i, peer in enumerate(sample_pool):
    progress(i + 1, sample_size)
    their_following = get_pages(f"https://api.github.com/users/{peer}/following", max_pages=cap_pages)
    
    for target in their_following:
        login = target["login"]
        if login in my_following or login == args.user:
            continue

        if login not in checked_profiles:
            profile = get_profile(login)
            if profile:
                # THE QUALITY GATE
                bad = profile.get("following", 0) > 800 or profile.get("public_repos", 0) < 3
                checked_profiles[login] = not bad
            else:
                checked_profiles[login] = False
                
        if checked_profiles.get(login, False):
            recommendations[login] += 1

save_cache(cache)
print("\n\n⚙️  Enriching top candidates with repository data...")
top_candidates = recommendations.most_common(15)
enriched_results = []

for user, score in top_candidates:
    langs = get_top_languages(user)
    enriched_results.append((user, score, langs))
    time.sleep(0.2)

# --- Output ---
print("\n" + "=" * 70)
print(f"🎯 HIGH-SIGNAL RECOMMENDATIONS FOR [{args.user}] (Filtered)")
print("=" * 70)
print(f"{'Username':<25} | {'Score':<6} | {'Top Languages'}")
print("-" * 70)

if not enriched_results:
    print("No high-signal recommendations found in this sample.")
else:
    for user, score, langs in enriched_results:
        print(f"{user:<25} | {score:<6} | {langs}")

if args.output:
    output_data = {
        "target_user": args.user,
        "scan_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "peers_scanned": sample_size,
        "recommendations": [{"login": u, "score": s, "languages": l} for u, s, l in enriched_results]
    }
    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\n📄 Results exported to {args.output}")

print("\n✅ Scan complete. Zero dependencies. Stay sharp. ☕🔥")