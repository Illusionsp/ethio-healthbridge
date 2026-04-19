# Contributing to Ethio-HealthBridge

Thanks for your interest in improving ጤናለአዳም (Tena LeAdam)! This document
summarises how to set up a development environment, the conventions we follow,
and how to propose changes.

## Code of Conduct

Please be respectful, constructive, and patient in all project spaces. This
project touches health information; hold yourself to a high standard of care
and humility when discussing clinical logic, triage thresholds, or Amharic
linguistic choices.

## Getting Set Up Locally

Follow the [Quick Start](README.md#quick-start) in the README to install
dependencies and run both services. The short version:

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in GEMINI_API_KEY / GOOGLE_API_KEY
uvicorn main:app --reload

# Frontend
cd ../frontend
npm install
npm run dev
```

## Branching and Commits

- **Never push directly to `main`.** Open a pull request.
- Use short, descriptive branch names prefixed with the type of change, e.g.:
  - `feat/medicine-scanner-cropping`
  - `fix/empty-transcription-handling`
  - `docs/readme-quickstart`
- Prefer [Conventional Commits](https://www.conventionalcommits.org/) for
  commit messages:
  ```
  feat(rag): add per-user chat memory buffer
  fix(tts): fall back to gTTS when edge-tts returns empty audio
  docs: expand backend environment-variable reference
  ```
- Keep PRs focused and small. Large refactors should be split into reviewable
  chunks whenever possible.

## Coding Conventions

### Python (backend)

- Target Python 3.10+ syntax (type hints, `list[str]`, etc.).
- Keep imports at the top of the file.
- Prefer small, pure helpers in `utils/` over fat functions in `main.py`.
- Log user-visible messages in Amharic where they surface to end users; keep
  developer-facing logs in English.
- Do **not** embed API keys or personal data in fixtures, tests, or commits.
  Use `.env` and the existing `_get_env` helper.

### TypeScript / React (frontend)

- Follow the `next/core-web-vitals` ESLint config (`npm run lint`).
- Prefer functional components and hooks. Co-locate component state where
  possible.
- Tailwind classes go in JSX; avoid ad-hoc CSS unless a feature genuinely
  needs it.
- Keep the Axios client in `src/lib/api.js` as the single source of truth for
  the backend base URL.

### Commits that change clinical behaviour

Changes to any of the following require extra scrutiny and a clear PR
description explaining the rationale:

- `backend/utils/emergency.py` (red-flag keywords, 912 message)
- `backend/utils/mapping.py` (symptom terminology)
- `backend/core/rag_engine.py` (doctor-persona system prompt)
- `backend/core/vision_eval.py` (medicine-label instructions)

Please cite the MoH guideline, WHO protocol, or clinical source you are
drawing from when adjusting these.

## Tests and Verification

There is no pytest suite yet, but a lightweight end-to-end check lives at
`backend/scripts/verify_features.py`. Run it before opening a PR that touches
backend logic:

```bash
cd backend
source .venv/bin/activate
python -m scripts.verify_features
```

For frontend changes, run:

```bash
cd frontend
npm run lint
npm run build
```

## Security and Privacy

- Never commit `.env`, Telegram tokens, Gemini keys, or real patient data.
- The `.gitignore` excludes `backend/data/guidelines/*.pdf`,
  `backend/data/vector_db/`, `backend/data/storage/chat_store.json`, and
  `backend/data/audio_outputs/*`. Please keep it that way.
- If you discover a vulnerability, please open a private issue or contact a
  maintainer directly rather than filing a public bug report.

## Pull Request Checklist

Before requesting review, please confirm:

- [ ] Branch is up to date with `main` and rebased (no merge commits from `main`).
- [ ] Backend changes run cleanly with `uvicorn main:app --reload`.
- [ ] Frontend changes pass `npm run lint` and `npm run build`.
- [ ] `scripts/verify_features.py` still passes (when backend logic changed).
- [ ] README / `.env.example` updated for any new config or endpoint.
- [ ] No secrets, PII, or real patient data in the diff.

Thank you for helping make Amharic-first healthcare tooling better! 🙏
