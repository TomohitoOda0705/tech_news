import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
location = "us-central1"

if not project_id:
    print("GOOGLE_CLOUD_PROJECT not set")
    exit()

client = genai.Client(
    vertexai=True,
    project=project_id,
    location=location
)

prompt = "Find 3 upcoming peatix events in Tokyo for next month. Return as JSON list with title, date, url."

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            # response_mime_type="application/json"
        )
    )
    print("Response received.")
    print(f"Text: {response.text}")
    # print(response.model_dump_json(indent=2))
except Exception as e:
    print(f"Error: {e}")
