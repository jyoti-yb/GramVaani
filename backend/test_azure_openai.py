from dotenv import load_dotenv
from openai import AzureOpenAI
import os

load_dotenv()

azure_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

try:
    response = azure_client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in one sentence."}
        ],
        max_tokens=50
    )
    
    print("✓ Azure OpenAI connection successful!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"✗ Azure OpenAI error: {e}")
