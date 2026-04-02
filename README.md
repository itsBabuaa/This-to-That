# This-to-That

A local Streamlit app that translates text between languages. Supports mixed-language content (e.g. Japanese + English), file uploads, batch folder translation, and multiple translation engines.

## Features

- **📝 Paste Text** — paste and translate with side-by-side view
- **📁 Upload Files** — upload one or multiple files (txt, json, csv, md, xml, html, yml, yaml, log, ini, cfg, tsv)
- **📋 Multi Text Blocks** — translate multiple text blocks at once
- **📂 Batch Folder** — point to a local folder and translate all supported files
- **Google Translate** — free, no API key needed
- **OpenAI GPT** — more accurate for mixed-language and structured content
- **Auto language detection** — shows detected languages with confidence
- **Copy to clipboard** — one-click copy on translated output
- **Translation history** — last 5 translations saved in session
- **Download** — single file or ZIP for batch results
- **Lazy-loaded pages** — only the active page runs

## Setup

```bash
uv add streamlit openai python-dotenv deep-translator httpx urllib3 langdetect
```

## Configuration

Create a `.env` file (optional, for OpenAI):

```
OPENAI_API_KEY=sk-your-key-here
```

Google Translate works without any API key.

## Run

```bash
uv run streamlit run app.py
```

## Project Structure

```
app.py                            # Entry point (st.navigation)
pages/
  home.py                         # Home page with feature cards
  1_📝_Paste_Text.py              # Paste & translate
  2_📁_Upload_Files.py            # Upload file(s)
  3_📋_Multi_Text_Blocks.py       # Multi text blocks
  4_📂_Batch_Folder.py            # Batch folder translation
utils/
  config.py                       # Constants, languages, SSL config
  translator.py                   # OpenAI + Google translate logic
  ui.py                           # UI components
  sidebar.py                      # Sidebar with settings + history
  history.py                      # Translation history
```
