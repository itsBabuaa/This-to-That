import os
import streamlit as st
from utils.config import LANGUAGES


def render_sidebar():
    with st.sidebar:
        st.markdown("### 🔄 This-to-That")
        engine = st.selectbox("Translation Engine", ["Google Translate (Free)", "OpenAI"])
        if engine == "OpenAI":
            api_key = st.text_input("OpenAI API Key", type="password",
                                    value=os.getenv("OPENAI_API_KEY", ""))
            model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
        else:
            api_key = ""
            model = ""
        target_lang = st.selectbox("Translate to", LANGUAGES)

        st.divider()
        st.markdown("#### 🕐 History")
        if st.session_state.history:
            for i, entry in enumerate(reversed(st.session_state.history)):
                idx = len(st.session_state.history) - 1 - i
                preview = entry["preview"][:40] + ("..." if len(entry["preview"]) > 40 else "")
                label = f'{entry["timestamp"]} | {entry["lang"]} | {entry["engine"][:6]}'
                if st.button(f'{preview}\n{label}', key=f"hist_{idx}", use_container_width=True):
                    st.session_state.paste_result = entry["translated"]
                    st.session_state.paste_dl_name = f'history_{entry["lang"].lower()}_translated.txt'
                    st.rerun()
            if st.button("Clear History", use_container_width=True, key="clear_hist"):
                st.session_state.history = []
                st.rerun()
        else:
            st.caption("No translations yet.")

    return engine, api_key, model, target_lang
