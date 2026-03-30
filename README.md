# 🔄 This-to-That

A local Streamlit app that translates mixed-language text (primarily Japanese → English) using OpenAI. Upload files or paste text — only the foreign-language parts get translated, everything else stays intact.

## Architecture

```mermaid
graph TD
    A[User] -->|Paste text / Upload files| B[Streamlit UI]
    B --> C{Input Type}
    C -->|Pasted Text| D[Single Translation]
    C -->|Single File| D
    C -->|Multiple Files| E[Batch Translation]

    D --> F[Chunker]
    E --> F

    F -->|≤10k char chunks| G[OpenAI API]
    G -->|Translated text| H[Session State]
    H --> I[Side-by-Side Display]
    I --> J[Download .txt / .zip]

    subgraph Sidebar
        K[API Key]
        L[Target Language]
        M[Model Selection]
        N[File Upload]
    end

    Sidebar --> B
```

## Flow

```mermaid
sequenceDiagram
    participant U as User
    participant S as Streamlit
    participant O as OpenAI API

    U->>S: Paste text or upload file(s)
    U->>S: Select target language
    U->>S: Click Translate

    S->>S: Read & chunk text (10k chars)

    loop Each chunk
        S->>O: System prompt + chunk
        O-->>S: Translated chunk
    end

    S->>S: Store in session_state
    S-->>U: Show side-by-side result
    U->>S: Download translation
```

## Setup

```bash
uv init --no-readme
uv add streamlit openai python-dotenv
```

Create a `.env` file:

```
OPENAI_API_KEY=sk-your-key-here
```

## Run

```bash
uv run streamlit run app.py
```

## Features

- Paste text or upload single/multiple files (json, txt, csv, md, xml, etc.)
- Translates only foreign-language parts, keeps target-language text untouched
- Side-by-side original vs translated view
- Download as `.txt` or `.zip` (multi-file) with `_english_translated` naming
- Persistent results across Streamlit reruns
- Configurable model (gpt-4o-mini default, gpt-4o, gpt-3.5-turbo)
