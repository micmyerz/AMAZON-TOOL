import requests
import json
import pandas as pd
import re
from time import sleep
from pytrends.request import TrendReq
from random import uniform

# High-intent keywords to look for
HIGH_INTENT = ["buy", "best", "top", "cheap", "affordable", "top rated"]
USER_AGENT = "Mozilla/5.0"
SEM_API_KEY = "your_semrush_api_key"  # Replace with your actual SEMrush API key

def get_amazon_suggestions(keyword):
    url = f"https://completion.amazon.com/search/complete"
    params = {"method": "completion", "search-alias": "aps", "mkt": 1, "q": keyword}
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return json.loads(response.text)[1]
    except Exception as e:
        print(f"Amazon error for {keyword}: {e}")
    return []

pytrends = TrendReq(hl='en-US', tz=360)

def get_trend_score(keyword):
    try:
        pytrends.build_payload([keyword], cat=0, timeframe='now 7-d', geo='', gprop='')
        df = pytrends.interest_over_time()
        return int(df[keyword].mean()) if not df.empty else 0
    except:
        return 0

def get_semrush_data(keyword):
    url = "https://api.semrush.com"
    params = {
        "type": "phrase_this",
        "key": SEM_API_KEY,
        "export_columns": "Ph,Nq,Co,Kd",
        "phrase": keyword,
        "database": "us"
    }
    try:
        res = requests.get(url, params=params)
        lines = res.text.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split(';')
            return {
                "volume": int(parts[1]),
                "competition": float(parts[2]),
                "kd": float(parts[3])
            }
    except Exception as e:
        print(f"SEMrush error for {keyword}: {e}")
    return {"volume": 0, "competition": 1.0, "kd": 100.0}

def is_high_intent(keyword):
    return any(term in keyword.lower() for term in HIGH_INTENT)

def fetch_keywords(seeds, trend_min, vol_min, comp_max, require_intent):
    all_keywords = []

    for seed in seeds:
        suggestions = get_amazon_suggestions(seed)
        for suggestion in suggestions:
            trend = get_trend_score(suggestion)
            sleep(uniform(1, 2))
            sem = get_semrush_data(suggestion)
            sleep(uniform(1, 2))

            if (trend >= trend_min and
                sem['volume'] >= vol_min and
                sem['competition'] <= comp_max and
                (not require_intent or is_high_intent(suggestion))):

                all_keywords.append({
                    "seed": seed,
                    "keyword": suggestion,
                    "trend_score": trend,
                    "volume": sem["volume"],
                    "competition": sem["competition"],
                    "kd": sem["kd"]
                })

    return pd.DataFrame(all_keywords)
