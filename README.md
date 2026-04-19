# ጤናለአዳም (Tena LeAdam) — Ethio-HealthBridge

**A multimodal AI healthcare assistant for the Ethiopian context.**

ጤናለአዳም (*Tena LeAdam* — "Health for Humanity") is an AI-powered triage and
medical-guidance system that accepts **Amharic voice, text, and images** and
responds in natural Amharic speech. Its answers are grounded in official
**Ethiopian Ministry of Health (MoH) clinical guidelines** via a retrieval-augmented
generation (RAG) pipeline, and it includes an automatic red-flag emergency
detector that dispatches a clinical alert to a hospital doctors' Telegram group.

> ⚠️ **Medical disclaimer.** This project is a research/hackathon prototype. It
> is **not** a substitute for professional medical advice, diagnosis, or
> treatment. In a real emergency, call **912** (Ethiopia) or your local
> emergency number.

---

## Table of Contents

- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Repository Layout](#repository-layout)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Configure environment variables](#2-configure-environment-variables)
  - [3. Set up the backend](#3-set-up-the-backend)
  - [4. Ingest MoH guidelines into the vector database](#4-ingest-moh-guidelines-into-the-vector-database)
  - [5. Run the backend](#5-run-the-backend)
  - [6. Run the frontend](#6-run-the-frontend)
- [Environment Variables](#environment-variables)
- [Setting Up the Doctors' Telegram Group](#setting-up-the-doctors-telegram-group)
- [API Reference](#api-reference)
- [Scripts and Utilities](#scripts-and-utilities)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Key Features

- **Amharic Voice-to-Voice chat.** Speak in Amharic; the system transcribes,
  reasons over MoH guidelines, and replies with a natural Amharic neural voice.
- **Grounded Medical RAG.** Answers are retrieved from official MoH Clinical
  Guidelines stored in a persistent ChromaDB vector store, then summarized by
  Gemini under a strict Amharic-only doctor persona.
- **Medicine Label Scanner (Vision).** Upload a photo of a drug label and get
  an Amharic breakdown of name, dosage, expiry, manufacturer, and warnings.
- **Red-Flag Emergency Mode.** A keyword/semantic triage layer detects
  life-threatening symptoms (chest pain, severe bleeding, unconsciousness,
  etc.) and returns an immediate 912 prompt, bypassing the LLM path.
- **Doctor Escalation.** When a red flag fires (or the user taps *ሐኪም ያማክሩ*),
  a structured clinical summary is pushed to a Telegram group of hospital
  doctors so the on-call clinician can pick it up immediately.
- **Outbreak Hotspot Tracking.** Reported symptoms are aggregated per Addis
  Ababa sub-city and surfaced via an admin dashboard; crossing a threshold
  raises an outbreak alert.
- **Per-User Conversation Memory.** Each `user_id` gets its own chat history
  buffer so follow-up questions stay in context.

## Architecture

```text
 ┌─────────────────────┐      audio / text / image       ┌───────────────────────────┐
 │  Next.js Frontend   │ ──────────────────────────────▶ │   FastAPI Backend (main)  │
 │  (Chat + Admin UI)  │ ◀────────────────────────────── │   Orchestrator & Router   │
 └─────────────────────┘      JSON + audio URL            └─────────────┬─────────────┘
                                                                        │
              ┌─────────────────────────┬─────────────────────────┬─────┴─────────────────────┐
              ▼                         ▼                         ▼                           ▼
   ┌────────────────────┐   ┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐
   │  STT Engine        │   │  RAG Engine            │  │  Vision Engine         │  │  Emergency / Triage    │
   │  (Gemini Audio)    │   │  (LlamaIndex +         │  │  (Gemini 2.5 Flash     │  │  Red-flag keywords +   │
   │  Amharic → text    │   │   ChromaDB + Gemini)   │  │   Lite, image → text)  │  │  Telegram dispatch     │
   └────────────────────┘   └────────────────────────┘  └────────────────────────┘  └────────────────────────┘
                                          │
                                          ▼
                             ┌────────────────────────┐
                             │  MoH Clinical          │
                             │  Guidelines (PDFs) →   │
                             │  Chroma vector store   │
                             └────────────────────────┘
                                          │
                                          ▼
                             ┌────────────────────────┐
                             │  TTS Engine            │
                             │  edge-tts (Mekdes      │
                             │  Neural) → gTTS fallbk │
                             └────────────────────────┘
```

**Request flow (voice chat):**

1. The browser records audio and posts it to `POST /api/voice-chat`.
2. The STT engine (`core/stt_engine.py`) uploads the audio to Gemini and
   returns a cleaned Amharic transcription.
3. `utils/mapping.py` extracts known symptom tokens from the transcription,
   which are logged to the in-memory hotspot registry and checked against the
   red-flag list in `utils/emergency.py`.
4. If a red flag fires, an emergency response is returned immediately and a
   structured alert is pushed to the hospital doctors' Telegram group.
   Otherwise, the query is enriched
   with extracted symptoms and sent to the RAG engine (`core/rag_engine.py`),
   which retrieves from ChromaDB and answers via Gemini under an
   Amharic-only doctor persona.
5. The response text is stripped of any Latin characters and synthesized to
   Amharic speech by `core/tts_engine.py` (edge-tts, falling back to gTTS).
6. The backend returns the transcription, Amharic response text, audio URL,
   emergency flag, citations, and a patient summary.

## Tech Stack

| Layer            | Technology |
| ---------------- | ---------- |
| Frontend         | Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Axios, lucide-react |
| Backend          | FastAPI, Uvicorn, Pydantic, python-dotenv |
| LLM              | Google Gemini (`gemini-2.5-flash-lite`) via `google-generativeai` and `llama-index-llms-gemini` |
| Embeddings       | `models/gemini-embedding-001` via `llama-index-embeddings-gemini` |
| Vector store     | ChromaDB (persistent, on-disk) |
| RAG framework    | LlamaIndex (core, readers, workflows, chat memory) |
| Amharic STT      | Gemini audio upload + prompted transcription (`core/stt_engine.py`) |
| Amharic TTS      | Microsoft `edge-tts` (`am-ET-MekdesNeural`) with `gTTS` fallback |
| Doctor alerts    | Telegram Bot API |
| PDF ingestion    | `pypdf`, `SimpleDirectoryReader` |

## Repository Layout

```text
ethio-healthbridge/
├── backend/                        # Python / FastAPI service
│   ├── main.py                     # API routes + orchestration
│   ├── requirements.txt            # Pinned backend dependencies
│   ├── core/
│   │   ├── stt_engine.py           # Amharic speech-to-text (Gemini audio)
│   │   ├── tts_engine.py           # Amharic TTS (edge-tts + gTTS fallback)
│   │   ├── rag_engine.py           # ChromaDB + LlamaIndex + Gemini RAG
│   │   └── vision_eval.py          # Medicine-label vision analysis
│   ├── utils/
│   │   ├── mapping.py              # Amharic symptom → canonical term map
│   │   ├── emergency.py            # Red-flag detection + emergency message
│   │   ├── text_utils.py           # Text cleaning helpers
│   │   └── telegram_bot.py         # Doctor-alert dispatcher
│   ├── scripts/
│   │   ├── ingest.py               # Build the Chroma vector DB from PDFs
│   │   ├── test_persona.py         # Sanity-check the RAG persona
│   │   └── verify_features.py      # End-to-end feature smoke test
│   └── data/
│       ├── guidelines/             # (gitignored) MoH Amharic protocol PDFs
│       ├── vector_db/              # (gitignored) Persistent Chroma store
│       ├── storage/                # Per-user chat memory (chat_store.json)
│       ├── audio_outputs/          # Temporary TTS .mp3 files
│       └── temp/                   # Uploaded audio/image temp files
├── frontend/                       # Next.js 14 web app
│   └── src/
│       ├── app/
│       │   ├── page.tsx            # Main chat UI (voice / text / camera)
│       │   ├── admin/page.tsx      # Outbreak hotspot dashboard
│       │   ├── layout.tsx          # Root layout + metadata
│       │   └── globals.css         # Tailwind base styles
│       ├── components/
│       │   ├── MicButton.tsx       # Push-to-talk mic control
│       │   ├── AudioPlayer.tsx     # Streams the AI's Amharic reply
│       │   └── CameraUI.tsx        # Capture medicine-label photos
│       ├── hooks/
│       │   └── useVoiceProcessor.js  # MediaRecorder audio pipeline
│       └── lib/
│           └── api.js              # Axios client (baseURL = backend)
├── LICENSE                         # MIT
└── README.md
```

## Prerequisites

- **Python 3.10+** (3.11 or 3.12 recommended — matches the pinned wheels).
- **Node.js 18.17+** (required by Next.js 14).
- **A Gemini API key.** Create one at
  [Google AI Studio](https://aistudio.google.com/app/apikey). The free tier is
  enough to run the app end-to-end; ingestion of large PDFs may require waiting
  on rate limits (the ingest script handles this automatically).
- **(Optional) Telegram bot + doctors' group** for clinical alerts. Create a
  bot with [@BotFather](https://t.me/BotFather), then add it to the Telegram
  group that your hospital doctors share. The numeric chat ID of that group
  is what `TELEGRAM_DOCTOR_CHAT_ID` should hold (group IDs start with `-100…`).
  See [Setting Up the Doctors' Telegram Group](#setting-up-the-doctors-telegram-group).
- **(Optional) MoH guideline PDFs** placed under `backend/data/guidelines/`.
  Without PDFs the RAG store is empty and the backend falls back to a plain
  LLM response.

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Illusionsp/ethio-healthbridge.git
cd ethio-healthbridge
```

### 2. Configure environment variables

Create `backend/.env` (see [`backend/.env.example`](backend/.env.example)):

```dotenv
# Required: Gemini (STT, RAG, Vision, embeddings)
GEMINI_API_KEY=your_gemini_api_key
# LlamaIndex's Gemini integration also reads GOOGLE_API_KEY
GOOGLE_API_KEY=your_gemini_api_key

# Optional: Telegram doctor-alert bot.
# TELEGRAM_DOCTOR_CHAT_ID is the numeric chat ID of the hospital doctors'
# Telegram group that the bot has been added to (group IDs start with -100…).
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_DOCTOR_CHAT_ID=-1001234567890
```

### 3. Set up the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

> The requirements file pins CPU-only Torch (`torch==2.11.0+cpu`). If `pip`
> cannot resolve it on your platform, install Torch separately from
> <https://pytorch.org/get-started/locally/> and then re-run `pip install -r
> requirements.txt`.

### 4. Ingest MoH guidelines into the vector database

Place one or more MoH Amharic clinical-guideline PDFs into
`backend/data/guidelines/`, then run:

```bash
cd backend
python -m scripts.ingest
```

This builds `backend/data/vector_db/` (a persistent ChromaDB collection named
`moh_guidelines`) in batches of 20 pages, with automatic back-off on Gemini
quota errors. You only need to run this once, and again whenever the PDFs
change.

### 5. Run the backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API is now live at <http://localhost:8000>; interactive Swagger docs are
at <http://localhost:8000/docs>.

### 6. Run the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:3000>. The Axios client in `frontend/src/lib/api.js`
defaults to `http://localhost:8000`.

Available frontend scripts:

| Script          | Purpose                              |
| --------------- | ------------------------------------ |
| `npm run dev`   | Start the Next.js dev server         |
| `npm run build` | Production build                     |
| `npm run start` | Run the production build             |
| `npm run lint`  | ESLint with the `next/core-web-vitals` config |

## Environment Variables

| Name                      | Required | Used by | Description |
| ------------------------- | :------: | ------- | ----------- |
| `GEMINI_API_KEY`          | ✅ | `core/stt_engine.py`, `core/vision_eval.py` | Google AI Studio API key for audio and vision calls. |
| `GOOGLE_API_KEY`          | ✅ | `core/rag_engine.py`, `scripts/ingest.py` | Same key, under the name LlamaIndex's Gemini integration looks for. In practice, set both variables to the same value. |
| `TELEGRAM_BOT_TOKEN`      | ⛔ optional | `utils/telegram_bot.py` | Bot token from [@BotFather](https://t.me/BotFather). When missing, doctor alerts are disabled silently. |
| `TELEGRAM_DOCTOR_CHAT_ID` | ⛔ optional | `utils/telegram_bot.py` | Numeric chat ID of the hospital doctors' Telegram group the bot has been added to. Group IDs start with `-100…`. `TELEGRAM_CHAT_ID` is accepted as an alias. |

`backend/.env` is git-ignored. Never commit real keys.

## Setting Up the Doctors' Telegram Group

Clinical alerts (red-flag emergencies and explicit *ሐኪም ያማክሩ* /
"Consult a doctor" taps) are pushed into a **Telegram group that you create
for the hospital's on-call doctors**, not into a single private chat. This
way any doctor in the rota can pick the alert up.

One-time setup:

1. **Create the bot.** Open [@BotFather](https://t.me/BotFather), run
   `/newbot`, give it a name (e.g. `Tena LeAdam Triage`) and a username
   (e.g. `tena_leadam_triage_bot`). BotFather replies with a token of the
   form `123456789:ABCdefGhIJK...` — this is your `TELEGRAM_BOT_TOKEN`.
2. **Disable group privacy** so the bot can read group messages it needs to
   acknowledge (optional but recommended). In BotFather: `/mybots` → select
   the bot → *Bot Settings* → *Group Privacy* → *Turn off*.
3. **Create the doctors' group** in Telegram and add every on-call doctor
   who should receive alerts.
4. **Add the bot to the group** (group settings → *Add members* → search by
   the bot's username).
5. **Get the group's chat ID.** The easiest way:
   - Send any message in the group.
   - Open `https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates` in a
     browser.
   - Look for `"chat":{"id":-1001234567890,...}` in the response. That
     negative number (group IDs always start with `-100…`) is your
     `TELEGRAM_DOCTOR_CHAT_ID`.
6. **Set both values** in `backend/.env`:
   ```dotenv
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJK...
   TELEGRAM_DOCTOR_CHAT_ID=-1001234567890
   ```
7. **Restart the backend** and trigger a test alert by hitting
   `POST /api/hakim-yamakru` (the *ሐኪም ያማክሩ* button in the UI does this)
   with any patient summary. You should see a formatted *CLINICAL TRIAGE
   ALERT* message land in the doctors' group.

If either variable is missing, `utils/telegram_bot.py` logs a warning and
the rest of the system continues to work — alerts simply aren't dispatched.

## API Reference

All endpoints are served by FastAPI from `backend/main.py`.

### `POST /api/voice-chat`
Multipart form: `audio` (required, audio file), `sub_city` (optional, string),
`user_id` (optional, string).
Returns JSON with `transcription`, `response_text` (Amharic), `audio_url`,
`emergency` (bool), `alert_sent` (bool), `citations`, and `patient_summary`.

### `POST /api/text-chat`
JSON body:
```json
{ "text": "ጭንቅላቴን በጣም ያመኛል", "sub_city": "Bole", "user_id": "guest_user" }
```
Returns the same shape as `voice-chat`, minus `transcription`.

### `POST /api/vision-analyze`
Multipart form: `image` (required, image file). Returns JSON with the Amharic
`analysis` of the medicine label and an `audio_url` for the spoken version.

### `POST /api/hakim-yamakru`
JSON body: a patient-summary object as returned by `/voice-chat` or
`/text-chat`. Triggers a Telegram doctor alert. Returns
`{"status": "success"}` on success.

### `GET /api/hotspots`
Returns the current in-memory sub-city → symptom → count map. Consumed by the
admin dashboard at `/admin`.

### `GET /api/audio/{filename}`
Serves a generated TTS MP3 from `backend/data/audio_outputs/`. Temporary files
older than five minutes are cleaned up automatically.

### `GET /pdfs/{filename}`
Static mount for the raw MoH PDFs under `backend/data/guidelines/`, used for
citation links.

## Scripts and Utilities

- `backend/scripts/ingest.py` — Chunk and embed PDFs into ChromaDB.
- `backend/scripts/test_persona.py` — Quick check that the RAG persona answers
  in Amharic only.
- `backend/scripts/verify_features.py` — End-to-end smoke test across STT,
  RAG, vision, and Telegram (with mocked credentials).

Run them from the `backend/` directory with the virtualenv activated, e.g.:

```bash
cd backend
python -m scripts.verify_features
```

## Troubleshooting

- **`GEMINI_API_KEY` / `GOOGLE_API_KEY` not set.** The backend will start, but
  STT, RAG, and vision calls will fail at runtime. Set both variables in
  `backend/.env` and restart `uvicorn`.
- **Rate-limit (429) during ingestion.** `scripts/ingest.py` automatically
  sleeps for 60 s when it detects a `ResourceExhausted` error and retries the
  current batch. Running against the free tier is expected to pause a few
  times on large documents.
- **Empty ChromaDB / generic answers.** If `data/vector_db/` is empty, the RAG
  engine falls back to a basic LLM response without MoH citations. Add PDFs
  to `data/guidelines/` and re-run `python -m scripts.ingest`.
- **No audio plays in the browser.** `edge-tts` requires outbound access to
  Microsoft's TTS endpoints. If it fails, the backend falls back to `gTTS`
  automatically — check the backend console logs for `⚠️ edge-tts failed`.
- **Telegram alerts not firing.** Confirm both `TELEGRAM_BOT_TOKEN` and
  `TELEGRAM_DOCTOR_CHAT_ID` are set, that the bot has been *added to the
  hospital doctors' Telegram group* (not just started in a private chat),
  and that `TELEGRAM_DOCTOR_CHAT_ID` is the numeric ID of that group. Without
  these variables, the dispatcher logs a warning and returns `False` instead
  of raising. See [Setting Up the Doctors' Telegram Group](#setting-up-the-doctors-telegram-group)
  for the full setup walkthrough.
- **CORS errors from the frontend.** The backend ships with `allow_origins=["*"]`
  for development. In production, restrict it to your deployed frontend origin.

## Contributing

Contributions are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) for
the branch naming convention, commit-message style, and local-development
checklist. Bug reports and feature requests can be filed as GitHub issues.

## License

Released under the [MIT License](LICENSE). © 2026 Ethio-HealthBridge Team.

## Acknowledgements

- The Ethiopian Ministry of Health for the publicly available clinical
  guidelines this project is grounded in.
- [Google DeepMind Gemini](https://ai.google.dev/), [LlamaIndex](https://www.llamaindex.ai/),
  [ChromaDB](https://www.trychroma.com/), [edge-tts](https://github.com/rany2/edge-tts),
  and [gTTS](https://github.com/pndurette/gTTS) for the open tooling that
  makes this prototype possible.
- The Amharic-speaking community and health workers whose feedback continues
  to shape the persona, vocabulary, and triage heuristics.
