# Backend — FastAPI Service

This directory contains the Python/FastAPI service that powers ጤናለአዳም
(Tena LeAdam). It orchestrates Amharic speech-to-text, retrieval-augmented
medical reasoning against Ethiopian MoH guidelines, medicine-label vision
analysis, Amharic text-to-speech, and Telegram alerts to a hospital doctors'
group chat.

See the [root README](../README.md) for the full project overview. This file
focuses on running and developing the backend in isolation.

## Layout

```text
backend/
├── main.py                 # FastAPI app + HTTP routes + orchestration
├── requirements.txt        # Pinned Python dependencies
├── core/
│   ├── stt_engine.py       # Amharic STT via Gemini audio upload
│   ├── tts_engine.py       # Amharic TTS (edge-tts + gTTS fallback)
│   ├── rag_engine.py       # ChromaDB + LlamaIndex + Gemini RAG
│   └── vision_eval.py      # Medicine-label analysis via Gemini vision
├── utils/
│   ├── mapping.py          # Amharic symptom → canonical term map
│   ├── emergency.py        # Red-flag keyword triage
│   ├── text_utils.py       # Latin-script stripping, etc.
│   └── telegram_bot.py     # Doctor-alert Telegram dispatcher
├── scripts/
│   ├── ingest.py           # Build the Chroma vector DB from PDFs
│   ├── test_persona.py     # Persona smoke test
│   └── verify_features.py  # End-to-end smoke test
└── data/                   # (mostly git-ignored) runtime data
    ├── guidelines/         # MoH Amharic PDFs (input to ingestion)
    ├── vector_db/          # Persistent Chroma store (output of ingestion)
    ├── storage/            # Per-user chat memory (chat_store.json)
    ├── audio_outputs/      # Temporary TTS .mp3 files
    └── temp/               # Temporary uploaded audio/image files
```

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env               # then fill in GEMINI_API_KEY / GOOGLE_API_KEY
```

The requirements pin CPU-only Torch (`torch==2.11.0+cpu`). If `pip` cannot
resolve it on your platform, install Torch separately from
<https://pytorch.org/get-started/locally/> and re-run
`pip install -r requirements.txt`.

## Ingestion

Place MoH Amharic clinical-guideline PDFs under `data/guidelines/` and run:

```bash
python -m scripts.ingest
```

This chunks and embeds the PDFs into a persistent `moh_guidelines` collection
under `data/vector_db/`. The script processes 20 pages at a time and
automatically sleeps for 60 s when it hits a Gemini `ResourceExhausted`
(429) error.

## Running

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI: <http://localhost:8000/docs>
- OpenAPI JSON: <http://localhost:8000/openapi.json>

The service creates `data/audio_outputs/`, `data/temp/`, and
`data/guidelines/` on startup if they do not already exist. A background task
deletes files older than five minutes from `audio_outputs/` and `temp/` every
five minutes.

## HTTP API

| Method | Path                    | Purpose |
| ------ | ----------------------- | ------- |
| POST   | `/api/voice-chat`       | Multipart audio → Amharic transcription + Amharic audio reply. |
| POST   | `/api/text-chat`        | JSON text → Amharic audio reply. |
| POST   | `/api/vision-analyze`   | Multipart image → Amharic medicine-label analysis. |
| POST   | `/api/hakim-yamakru`    | Push a patient summary to the hospital doctors' Telegram group (used both for automatic red-flag escalation and for the user-initiated *ሐኪም ያማክሩ* button on any conversation). |
| GET    | `/api/hotspots`         | Current sub-city symptom hotspot registry. |
| GET    | `/api/audio/{filename}` | Stream a generated TTS MP3. |
| GET    | `/pdfs/{filename}`      | Static mount for the raw MoH PDFs used as citations. |

See the [API Reference](../README.md#api-reference) in the root README for
request/response details.

## Environment Variables

| Name                      | Required | Description |
| ------------------------- | :------: | ----------- |
| `GEMINI_API_KEY`          | ✅ | Google AI Studio key, used by `core/stt_engine.py` and `core/vision_eval.py`. |
| `GOOGLE_API_KEY`          | ✅ | Same key, under the name LlamaIndex's Gemini integration expects. Set both to the same value. |
| `TELEGRAM_BOT_TOKEN`      | ⛔ optional | Bot token for the doctor-alert dispatcher. |
| `TELEGRAM_DOCTOR_CHAT_ID` | ⛔ optional | Numeric chat ID of the hospital doctors' Telegram group the bot has been added to (group IDs start with `-100…`). `TELEGRAM_CHAT_ID` is accepted as an alias. |

See [Setting Up the Doctors' Telegram Group](../README.md#setting-up-the-doctors-telegram-group)
in the root README for the full bot → group → chat-ID walkthrough.

Secrets are loaded from `backend/.env` via `python-dotenv`. `.env` is
git-ignored; never commit it.

## Development Scripts

```bash
# Persona smoke test: confirms the RAG doctor answers in Amharic only.
python -m scripts.test_persona

# End-to-end feature verification (uses mocked Telegram creds by default).
python -m scripts.verify_features
```

## Troubleshooting

- **`GEMINI_API_KEY` missing** — the server starts, but the first STT / RAG /
  vision call raises. Set both `GEMINI_API_KEY` and `GOOGLE_API_KEY` in
  `backend/.env` and restart.
- **Empty ChromaDB** — if `data/vector_db/` is empty, the RAG engine falls
  back to a basic LLM response without citations. Add PDFs to
  `data/guidelines/` and re-run `python -m scripts.ingest`.
- **`edge-tts` failures** — the TTS engine falls back to `gTTS` automatically.
  Look for `⚠️ edge-tts failed` in the backend logs.
- **Telegram alerts not firing** — the dispatcher logs a warning and returns
  `False` when `TELEGRAM_BOT_TOKEN` / `TELEGRAM_DOCTOR_CHAT_ID` are not set,
  or when the bot has not been added to the hospital doctors' Telegram
  group whose ID is in `TELEGRAM_DOCTOR_CHAT_ID`.
