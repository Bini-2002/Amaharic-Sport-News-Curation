import pandas as pd
import re
import os
import json
import time
import google.generativeai as genai

def normalize_amharic(text):
    if not isinstance(text, str):
        return ""
    replacements = {
        "ሐ": "ሀ", "ኀ": "ሀ", "ኃ": "ሀ", "ሠ": "ሰ",
        "ዐ": "አ", "ዓ": "አ", "ፀ": "ጸ", "ፅ": "ጽ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"[a-zA-Z]", "", text)
    return re.sub(r"\s+", " ", text).strip()

file_path_local = r"D:\Amaharic-Sport-News-Curation\Amharic News Dataset.csv"

if os.path.exists(file_path_local):
    df = pd.read_csv(file_path_local)
    sports_df = df[df["category"] == "ስፖርት"].head(1200).copy()
    sports_df["cleaned"] = sports_df["content"].apply(normalize_amharic)
    print(f"✅ Prepared {len(sports_df)} sports articles for curation.")
else:
    print(f"❌ ERROR: File not found at {file_path_local}!")

# Replace with your actual Gemini API Key
genai.configure(api_key="PASTE_YOUR_API_KEY_HERE")
model = genai.GenerativeModel("gemini-1.5-flash")

output_path = r"D:\Amaharic-Sport-News-Curation\amharic_sports_curated.jsonl"

def curate_batch():
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            done_count = sum(1 for _ in f)
    except FileNotFoundError:
        done_count = 0

    print(f"Resuming from row {done_count}...")

    with open(output_path, "a", encoding="utf-8") as f:
        for i, row in sports_df.iloc[done_count:].iterrows():
            prompt = f"Read this Amharic sport news: {row['cleaned'][:1200]}. Generate 1 instruction and 1 response in Amharic based on the text. Format strictly as JSON with keys 'instruction' and 'output'."
            try:
                response = model.generate_content(prompt)
                json_text = response.text.replace("```json", "").replace("```", "").strip()
                json_data = json.loads(json_text)
                
                entry = {
                    "instruction": json_data["instruction"],
                    "input": row["cleaned"],
                    "output": json_data["output"],
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

                if (done_count + i + 1) % 10 == 0:
                    print(f"Successfully curated {done_count + i + 1} rows.")
            except Exception as e:
                print(f"Error on row {done_count + i}: {e}")
                continue
            time.sleep(1.2)

# curate_batch()
