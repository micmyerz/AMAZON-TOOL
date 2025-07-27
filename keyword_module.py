# keyword_module.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
import numpy as np

import requests
import json

def fetch_related_keywords(seed_keyword: str, max_results: int = 10) -> list:
    """
    Fetches keyword suggestions from Google Suggest API for SEO research.
    
    Args:
        seed_keyword (str): The main product keyword.
        max_results (int): Max number of keyword suggestions to return.

    Returns:
        List[str]: A list of related keyword strings.
    """
    try:
        response = requests.get(
            "https://suggestqueries.google.com/complete/search",
            params={
                "client": "firefox",
                "q": seed_keyword
            },
            timeout=10
        )

        suggestions = response.json()[1]
        return suggestions[:max_results]

    except Exception as e:
        print(f"Error fetching keywords for '{seed_keyword}':", e)
        return [seed_keyword]  # fallback to seed

import re

# High-intent terms to filter for buying intent
HIGH_INTENT_TERMS = ["buy", "best", "top", "cheap", "affordable", "review", "discount"]

SEM_API_KEY = "your_semrush_api_key_here"  # Replace with your real key

def get_semrush_data(keyword: str) -> dict:
    """
    Placeholder to get search volume and competition from SEMrush API.
    Returns a dict with keys: volume (int), competition (float 0-1).
    """
    url = "https://api.semrush.com/"
    params = {
        "type": "phrase_this",
        "key": SEM_API_KEY,
        "export_columns": "Ph,Nq,Co",
        "phrase": keyword,
        "database": "us"
    }
    try:
        response = requests.get(url, params=params)
        lines = response.text.strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].split(";")
            return {
                "volume": int(parts[1]),
                "competition": float(parts[2])
            }
    except Exception as e:
        print(f"SEMrush API error for '{keyword}': {e}")
    return {"volume": 0, "competition": 1.0}

def is_high_intent(keyword: str) -> bool:
    """
    Returns True if keyword contains any high intent term.
    """
    return any(re.search(rf"\b{term}\b", keyword, re.I) for term in HIGH_INTENT_TERMS)

def fetch_filtered_keywords(
    seed_keyword: str,
    max_results: int = 20,
    trend_min: int = 10,
    vol_min: int = 1000,
    comp_max: float = 0.7,
    require_intent: bool = True
) -> list:
    """
    Fetch keywords filtered by trends, volume, competition, and intent.
    """
    raw_keywords = fetch_related_keywords(seed_keyword, max_results)
    filtered_keywords = []

    for kw in raw_keywords:
        trend_score = get_trend_score(kw)
        sem_data = get_semrush_data(kw)

        if (
            trend_score >= trend_min and
            sem_data["volume"] >= vol_min and
            sem_data["competition"] <= comp_max and
            (not require_intent or is_high_intent(kw))
        ):
            filtered_keywords.append(kw)

    return filtered_keywords