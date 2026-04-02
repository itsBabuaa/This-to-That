import streamlit as st
from utils.config import MAX_CHARS
from utils.ui import apply_styles, lined_text, output_header, char_and_detect
from utils.sidebar import render_sidebar
from utils.translator import do_translate
from utils.history import init_history, save_history

apply_styles()
init_history()

if "paste_result" not in st.session_state:
    st.session_state.paste_result = ""
if "paste_dl_name" not in st.session_state:
    st.session_state.paste_dl_name = ""

engine, api_key, model, target_lang = render_sidebar()

st.markdown("## Paste Text")

left, right = st.columns(2, gap="medium")
with left:
    st.markdown('<p class="panel-label">ORIGINAL</p>', unsafe_allow_html=True)
    source_text = st.text_area("input", height=280, label_visibility="collapsed",
                               placeholder="Paste any text here...", key="input_paste",
                               max_chars=MAX_CHARS)
    char_and_detect(source_text, MAX_CHARS)

with right:
    if st.session_state.paste_result:
        output_header(target_lang.upper(), st.session_state.paste_result, "paste")
        lined_text(st.session_state.paste_result, 280)
    else:
        output_header(target_lang.upper())
        lined_text("", 280)

bc1, bc2, bc3 = st.columns([1, 2, 1])
with bc2:
    paste_translate = st.button("Translate", type="primary", use_container_width=True)
    if st.session_state.paste_result:
        dl_col, clr_col = st.columns(2)
        with dl_col:
            st.download_button("Download", st.session_state.paste_result,
                               file_name=st.session_state.paste_dl_name or
                                         f"pasted_text_{target_lang.lower()}_translated.txt",
                               use_container_width=True)
        with clr_col:
            if st.button("Clear", use_container_width=True, key="clr_paste"):
                st.session_state.paste_result = ""
                st.rerun()

if paste_translate:
    if engine == "OpenAI" and not api_key:
        st.error("Enter your OpenAI API key in the sidebar.")
    elif not source_text.strip():
        st.error("Paste some text first.")
    else:
        with st.spinner("Translating..."):
            try:
                result = do_translate(source_text, target_lang, engine, api_key, model)
                st.session_state.paste_result = result
                st.session_state.paste_dl_name = f"pasted_text_{target_lang.lower()}_translated.txt"
                save_history(source_text, result, target_lang, engine)
                st.rerun()
            except Exception as e:
                st.error(f"{e}")
