### Amharic Sports Curated Dataset

NAME                             ID                                        
1.Bemnet Grum               ugr/25906/14              
2.Biniyam Getachew          ugr/25297/14              
3.Yonas Esubalew            ugr/26605/14                   
4.Bitaniya Zeray            ugr/25812/14              
5.Mihret Abebe              ugr/25394/14                     
6.Kalkidan Yalew            ugr/25325/14

Contents
- amharic_sports_curated.jsonl — 1200 line-delimited JSON entries (instruction/input/output)
- amharic_sports_curated.json — full JSON array of 1200 entries

Overview
This dataset contains 1200 curated Amharic sports-news examples in an instruction-finetuning format. Each entry has three fields:
- `instruction`: a clear task prompt in Amharic
- `input`: a sports news article (guaranteed to be at least 5 sentences)
- `output`: a model-style response (summary, extraction, or analysis)

Usage (Python)

```python
import json

# Read JSONL
with open('amharic_sports_curated.jsonl', 'r', encoding='utf-8') as f:
    examples = [json.loads(line) for line in f]

# Read JSON
with open('amharic_sports_curated.json', 'r', encoding='utf-8') as f:
    examples_array = json.load(f)
```

Notes
- Files are UTF-8 encoded. Verify display fonts for proper Amharic rendering.
- The dataset was synthetically generated and intended for fine-tuning or evaluation; review entries before public release.

If you want, I can:
- Compress the dataset into a single ZIP for download
- Prepare a Git commit and push
- Run additional validation checks (encoding, token counts, sentence-length stats)
