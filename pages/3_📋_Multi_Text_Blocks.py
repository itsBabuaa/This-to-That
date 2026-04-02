import streamlit as st
import io, zipfile
from utils.config import MAX_CHARS
from utils.ui import apply_styles, lined_text, output_header
from utils.sidebar import render_sidebar
from utils.translator import do_translate
from utils.history import init_history, save_history

apply_styles()
init_history()

if "blocks" not in st.session_state:
    st.session_state.blocks = [""]
if "block_results" not in st.session_state:
    st.session_state.block_results = {}

engine, api_key, model, target_lang = render_sidebar()

st.markdown("## Multi Text Blocks")

ac1, ac2, ac3 = st.columns([1, 1, 4])
with ac1:
    if st.button("+ Add Block", use_container_width=True):
        st.session_state.blocks.append("")
        st.rerun()
with ac2:
    if len(st.session_state.blocks) > 1:
        if st.button("- Remove Last", use_container_width=True):
            st.session_state.blocks.pop()
            st.rerun()

left, right = st.columns(2, gap="medium")
with left:
    st.markdown('<p class="panel-label">ORIGINAL BLOCKS</p>', unsafe_allow_html=True)
    block_tabs = st.tabs([f"Block {i+1}" for i in range(len(st.session_state.blocks))])
    for i, bt in enumerate(block_tabs):
        with bt:
            st.session_state.blocks[i] = st.text_area(
                "input", value=st.session_state.blocks[i], height=240,
                label_visibility="collapsed", key=f"block_input_{i}",
                placeholder=f"Text block {i+1}...", max_chars=MAX_CHARS)
            cc = len(st.session_state.blocks[i])
            clr = "#ff4b4b" if cc > MAX_CHARS * 0.9 else "#888"
            st.markdown(f'<p style="font-size:12px;color:{clr};text-align:right;margin-top:-10px">'
                        f'{cc:,} / {MAX_CHARS:,} chars</p>', unsafe_allow_html=True)

with right:
    if st.session_state.block_results:
        if len(st.session_state.block_results) == 1:
            output_header(target_lang.upper(), list(st.session_state.block_results.values())[0], "block")
            lined_text(list(st.session_state.block_results.values())[0], 280)
        else:
            output_header(target_lang.upper())
            tabs_out = st.tabs(list(st.session_state.block_results.keys()))
            for i, (label, trans) in enumerate(st.session_state.block_results.items()):
                with tabs_out[i]:
                    lined_text(trans, 260)
    else:
        output_header(target_lang.upper())
        lined_text("", 280)

mc1, mc2, mc3 = st.columns([1, 2, 1])
with mc2:
    blocks_translate = st.button("Translate", type="primary", use_container_width=True)
    if st.session_state.block_results:
        if len(st.session_state.block_results) == 1:
            dl_col, clr_col = st.columns(2)
            with dl_col:
                st.download_button("Download", list(st.session_state.block_results.values())[0],
                                   file_name=f"block_1_{target_lang.lower()}_translated.txt",
                                   use_container_width=True)
            with clr_col:
                if st.button("Clear", use_container_width=True, key="clr_block"):
                    st.session_state.block_results = {}
                    st.rerun()
        else:
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for label, trans in st.session_state.block_results.items():
                    zf.writestr(f"{label.lower().replace(' ', '_')}_{target_lang.lower()}_translated.txt", trans)
            dl_col, clr_col = st.columns(2)
            with dl_col:
                st.download_button("Download All (ZIP)", zip_buf.getvalue(),
                                   file_name=f"blocks_{target_lang.lower()}_translated.zip",
                                   mime="application/zip", use_container_width=True)
            with clr_col:
                if st.button("Clear", use_container_width=True, key="clr_blocks"):
                    st.session_state.block_results = {}
                    st.rerun()

if blocks_translate:
    if engine == "OpenAI" and not api_key:
        st.error("Enter your OpenAI API key in the sidebar.")
    else:
        texts = [(f"Block {i+1}", t) for i, t in enumerate(st.session_state.blocks) if t.strip()]
        if not texts:
            st.error("Add text to at least one block.")
        else:
            new_results = {}
            progress = st.progress(0, text="Translating blocks...")
            for i, (label, content) in enumerate(texts):
                try:
                    translated = do_translate(content, target_lang, engine, api_key, model)
                    new_results[label] = translated
                except Exception as e:
                    st.error(f"{label}: {e}")
                progress.progress((i + 1) / len(texts), text=f"{i + 1}/{len(texts)} done")
            if new_results:
                for label, trans in new_results.items():
                    save_history(label, trans, target_lang, engine)
                st.session_state.block_results = new_results
                st.rerun()
