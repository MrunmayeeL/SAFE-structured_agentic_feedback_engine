import os
from groq import Groq

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model="qwen2.5-coder:1.5b",
    messages=[{"role": "user", "content": "Say hello"}]
)

print(response.choices[0].message.content)

# To check models:
# models = client.models.list()
# for m in models.data:
#     print(m.id)

