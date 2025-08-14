import os
from openai import OpenAI

# Load from environment variables
API_KEY = "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"
BASE_URL = "https://models.github.ai/inference"
MODEL_NAME = "openai/gpt-4o"

def main():
    if not API_KEY or not BASE_URL:
        print("Missing GITHUB_MODELS_API_KEY or GITHUB_MODELS_BASE_URL in environment.")
        return

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello from GitHub Models API and introduce yourself, which model are you."}
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=100,
            stream=False
        )
        print("Response from model:")
        print(response.choices[0].message.content)
    except Exception as e:
        print("Error communicating with GitHub Models API:", e)

if __name__ == "__main__":
    main()