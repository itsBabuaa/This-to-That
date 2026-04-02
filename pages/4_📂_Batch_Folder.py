import streamlit as st
import os
from utils.config import SUPPORTED_EXTS
from utils.ui import apply_styles, lined_text, output_header, detect_language
from utils.sidebar import render_sidebar
from utils.translator import do_translate
from utils.history import init_history, save_history

apply_styles()
init_history()

if "folder_results" not in st.session_state:
    st.session_state.folder_results = {}
if "folder_path_used" not in st.session_state:
    st.session_state.folder_path_used = ""

engine, api_key, model, target_lang = render_sidebar()

st.markdown("## Batch Folder")
st.caption("Point to a local folder. All supported text files will be translated and saved.")

folder_path = st.text_input("Folder path", placeholder=r"C:\Users\you\Documents\my_files",
                            key="folder_input")

files_found = []
if folder_path and os.path.isdir(folder_path):
    for fname in sorted(os.listdir(folder_path)):
        fpath = os.path.join(folder_path, fname)
        if os.path.isfile(fpath) and os.path.splitext(fname)[1].lower() in SUPPORTED_EXTS:
            files_found.append((fname, fpath))
    st.info(f"Found {len(files_found)} file(s)")
    with st.expander("Show files", expanded=False):
        for fname, _ in files_found[:20]:
            st.caption(f"  {fname}")
        if len(files_found) > 20:
            st.caption(f"  ... and {len(files_found) - 20} more")
elif folder_path:
    st.error("Folder not found. Check the path.")

if st.session_state.folder_results and st.session_state.folder_path_used:
    st.success(f"Saved to: {st.session_state.folder_path_used}_translated")

# --- Translate button (before preview) ---
f1, f2, f3 = st.columns([1, 2, 1])
with f2:
    folder_translate = st.button("Translate Folder", type="primary", use_container_width=True)
    if st.session_state.folder_results:
        if st.button("Clear", use_container_width=True, key="clr_folder"):
            st.session_state.folder_results = {}
            st.session_state.folder_path_used = ""
            st.rerun()

left, right = st.columns(2, gap="medium")
with left:
    st.markdown('<p class="panel-label">ORIGINAL (PREVIEW)</p>', unsafe_allow_html=True)
    if files_found:
        preview_tabs = st.tabs([f[0] for f in files_found[:10]])
        for i, (fname, fpath) in enumerate(files_found[:10]):
            with preview_tabs[i]:
                try:
                    with open(fpath, "r", encoding="utf-8", errors="replace") as fh:
                        preview = fh.read()
                    lined_text(preview, 200)
                    det = detect_language(preview)
                    st.markdown(f'<p style="font-size:12px;color:#6c9;margin-top:-4px;text-align:left">'
                                f'Detected: {det}</p>', unsafe_allow_html=True)
                except Exception:
                    st.caption("Could not read file")
    else:
        lined_text("", 220)

with right:
    if st.session_state.folder_results:
        output_header(f"{target_lang.upper()} (OUTPUT)",
                      "\n\n".join(st.session_state.folder_results.values()), "folder")
        tabs_out = st.tabs(list(st.session_state.folder_results.keys())[:10])
        for i, (fn, content) in enumerate(list(st.session_state.folder_results.items())[:10]):
            with tabs_out[i]:
                lined_text(content, 180)
    else:
        st.markdown(f'<p class="panel-label">{target_lang.upper()} (OUTPUT)</p>', unsafe_allow_html=True)
        lined_text("", 220)

if folder_translate:
    if engine == "OpenAI" and not api_key:
        st.error("Enter your OpenAI API key in the sidebar.")
    elif not files_found:
        st.error("No supported files found in folder.")
    else:
        out_dir = folder_path.rstrip("/\\") + "_translated"
        os.makedirs(out_dir, exist_ok=True)
        folder_res = {}
        progress = st.progress(0, text="Translating folder...")
        for i, (fname, fpath) in enumerate(files_found):
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as fh:
                    content = fh.read()
                translated = do_translate(content, target_lang, engine, api_key, model)
                name, ext = os.path.splitext(fname)
                out_name = f"{name}_{target_lang.lower()}_translated{ext}"
                with open(os.path.join(out_dir, out_name), "w", encoding="utf-8") as fh:
                    fh.write(translated)
                folder_res[fname] = translated
                save_history(fname, translated, target_lang, engine)
            except Exception as e:
                st.error(f"{fname}: {e}")
            progress.progress((i + 1) / len(files_found), text=f"{i + 1}/{len(files_found)} done")
        if folder_res:
            st.session_state.folder_results = folder_res
            st.session_state.folder_path_used = folder_path
            st.rerun()
