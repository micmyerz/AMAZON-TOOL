# keyword_module.py

import requests
import json
import re
from time import sleep
from random import uniform
from pytrends.request import TrendReq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering

# Initialize Google Trends client
pytrends = TrendReq(hl='en-US', tz=360)

# High-intent terms for filtering
HIGH_INTENT_TERMS = ["buy", "best", "top", "cheap", "affordable", "review", "discount"]


def fetch_related_keywords(seed_keyword: str, max_results: int = 20) -> list:
    """Fetch keyword suggestions from Google Suggest API."""
    try:
        response = requests.get(
            "https://suggestqueries.google.com/complete/search",
            params={"client": "firefox", "q": seed_keyword},
            timeout=10
        )
        suggestions = response.json()[1]
        return suggestions[:max_results]
    except Exception as e:
        print(f"Error fetching keywords for '{seed_keyword}':", e)
        return [seed_keyword]  # fallback to seed


def get_trend_score(keyword: str) -> int:
    """Return average Google Trends interest over the last 7 days."""
    try:
        pytrends.build_payload([keyword], timeframe='now 7-d')
        df = pytrends.interest_over_time()
        if df.empty:
            return 0
        return int(df[keyword].mean())
    except Exception as e:
        print(f"Google Trends error for '{keyword}': {e}")
        return 0


def is_high_intent(keyword: str) -> bool:
    """Check if keyword contains high-intent terms."""
    return any(re.search(rf"\b{term}\b", keyword, re.I) for term in HIGH_INTENT_TERMS)


def fetch_filtered_keywords(
    seed_keyword: str,
    max_results: int = 20,
    trend_min: int = 10,
    require_intent: bool = True
) -> list:
    """
    Fetch keywords filtered by Google Trends interest and intent terms.
    """
    raw_keywords = fetch_related_keywords(seed_keyword, max_results)
    filtered_keywords = []

    for kw in raw_keywords:
        trend_score = get_trend_score(kw)

        if (
            trend_score >= trend_min and
            (not require_intent or is_high_intent(kw))
        ):
            filtered_keywords.append(kw)
        sleep(uniform(1, 2))  # Be polite to APIs

    return filtered_keywords


def cluster_keywords(keywords: list, distance_threshold=1.0) -> dict:
    """
    Cluster similar keywords using TF-IDF and Agglomerative Clustering.

    Returns a dict: cluster_id -> list of keywords.
    """
    if not keywords:
        return {}

    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(keywords)

    clustering_model = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        affinity='cosine',
        linkage='average'
    )

    clustering_model.fit(X.toarray())
    labels = clustering_model.labels_

    clusters = {}
    for label, keyword in zip(labels, keywords):
        clusters.setdefault(label, []).append(keyword)

    return clusters


if __name__ == "__main__":
    # Simple test
    seeds = ["wireless earbuds", "camping stove"]
    for seed in seeds:
        print(f"\nSeed keyword: {seed}")
        filtered = fetch_filtered_keywords(seed)
        clusters = cluster_keywords(filtered, distance_threshold=0.7)
        for cid, kws in clusters.items():
            print(f"Cluster {cid}:")
            for kw in kws:
                print(f" - {kw}")
