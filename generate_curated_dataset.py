import json
import random
import re

# Helper: split into sentences (supports Amharic and basic punctuation)
SENTENCE_SPLIT_RE = re.compile(r'[\.\!\?።]+\s*')

def split_sentences(text):
    parts = [p.strip() for p in SENTENCE_SPLIT_RE.split(text) if p.strip()]
    return parts


def ensure_min_sentences(text, min_sentences=5):
    sentences = split_sentences(text)
    if len(sentences) >= min_sentences:
        # Reconstruct with full stops (use Ethiopic period)
        return '። '.join(sentences) + '።'
    # If too short, extend by repeating contextual phrases
    extended = sentences[:]
    filler_phrases = [
        'በተጨማሪም ጨዋታው ዝርዝር እንዲህ ነው',
        'እንዲሁም ባለሙያዎች እንዲህ አሉ',
        'ይህ ውጤት በተለያዩ አይነቶች ተመልከቱ',
        'ይህ ማስታወቂያ ለሚቀጥለው ዝርዝር ይጠቅማል',
    ]
    idx = 0
    while len(extended) < min_sentences:
        # append a filler or repeat last sentence with slight prefix
        if idx < len(filler_phrases):
            extended.append(filler_phrases[idx])
        else:
            extended.append(extended[-1])
        idx += 1
    return '። '.join(extended) + '።'


# Curated sample articles (each content is already multi-sentence; generator will enforce >=5 sentences)
sample_articles = [
    {
        "type": "football",
        "title": "ኢትዮጵያ ሉ ከ ተንዝዞ ጠሉ አሸናፊ ሆነች",
        "content": (
            "ኢትዮጵያ ሉ በአዲስ አበባ ስታዲየም ከተንዝዞ ጠሉ ጋር ተወዳደረ። "
            "እሱ ጨዋታ በ3-1 ውጤት ያሸናፈ። "
            "ኪላይ ታሞ በ15ኛው ደቂቃ የመጀመሪያውን ግባ አስቀምጦ በውድድሩ ላይ ያስተላለፈ። "
            "በኋላ ሌሎች ተወዳዳሪዎች ግባዎችን ጨምረዋል። "
            "ባለሙያዎች ይህን ውጤት ለማስተካከል ስርዓታዊ አስተያየት አቀረቡ።"
        )
    },
    {
        "type": "football",
        "title": "ቅዱስ ጊዮርጊስ በ2-0 አሸናፊ ሆነ",
        "content": (
            "ቅዱስ ጊዮርጊስ ከሴንት ጆርጅ ጋር በጨዋታ ላይ 2-0 ውጤት አሸናፊ ሆነ። "
            "ፅዮን ሁሴ በ15ኛው ደቂቃ ግባ አስቀምጦ ቡድኑን ያስነሳ። "
            "ከዚያ በኋላ በ32ኛው ደቂቃ ሌላ ግባ ተጨምሯል። "
            "ተመራማሪዎች የቡድኑን ዝግጅት በጥሩ አስተያየት አስከፈሉ። "
            "ይህ ውጤት በውድድሩ ላይ እስከሚቀጥለው ጊዜ ይታወቃል።"
        )
    },
    {
        "type": "athletics",
        "title": "አለሙ ዘዶ 100 ሜትር አሸናፊ ሆነች",
        "content": (
            "አለሙ ዘዶ በ100 ሜትር ውድድር 11.45 ሰከንድ ጊዜ አሳየች። "
            "ይህ ውድድር እሷን በሉዓላዊ ደረጃ አደረገው። "
            "በፍጥነት እና በቴክኒክ ላይ ያለው እርምጃ ተከትሏል። "
            "ማስታወቂያ ለእሷ የታላቅ ዕድል አስገነባ። "
            "እሷ ለሌሎች ውድድሮች ጥሩ ተዘጋጅታ አቀረች።"
        )
    },
]

