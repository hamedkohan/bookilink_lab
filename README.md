# Bookilink Lab

Bookilink Lab is a fast product prototype for making books interactive rather than merely searchable.

## Experiences

- **Book DNA** — thesis, recurring beliefs, assumptions, strongest/weakest arguments, tensions and durable takeaways.
- **Talk / Interrogate** — grounded conversation with `Talk`, `Interrogate`, `Skeptical`, `Devil's advocate`, and `Academic critique` modes.
- **Book Debate** — retrieve evidence from two books and put their ideas into one structured argument.

The deployed app opens in **Demo mode**, so it can be explored without an API key. Switch to **Live** to upload your own PDF/EPUB and run the real pipeline.

## Live architecture

```text
PDF / EPUB
   ↓
parser
   ↓
semantic chunks
   ↓
OpenAI embeddings (text-embedding-3-small)
   ↓
SQLite prototype store
   ↓
semantic retrieval
   ↓
Book DNA / Talk / Debate
   ↓
OpenAI Responses API
   ↓
answer + retrieved evidence
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

For Live mode, either export `OPENAI_API_KEY` or put it in `.env`.

## Streamlit Community Cloud

Deploy `app.py` from this repository. If you want Live mode to work without pasting a key in the sidebar, add this in **App settings → Secrets**:

```toml
OPENAI_API_KEY = "sk-..."
```

## Prototype limitations

- Scanned/image-only PDFs need OCR; v0.2 only extracts embedded PDF text.
- EPUB parsing is intentionally lightweight.
- SQLite is a prototype vector store and cloud filesystem persistence is not guaranteed across restarts.
- Retrieved source labels are grounding aids, not formal scholarly citations.
- Demo mode contains handcrafted sample content and does not contain or reproduce full book text.
- No accounts, billing, permissions, telemetry, or production persistence yet.
