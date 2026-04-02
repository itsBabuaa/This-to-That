import streamlit as st
import html as html_mod
import base64
import streamlit.components.v1 as components
from langdetect import detect_langs
from utils.config import LANG_NAMES


def apply_styles():
    st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 0; max-width: 1200px; }
        div[data-testid="stTextArea"] textarea {
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px; line-height: 1.5;
        }
        .panel-label {
            font-size: 13px; font-weight: 600; margin-bottom: 2px;
            color: #aaa; text-transform: uppercase; letter-spacing: 1px;
        }
        .app-subtitle { font-size: 13px; color: #888; margin: -10px 0 8px 0; }
        h2 { margin-bottom: 0 !important; padding-bottom: 0 !important; font-size: 22px !important; }
        .lined-box {
            background: #0e1117; border: 1px solid #333; border-radius: 8px;
            padding: 10px 0; overflow: auto; font-family: 'Consolas','Monaco',monospace;
            font-size: 13px; line-height: 1.6;
        }
        .lined-box table { border-collapse: collapse; width: 100%; }
        .lined-box td { padding: 0 10px; vertical-align: top; white-space: pre-wrap; word-break: break-all; }
        .lined-box .ln { color: #555; text-align: right; user-select: none; width: 1%;
            white-space: nowrap; padding-right: 12px; border-right: 1px solid #333; }
        .lined-box .code { color: #e0e0e0; padding-left: 12px; }
    </style>
    """, unsafe_allow_html=True)


def lined_text(text: str, height: int = 280):
    if not text:
        st.markdown(f'<div class="lined-box" style="height:{height}px;color:#555;padding:10px;">'
                    'No content</div>', unsafe_allow_html=True)
        return
    lines = text.split("\n")
    rows = ""
    for i, line in enumerate(lines, 1):
        escaped = html_mod.escape(line) if line else "&nbsp;"
        rows += f'<tr><td class="ln">{i}</td><td class="code">{escaped}</td></tr>'
    st.markdown(f'<div class="lined-box" style="max-height:{height}px;">'
                f'<table>{rows}</table></div>', unsafe_allow_html=True)


def output_header(label: str, text: str = "", key: str = ""):
    if text:
        b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
        components.html(f'''
            <style>html,body{{margin:0;padding:0;overflow:hidden;background:transparent;}}</style>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:13px;font-weight:600;color:#aaa;
                    text-transform:uppercase;letter-spacing:1px;
                    font-family:'Source Sans Pro',sans-serif;">{label}</span>
                <button id="cpbtn_{key}" style="
                    background:#333;color:#ccc;border:1px solid #555;border-radius:4px;
                    padding:2px 10px;font-size:11px;cursor:pointer;
                    font-family:'Source Sans Pro',sans-serif;
                " onclick="
                    var t=atob('{b64}');
                    var ta=document.createElement('textarea');
                    ta.value=t;ta.style.position='fixed';ta.style.left='-9999px';
                    document.body.appendChild(ta);ta.select();
                    document.execCommand('copy');document.body.removeChild(ta);
                    this.textContent='Copied!';
                    setTimeout(()=>this.textContent='Copy',1500);
                ">Copy</button>
            </div>
        ''', height=20)
    else:
        st.markdown(f'<p class="panel-label">{label}</p>', unsafe_allow_html=True)


def detect_language(text: str) -> str:
    try:
        results = detect_langs(text[:3000])
        parts = []
        for r in results[:3]:
            name = LANG_NAMES.get(r.lang, r.lang.upper())
            parts.append(f"{name} {r.prob:.0%}")
        return " | ".join(parts)
    except Exception:
        return "Unknown"


def char_and_detect(text: str, max_chars: int):
    char_count = len(text)
    color = "#ff4b4b" if char_count > max_chars * 0.9 else "#888"
    det_str = detect_language(text) if text.strip() else ""
    if det_str:
        st.markdown(f'<p style="font-size:12px;margin-top:-10px;display:flex;justify-content:space-between">'
                    f'<span style="color:#6c9">Detected: {det_str}</span>'
                    f'<span style="color:{color}">{char_count:,} / {max_chars:,} chars</span></p>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<p style="font-size:12px;color:{color};text-align:right;margin-top:-10px">'
                    f'{char_count:,} / {max_chars:,} chars</p>', unsafe_allow_html=True)


def read_file(f) -> str:
    f.seek(0)
    try:
        return f.read().decode("utf-8")
    except UnicodeDecodeError:
        f.seek(0)
        return f.read().decode("latin-1")
