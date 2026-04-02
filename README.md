# This-to-That

A local Streamlit app that translates text between languages. Supports mixed-language content (e.g. Japanese + English), file uploads, batch folder translation, and multiple translation engines.

## Features

- **Paste Text** — paste and translate with side-by-side view
- **Upload Files** — upload one or multiple files (txt, json, csv, md, xml, html, yml, yaml, log, ini, cfg, tsv)
- **Multi Text Blocks** — translate multiple text blocks at once
- **Batch Folder** — point to a local folder and translate all supported files
- **Google Translate** — free, no API key needed
- **OpenAI GPT** — more accurate for mixed-language and structured content
- **Auto language detection** — shows detected languages with confidence
- **Copy to clipboard** — one-click copy on translated output
- **Translation history** — last 5 translations saved in session
- **Download** — single file or ZIP for batch results

## Setup

```bash
uv init --no-readme
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
uv run streamlit run Home.py
```

## Project Structure

```
Home.py                       # Home page (entry point)
pages/
  1_Paste_Text.py             # Paste & translate
  2_Upload_Files.py           # Upload file(s)
  3_Multi_Text_Blocks.py      # Multi text blocks
  4_Batch_Folder.py           # Batch folder translation
utils/
  config.py                   # Constants, languages, SSL config
  translator.py               # OpenAI + Google translate logic
  ui.py                       # UI components
  sidebar.py                  # Sidebar with settings + history
  history.py                  # Translation history
```
