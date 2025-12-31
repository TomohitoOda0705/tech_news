from google import genai
from google.genai import types
import os

class NewsSummarizer:
    def __init__(self):
        self.project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        self.location = "us-central1"
        
        if not self.project_id:
            print("Warning: GOOGLE_CLOUD_PROJECT environment variable is not set.")
            self.client = None
            return

        try:
            self.client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location
            )
            self.model = "gemini-2.5-flash"
        except Exception as e:
            print(f"Error initializing GenAI Client: {e}")
            self.client = None

    def summarize(self, title, original_summary):
        if not self.client:
            return original_summary

        prompt = f"""
以下の技術記事のタイトルと概要を読んで、エンジニア向けに日本語で要約してください。
出力は3点の箇条書きのみにしてください。

Title: {title}
Summary: {original_summary}
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=1024,
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating summary for '{title}': {e}")
            return original_summary
