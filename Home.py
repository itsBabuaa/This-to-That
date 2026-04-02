import streamlit as st
from utils.ui import apply_styles
from utils.sidebar import render_sidebar
from utils.history import init_history

st.set_page_config(page_title="Home - This-to-That", layout="wide", initial_sidebar_state="expanded")
apply_styles()
init_history()

if "paste_result" not in st.session_state:
    st.session_state.paste_result = ""
if "paste_dl_name" not in st.session_state:
    st.session_state.paste_dl_name = ""

render_sidebar()

# --- Hero ---
st.markdown("""
<div style="text-align:center;padding:20px 0 10px 0;">
    <h1 style="font-size:36px;margin-bottom:4px;">This-to-That</h1>
    <p style="color:#888;font-size:16px;margin-top:0;">
        Translate any text from <em>this</em> language to <em>that</em> language.
        Paste, upload, or point to a folder.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- Feature cards (clickable) ---
c1, c2 = st.columns(2, gap="medium")
c3, c4 = st.columns(2, gap="medium")

with c1:
    with st.container(border=True):
        st.subheader("📝 Paste Text")
        st.write("Paste any text and get an instant side-by-side translation with auto language detection.")
        st.page_link("pages/1_📝_Paste_Text.py", label="Go to Paste Text", use_container_width=True)

with c2:
    with st.container(border=True):
        st.subheader("📁 Upload Files")
        st.write("Upload one or multiple files. Supports txt, json, csv, md, xml, html, yml and more.")
        st.page_link("pages/2_📁_Upload_Files.py", label="Go to Upload Files", use_container_width=True)

with c3:
    with st.container(border=True):
        st.subheader("📋 Multi Text Blocks")
        st.write("Add multiple text blocks and translate them all at once. Great for batch snippets.")
        st.page_link("pages/3_📋_Multi_Text_Blocks.py", label="Go to Multi Blocks", use_container_width=True)

with c4:
    with st.container(border=True):
        st.subheader("📂 Batch Folder")
        st.write("Point to a local folder and translate every supported file. Output saved automatically.")
        st.page_link("pages/4_📂_Batch_Folder.py", label="Go to Batch Folder", use_container_width=True)

st.markdown("")
st.divider()

# --- Quick stats ---
s1, s2, s3 = st.columns(3)
with s1:
    st.metric("🔧 Engines", "2", help="Google Translate (Free) + OpenAI GPT")
with s2:
    st.metric("🌍 Languages", "20")
with s3:
    history_count = len(st.session_state.get("history", []))
    st.metric("📊 Translations", str(history_count))

st.markdown("")
st.caption("Select a page from the sidebar to get started.")
