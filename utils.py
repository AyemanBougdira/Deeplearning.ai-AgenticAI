# === Standard Library ===
import os
import re
import json
import base64
import mimetypes
from pathlib import Path
import os
# === Third-Party ===
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image  # (kept if you need it elsewhere)
from dotenv import load_dotenv
from openai import OpenAI
# from anthropic import Anthropic
from html import escape


from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

#  ===== Setting up models ====

def get_response(prompt: str) -> str:
    completion = client.chat.completions.create(
        model="qwen/qwen2.5-vl-72b-instruct:free",
        messages=[
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ]
    )
    print(completion.choices[0].message.content)


def image_openai_call(prompt: str, image_url: str) -> str:
    completion = client.chat.completions.create(
        model="qwen/qwen2.5-vl-72b-instruct:free",
        messages=[
            {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"{prompt}"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"{image_url}"
                    }
                }
            ]
            }
        ]
    )
    print(completion.choices[0].message.content)





#  ==== Data loading & helpers===


def load_and_prepare_data(csv_path: str) -> pd.DataFrame:
    """Load CSV and derive date parts commonly used in charts"""
    df = pd.read_csv(csv_path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["quarter"] = df["date"].dt.quarter
        df["month"]=df["date"].dt.month
        df["year"]=df["date"].dt.year
    return df

def make_shema_text(df: pd.DataFrame) -> str:
    """Return a human readable schema from a DataFrame"""
    return "\n".join(f"-{c}: {dt}" for c, dt in df.types.items())

# if __name__ == "__main__":
#     get_response("what is the meaning of life ?")