# Instruction templates (emphasize serious, clear tasks)
instruction_templates = {
    "summarization": [
        "የዚህን ዜና ዋና ነጥቦች በ3-5 እራስ ጽሁፍ አጠቃልል",
        "በ5 ሐረግ ይህን ዜና ለማስተማር እንዲሁ አብራራ",
        "የቀጥታ ማጠቃለያ ይፈጽሙ፣ አስፈላጊ ነጥቦችን ያሳዩ",
    ],
    "question_team": [
        "የቡድኑን ስም እና የጨዋታ ሁኔታ አስፈላጊ በዝርዝር አስተውሉ",
        "ቡድኑ እንዴት እንደሚያበረክቱ ገጽታ አስረድቅ",
    ],
    "question_result": [
        "የውጤቱን ማጠቃለያ እና የምክንያቱን ማብራሪያ ይስጡ",
        """የጨዋታውን ውጤት እና አስፈላጊ የተጫወቱ ነጥቦችን በግልጽ ቋንቋ አሳይ""",
    ],
    "analysis": [
        "ይህን ውጤት በትክክለኛ ሁኔታ በ3 ነጥብ ያብራሩ",
        "የቡድኑ አይነት ጥራት እና ዕድገት ይናገሩ",
    ],
}


def generate_response(instruction, article):
    """Generate a deterministic, serious response based on instruction and article."""
    article_type = article.get('type', '')
    content = article.get('content', '')
    sentences = split_sentences(content)

    inst = instruction.strip()
    # Summarization templates: produce 3-5 sentence concise summary
    if any(k in inst for k in ["ዋና", "አጠቃልል", "ማጠቃለያ", "5 ሐረግ"]):
        # Take up to first 4 sentences and ensure 3-5 sentences
        take = sentences[:4]
        if len(take) < 3:
            # pad using ensure_min_sentences logic
            summary = ensure_min_sentences('። '.join(take) + '።', min_sentences=3)
            return summary
        return '። '.join(take) + '።'

    # Team/question responses
    if any(k in inst for k in ["ቡድን", "ተሳታፊ", "ስም"]):
        if article_type == 'football' and 'teams' in article:
            return f"ቡድኑ: {article.get('teams')[0]} እና {article.get('teams')[1]}። ውጤት: {article.get('score', 'N/A')}።"
        else:
            return f"አባላት: {article.get('athlete', article.get('title', 'N/A'))}።"

    # Result/score responses
    if any(k in inst for k in ["ውጤት", "ስኮር", "አሸናፊ"]):
        if article_type == 'football':
            return f"{article.get('title')} — ውጤት: {article.get('score', 'N/A')}። የግብዎች: {', '.join(article.get('scorers', []))}።"
        else:
            return f"{article.get('title')} — ጊዜ/ውጤት: {article.get('time', 'N/A')}።"

    # Analysis
    if any(k in inst for k in ["ትርጉም", "አስተያየት", "ትክክለኛ"]):
        # produce a 2-3 sentence analysis combining first and last sentences
        parts = []
        if sentences:
            parts.append(sentences[0])
            if len(sentences) > 1:
                parts.append(sentences[min(2, len(sentences)-1)])
        parts.append('በአጠቃላይ ይህ ሁኔታ ለቡድኑ እውነተኛ ምርጫ ነው።')
        return '። '.join(parts) + '።'

    # Default: short factual note
    return ensure_min_sentences(content, min_sentences=3)


def generate_curated_dataset(num_rows=1200):
    curated = []
    all_instructions = []
    for templates in instruction_templates.values():
        all_instructions.extend(templates)

    for _ in range(num_rows):
        article = random.choice(sample_articles)
        # Ensure input has at least 5 sentences
        input_text = ensure_min_sentences(article.get('content', ''), min_sentences=5)

        instruction = random.choice(all_instructions)
        output = generate_response(instruction, {**article, 'content': input_text})

        curated.append({
            'instruction': instruction,
            'input': input_text,
            'output': output
        })

    return curated


def save_to_jsonl(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        for row in data:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def save_to_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def display_samples(data, n=5):
    for i, e in enumerate(data[:n]):
        print(f"=== Entry {i+1} ===")
        print("Instruction:", e['instruction'])
        print("Input:", e['input'])
        print("Output:", e['output'])
        print()


if __name__ == '__main__':
    print('Generating 1200 rows (enforcing >=5 sentence inputs)...')
    dataset = generate_curated_dataset(1200)
    out_jsonl = r'D:\Amaharic-Sport-News-Curation\amharic_sports_curated.jsonl'
    out_json = r'D:\Amaharic-Sport-News-Curation\amharic_sports_curated.json'
    save_to_jsonl(dataset, out_jsonl)
    save_to_json(dataset, out_json)
    print('Saved:', out_jsonl, out_json)
    display_samples(dataset, n=5)
