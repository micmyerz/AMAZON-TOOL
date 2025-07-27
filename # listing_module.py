# listing_module.py

import openai
import os

# Load API key securely from local file
def load_openai_key():
    with open("AmazonTool_API_KEY", "r") as file:
        return file.read().strip()

openai.api_key = load_openai_key()

def generate_listing(keyword: str) -> dict:
    prompt = f"""
You are an Amazon listing expert. Write a compelling product listing for the following keyword: "{keyword}"

Respond with JSON in this format:
{{
  "title": "...",
  "bullet_points": ["...", "...", "...", "...", "..."],
  "description": "..."
}}

Make sure:
- Title includes the keyword
- Bullet points highlight benefits and features
- Description sounds natural and persuasive
- Language is suitable for high-converting Amazon product pages
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert Amazon seller assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )

        text_output = response['choices'][0]['message']['content']

        # Attempt to safely evaluate the response as a dictionary
        import json
        return json.loads(text_output)

    except Exception as e:
        print(f"Error generating listing for keyword '{keyword}':", e)
        return {
            "title": f"{keyword} | Premium Product",
            "bullet_points": ["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5"],
            "description": f"This is a high-quality product for '{keyword}'."