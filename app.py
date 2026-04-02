import streamlit as st

st.set_page_config(page_title="This-to-That", layout="wide", initial_sidebar_state="expanded")

# --- Define pages (lazy-loaded) ---
home = st.Page("pages/home.py", title="Home", icon="🏠", default=True)
paste = st.Page("pages/1_📝_Paste_Text.py", title="Paste Text", icon="📝")
upload = st.Page("pages/2_📁_Upload_Files.py", title="Upload Files", icon="📁")
blocks = st.Page("pages/3_📋_Multi_Text_Blocks.py", title="Multi Text Blocks", icon="📋")
folder = st.Page("pages/4_📂_Batch_Folder.py", title="Batch Folder", icon="📂")

pg = st.navigation([home, paste, upload, blocks, folder])
pg.run()
