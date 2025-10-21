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

# === Standard Library ===

from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
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
    response_code = completion.choices[0].message.content
    print(response_code)
    return response_code


def image_openai_call(prompt: str, media_type: str, b64: str) -> str:
    image_url = f"data:{media_type};base64,{b64}"
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

    response_imag = completion.choices[0].message.content
    print(response_imag)
    return response_imag




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


def ensure_execute_python_tags(text: str) -> str:
    """Normalize code to be wrapped in <execute_python>...</execute_python>."""
    text = text.strip()
    # Strip ```python fences if present
    text = re.sub(r"^```(?:python)?\s*|\s*```$", "", text).strip()
    if "<execute_python>" not in text:
        text = f"<execute_python>\n{text}\n</execute_python>"
    return text
# if __name__ == "__main__":
#     get_response("what is the meaning of life ?")

import base64
from IPython.display import HTML, display
import pandas as pd
from typing import Any  


def encode_image_b64(path: str) -> tuple[str, str]:
    """Return (media_type, base64_str) for an image file path."""
    mime, _ = mimetypes.guess_type(path)
    media_type = mime or "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return media_type, b64


def print_html(content: any, title: str | None = None, is_image: bool = False):
    """
    Pretty-print inside a styled card.
    - If is_image=True and content is a string: treat as image path/URL and render <img>.
    - If content is a pandas DataFrame/Series: render as an HTML table.
    - Otherwise (strings/others): show as code/text in <pre><code>.
    """
    try:
        from html import escape as _escape
    except ImportError:
        def _escape(x): return x

    def image_to_base64(image_path: str) -> str:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    # Render content
    if is_image and isinstance(content, str):
        b64 = image_to_base64(content)
        rendered = f'<img src="data:image/png;base64,{b64}" alt="Image" style="max-width:100%; height:auto; border-radius:8px;">'
    elif isinstance(content, pd.DataFrame):
        rendered = content.to_html(
            classes="pretty-table", index=False, border=0, escape=False)
    elif isinstance(content, pd.Series):
        rendered = content.to_frame().to_html(
            classes="pretty-table", border=0, escape=False)
    elif isinstance(content, str):
        rendered = f"<pre><code>{_escape(content)}</code></pre>"
    else:
        rendered = f"<pre><code>{_escape(str(content))}</code></pre>"

    css = """
    <style>
    .pretty-card{
      font-family: ui-sans-serif, system-ui;
      border: 2px solid transparent;
      border-radius: 14px;
      padding: 14px 16px;
      margin: 10px 0;
      background: linear-gradient(#fff, #fff) padding-box,
                  linear-gradient(135deg, #3b82f6, #9333ea) border-box;
      color: #111;
      box-shadow: 0 4px 12px rgba(0,0,0,.08);
    }
    .pretty-title{
      font-weight:700;
      margin-bottom:8px;
      font-size:14px;
      color:#111;
    }
    /* 🔒 Only affects INSIDE the card */
    .pretty-card pre, 
    .pretty-card code {
      background: #f3f4f6;
      color: #111;
      padding: 8px;
      border-radius: 8px;
      display: block;
      overflow-x: auto;
      font-size: 13px;
      white-space: pre-wrap;
    }
    .pretty-card img { max-width: 100%; height: auto; border-radius: 8px; }
    .pretty-card table.pretty-table {
      border-collapse: collapse;
      width: 100%;
      font-size: 13px;
      color: #111;
    }
    .pretty-card table.pretty-table th, 
    .pretty-card table.pretty-table td {
      border: 1px solid #e5e7eb;
      padding: 6px 8px;
      text-align: left;
    }
    .pretty-card table.pretty-table th { background: #f9fafb; font-weight: 600; }
    </style>
    """

    title_html = f'<div class="pretty-title">{title}</div>' if title else ""
    card = f'<div class="pretty-card">{title_html}{rendered}</div>'
    display(HTML(css + card))
