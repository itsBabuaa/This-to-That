import streamlit as st
import os, io, zipfile
from utils.ui import apply_styles, lined_text, output_header, char_and_detect, read_file
from utils.sidebar import render_sidebar
from utils.translator import do_translate
from utils.history import init_history, save_history

st.set_page_config(page_title="Upload Files - This-to-That", layout="wide")
apply_styles()
init_history()

if "file_results" not in st.session_state:
    st.session_state.file_results = {}

engine, api_key, model, target_lang = render_sidebar()

st.markdown("## Upload File(s)")

uploaded_files = st.file_uploader("Upload one or more files (txt, json, csv, md, xml, etc.)",
                                  accept_multiple_files=True, key="upload_files")
file_sources = []
if uploaded_files:
    for f in uploaded_files:
        file_sources.append((f.name, read_file(f)))

left, right = st.columns(2, gap="medium")
with left:
    st.markdown('<p class="panel-label">ORIGINAL</p>', unsafe_allow_html=True)
    if file_sources:
        if len(file_sources) == 1:
            st.text_area("input", file_sources[0][1], height=280,
                         label_visibility="collapsed", key="input_file_single")
            char_and_detect(file_sources[0][1], 50_000)
        else:
            tabs_in = st.tabs([name for name, _ in file_sources])
            for i, tab in enumerate(tabs_in):
                with tab:
                    st.text_area("input", file_sources[i][1], height=260,
                                 label_visibility="collapsed", key=f"input_file_{i}")
                    char_and_detect(file_sources[i][1], 50_000)
    else:
        st.text_area("input", "", height=280, label_visibility="collapsed",
                     disabled=True, key="input_file_empty",
                     placeholder="Upload file(s) to see content...")

with right:
    if st.session_state.file_results:
        if len(st.session_state.file_results) == 1:
            output_header(target_lang.upper(), list(st.session_state.file_results.values())[0], "file")
            lined_text(list(st.session_state.file_results.values())[0], 280)
        else:
            output_header(target_lang.upper())
            tabs_out = st.tabs(list(st.session_state.file_results.keys()))
            for i, (fname, trans) in enumerate(st.session_state.file_results.items()):
                with tabs_out[i]:
                    lined_text(trans, 260)
    else:
        output_header(target_lang.upper())
        lined_text("", 280)

fc1, fc2, fc3 = st.columns([1, 2, 1])
with fc2:
    file_translate = st.button("Translate", type="primary", use_container_width=True)
    if st.session_state.file_results:
        if len(st.session_state.file_results) == 1:
            fname = list(st.session_state.file_results.keys())[0]
            trans = list(st.session_state.file_results.values())[0]
            name, ext = os.path.splitext(fname)
            dl_col, clr_col = st.columns(2)
            with dl_col:
                st.download_button("Download", trans,
                                   file_name=f"{name}_{target_lang.lower()}_translated{ext}",
                                   use_container_width=True)
            with clr_col:
                if st.button("Clear", use_container_width=True, key="clr_file"):
                    st.session_state.file_results = {}
                    st.rerun()
        else:
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname, trans in st.session_state.file_results.items():
                    name, ext = os.path.splitext(fname)
                    zf.writestr(f"{name}_{target_lang.lower()}_translated{ext}", trans)
            dl_col, clr_col = st.columns(2)
            with dl_col:
                st.download_button("Download All (ZIP)", zip_buf.getvalue(),
                                   file_name=f"translations_{target_lang.lower()}_translated.zip",
                                   mime="application/zip", use_container_width=True)
            with clr_col:
                if st.button("Clear", use_container_width=True, key="clr_files"):
                    st.session_state.file_results = {}
                    st.rerun()

if file_translate:
    if engine == "OpenAI" and not api_key:
        st.error("Enter your OpenAI API key in the sidebar.")
    elif not file_sources:
        st.error("Upload file(s) first.")
    else:
        new_results = {}
        if len(file_sources) == 1:
            with st.spinner("Translating..."):
                try:
                    result = do_translate(file_sources[0][1], target_lang, engine, api_key, model)
                    new_results[file_sources[0][0]] = result
                except Exception as e:
                    st.error(f"{e}")
        else:
            progress = st.progress(0, text="Translating...")
            for i, (fname, content) in enumerate(file_sources):
                try:
                    translated = do_translate(content, target_lang, engine, api_key, model)
                    new_results[fname] = translated
                except Exception as e:
                    st.error(f"{fname}: {e}")
                progress.progress((i + 1) / len(file_sources), text=f"{i + 1}/{len(file_sources)} done")
        if new_results:
            for fname, trans in new_results.items():
                save_history(fname, trans, target_lang, engine)
            st.session_state.file_results = new_results
            st.rerun()
