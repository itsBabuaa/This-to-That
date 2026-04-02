import httpx
from openai import OpenAI
from deep_translator import GoogleTranslator
from utils.config import LANG_CODES

SYSTEM_PROMPT = """You are a precise translator. The user will give you text that contains a MIX of languages.

YOUR TASK:
- Find every word, phrase, or sentence that is NOT in {lang}.
- Translate those parts into {lang}.
- Keep all parts already in {lang} EXACTLY as they are, character for character.
- Keep ALL formatting, whitespace, line breaks, indentation, JSON structure, code, keys, tags unchanged.
- Output ONLY the resulting text. No commentary, no notes, no explanations.

EXAMPLE (target: English):
Input:  "name": "こんにちは世界"
Output: "name": "Hello World"

Input:  Hello, 今日はいい天気ですね。Let's go.
Output: Hello, the weather is nice today. Let's go.

Be accurate. Do not skip any foreign text. Do not alter any {lang} text."""


def translate_openai(text: str, lang: str, key: str, mdl: str) -> str:
    client = OpenAI(api_key=key)
    MAX_CHUNK = 10_000
    chunks = [text[i:i + MAX_CHUNK] for i in range(0, len(text), MAX_CHUNK)]
    parts = []
    for chunk in chunks:
        resp = client.chat.completions.create(
            model=mdl,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.format(lang=lang)},
                {"role": "user", "content": chunk},
            ],
            temperature=0.1,
        )
        parts.append(resp.choices[0].message.content)
    return "\n".join(parts)


def translate_google(text: str, lang: str) -> str:
    code = LANG_CODES.get(lang, "en")
    MAX_CHUNK = 2000
    chunks = [text[i:i + MAX_CHUNK] for i in range(0, len(text), MAX_CHUNK)]
    parts = []
    for chunk in chunks:
        try:
            translated = GoogleTranslator(source="auto", target=code).translate(chunk)
            parts.append(translated if translated else chunk)
        except Exception:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {"client": "gtx", "sl": "auto", "tl": code, "dt": "t"}
            data = {"q": chunk}
            try:
                resp = httpx.post(url, params=params, data=data, verify=False, timeout=30)
                resp.raise_for_status()
                result_data = resp.json()
                translated = "".join(seg[0] for seg in result_data[0] if seg[0])
                parts.append(translated)
            except Exception as e2:
                parts.append(f"[Translation error: {e2}]\n{chunk}")
    return "\n".join(parts)


def do_translate(text: str, lang: str, eng: str, key: str, mdl: str) -> str:
    if eng == "OpenAI":
        return translate_openai(text, lang, key, mdl)
    else:
        return translate_google(text, lang)
