import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import zipfile
import io

load_dotenv()

LANGUAGES = [
    "English", "Spanish", "French", "German", "Italian", "Portuguese",
    "Chinese (Simplified)", "Chinese (Traditional)", "Japanese", "Korean",
    "Arabic", "Hindi", "Russian", "Turkish", "Dutch", "Polish", "Swedish",
    "Thai", "Vietnamese", "Indonesian",
]

st.set_page_config(page_title="This-to-That Translator", layout="wide", page_icon="🔄")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 0; max-width: 1200px; }
    div[data-testid="stTextArea"] textarea {
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 13px;
        line-height: 1.5;
    }
    .panel-label {
        font-size: 13px; font-weight: 600; margin-bottom: 2px;
        color: #aaa; text-transform: uppercase; letter-spacing: 1px;
    }
    .app-subtitle {
        font-size: 13px; color: #888; margin: -10px 0 8px 0;
    }
    h2 { margin-bottom: 0 !important; padding-bottom: 0 !important; font-size: 22px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🔄 This-to-That")
st.markdown('<p class="app-subtitle">Translate any text from this language to that language.</p>',
            unsafe_allow_html=True)

# --- Session state init ---
if "translation_result" not in st.session_state:
    st.session_state.translation_result = None  # str or dict
if "translation_lang" not in st.session_state:
    st.session_state.translation_lang = ""
if "translation_source" not in st.session_state:
    st.session_state.translation_source = None  # str or dict
if "dl_name" not in st.session_state:
    st.session_state.dl_name = ""
if "multi_texts" not in st.session_state:
    st.session_state.multi_texts = [""]  # list of text blocks
if "input_mode" not in st.session_state:
    st.session_state.input_mode = "single"

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🔄 This-to-That")
    api_key = st.text_input("OpenAI API Key", type="password",
                            value=os.getenv("OPENAI_API_KEY", ""))
    target_lang = st.selectbox("Translate to", LANGUAGES)
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
    st.divider()
    if st.button("🗑️ Clear results", use_container_width=True):
        st.session_state.translation_result = None
        st.session_state.translation_source = None
        st.session_state.dl_name = ""
        st.rerun()


def read_file(f) -> str:
    f.seek(0)
    try:
        return f.read().decode("utf-8")
    except UnicodeDecodeError:
        f.seek(0)
        return f.read().decode("latin-1")


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


def translate(text: str, lang: str, key: str, mdl: str) -> str:
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

# --- Determine source text ---
source_text = ""
file_sources: list[tuple[str, str]] = []

# --- Input mode selector ---
input_mode = st.radio("Input mode", ["✏️ Single Text", "📝 Multi Text", "📁 Files"],
                      horizontal=True, label_visibility="collapsed",
                      index=["single", "multi", "files"].index(st.session_state.input_mode),
                      key="mode_radio")

if input_mode == "📁 Files":
    st.session_state.input_mode = "files"
elif input_mode == "📝 Multi Text":
    st.session_state.input_mode = "multi"
else:
    st.session_state.input_mode = "single"

# --- Main two-column layout ---
left, right = st.columns(2, gap="medium")

with left:
    st.markdown('<p class="panel-label">📄 ORIGINAL</p>', unsafe_allow_html=True)

    if st.session_state.input_mode == "files":
        uploaded_files = st.file_uploader("Upload file(s)",
                                          accept_multiple_files=True, key="files",
                                          help="txt, json, csv, md, xml, etc.")
        if uploaded_files:
            for f in uploaded_files:
                file_sources.append((f.name, read_file(f)))
            if len(file_sources) == 1:
                source_text = file_sources[0][1]
                st.text_area("input", source_text, height=220, label_visibility="collapsed",
                             key="input_single_file")
            else:
                tabs = st.tabs([name for name, _ in file_sources])
                for i, tab in enumerate(tabs):
                    with tab:
                        st.text_area("input", file_sources[i][1], height=220,
                                     label_visibility="collapsed", key=f"input_file_{i}")

    elif st.session_state.input_mode == "multi":
        # Dynamic multi-text blocks
        for i in range(len(st.session_state.multi_texts)):
            st.session_state.multi_texts[i] = st.text_area(
                f"Text block {i + 1}", value=st.session_state.multi_texts[i],
                height=120, key=f"multi_input_{i}",
                placeholder=f"Text block {i + 1}...")
        mc1, mc2 = st.columns(2)
        with mc1:
            if st.button("➕ Add block", use_container_width=True):
                st.session_state.multi_texts.append("")
                st.rerun()
        with mc2:
            if len(st.session_state.multi_texts) > 1:
                if st.button("➖ Remove last", use_container_width=True):
                    st.session_state.multi_texts.pop()
                    st.rerun()

    else:
        source_text = st.text_area("input", height=280, label_visibility="collapsed",
                                   placeholder="Paste any text here...", key="input_paste")

with right:
    st.markdown(f'<p class="panel-label">🌍 {target_lang.upper()}</p>', unsafe_allow_html=True)
    # Show persisted result
    if st.session_state.translation_result and isinstance(st.session_state.translation_result, dict):
        tabs_out = st.tabs(list(st.session_state.translation_result.keys()))
        for i, (label, trans) in enumerate(st.session_state.translation_result.items()):
            with tabs_out[i]:
                st.text_area("out", trans, height=280,
                             label_visibility="collapsed", key=f"out_persist_{i}")
    elif st.session_state.translation_result and isinstance(st.session_state.translation_result, str):
        st.text_area("output", value=st.session_state.translation_result, height=280,
                     label_visibility="collapsed", key="output_persisted")
    else:
        st.text_area("output", value="", height=280,
                     label_visibility="collapsed", disabled=True,
                     key="output_default",
                     placeholder="Translation will appear here...")

# --- Translate button + download ---
btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
with btn_col2:
    do_translate = st.button("🔄 Translate", type="primary", use_container_width=True)
    # Show download if we have results
    if st.session_state.translation_result:
        if isinstance(st.session_state.translation_result, dict):
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname, trans in st.session_state.translation_result.items():
                    name, ext = os.path.splitext(fname)
                    zf.writestr(f"{name}_{st.session_state.translation_lang}_translated{ext}", trans)
            st.download_button("⬇️ Download All (ZIP)", zip_buf.getvalue(),
                               file_name=f"translations_{st.session_state.translation_lang}_translated.zip",
                               mime="application/zip", use_container_width=True)
        else:
            st.download_button("⬇️ Download", st.session_state.translation_result,
                               file_name=st.session_state.dl_name,
                               use_container_width=True)

# --- Handle translation ---
if do_translate:
    if not api_key:
        st.error("⚠️ Enter your OpenAI API key in the sidebar.")
    elif not source_text.strip() and not file_sources and st.session_state.input_mode != "multi":
        st.error("⚠️ Paste text or upload file(s) first.")
    elif st.session_state.input_mode == "multi" and not any(t.strip() for t in st.session_state.multi_texts):
        st.error("⚠️ Add some text to at least one block.")
    else:
        # Multi-text blocks
        if st.session_state.input_mode == "multi":
            texts = [(f"Block {i+1}", t) for i, t in enumerate(st.session_state.multi_texts) if t.strip()]
            results: dict[str, str] = {}
            progress = st.progress(0, text="Translating...")
            for i, (label, content) in enumerate(texts):
                try:
                    translated = translate(content, target_lang, api_key, model)
                    results[label] = translated
                except Exception as e:
                    st.error(f"❌ {label}: {e}")
                progress.progress((i + 1) / len(texts),
                                  text=f"{i + 1}/{len(texts)} done")
            st.session_state.translation_result = results
            st.session_state.translation_lang = target_lang.lower()
            st.rerun()

        # Multi-file
        elif file_sources and len(file_sources) > 1:
            results: dict[str, str] = {}
            progress = st.progress(0, text="Translating...")
            for i, (fname, content) in enumerate(file_sources):
                try:
                    translated = translate(content, target_lang, api_key, model)
                    results[fname] = translated
                except Exception as e:
                    st.error(f"❌ {fname}: {e}")
                progress.progress((i + 1) / len(file_sources),
                                  text=f"{i + 1}/{len(file_sources)} done")
            st.session_state.translation_result = results
            st.session_state.translation_lang = target_lang.lower()
            st.rerun()

        # Single text or single file
        else:
            text_to_translate = file_sources[0][1] if file_sources else source_text
            orig_name = file_sources[0][0] if file_sources else None
            with st.spinner("Translating..."):
                try:
                    result = translate(text_to_translate, target_lang, api_key, model)
                    st.session_state.translation_result = result
                    st.session_state.translation_lang = target_lang.lower()
                    if orig_name:
                        name, ext = os.path.splitext(orig_name)
                        st.session_state.dl_name = f"{name}_{target_lang.lower()}_translated{ext}"
                    else:
                        st.session_state.dl_name = f"pasted_text_{target_lang.lower()}_translated.txt"
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")
