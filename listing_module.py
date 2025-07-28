import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API key securely from environment variable
openai.api_key = os.getenv("AmazonTool_API_KEY")

def generate_listing(keyword: str):
    prompt = f"""
You are an Amazon listing expert. Write an SEO-optimized product listing for: "{keyword}"

Include:
- A title (under 200 characters)
- 5 benefit-focused bullet points
- A compelling product description
- Backend search terms (not visible to buyers)

Format your response as JSON:
{{
  "title": "...",
  "bullets": ["...", "...", "...", "...", "..."],
  "description": "...",
  "backend_keywords": "..."
}}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        content = response.choices[0].message["content"]
        return eval(content)  # Safely convert string to dict if trusted
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None
