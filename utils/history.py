import streamlit as st
from datetime import datetime


def init_history():
    if "history" not in st.session_state:
        st.session_state.history = []


def save_history(original: str, translated: str, lang: str, eng: str):
    st.session_state.history.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "preview": original.replace("\n", " ").strip(),
        "original": original,
        "translated": translated,
        "lang": lang,
        "engine": eng,
    })
    if len(st.session_state.history) > 5:
        st.session_state.history = st.session_state.history[-5:]
