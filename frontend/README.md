# Frontend — Next.js 14 Web App

This directory contains the Next.js 14 (App Router) web client for ጤናለአዳም
(Tena LeAdam). It provides the Amharic voice/text chat UI, the medicine-label
camera view, and an admin page that visualises the outbreak hotspot registry.

See the [root README](../README.md) for the full project overview. This file
focuses on running and developing the frontend in isolation.

## Layout

```text
frontend/
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
├── public/                          # Static assets (fonts, icons)
└── src/
    ├── app/
    │   ├── layout.tsx               # Root layout, metadata, Inter font
    │   ├── globals.css              # Tailwind base styles
    │   ├── page.tsx                 # Main chat UI (voice / text / camera)
    │   └── admin/page.tsx           # Outbreak hotspot dashboard
    ├── components/
    │   ├── MicButton.tsx            # Push-to-talk microphone control
    │   ├── AudioPlayer.tsx          # Plays the AI's Amharic TTS reply
    │   └── CameraUI.tsx             # Captures a medicine-label photo
    ├── hooks/
    │   └── useVoiceProcessor.js     # MediaRecorder audio pipeline
    └── lib/
        └── api.js                   # Axios client (baseURL = backend)
```

## Setup

```bash
cd frontend
npm install
```

Node.js 18.17+ is required by Next.js 14.

## Scripts

| Script          | Purpose                                               |
| --------------- | ----------------------------------------------------- |
| `npm run dev`   | Start the Next.js dev server on <http://localhost:3000>. |
| `npm run build` | Production build.                                     |
| `npm run start` | Run the production build.                             |
| `npm run lint`  | ESLint with `next/core-web-vitals` rules.             |

## Connecting to the Backend

The Axios client in `src/lib/api.js` currently hard-codes the backend base URL
to `http://localhost:8000`. If your backend runs elsewhere (for example, in
production or on a different port), update that file:

```js
// src/lib/api.js
import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});
```

If you adopt the `NEXT_PUBLIC_API_BASE_URL` pattern, create
`frontend/.env.local` with:

```dotenv
NEXT_PUBLIC_API_BASE_URL=https://your-backend.example.com
```

## Browser Permissions

- **Microphone** is required for voice chat (`MicButton` + `useVoiceProcessor`).
- **Camera** is required for the medicine-label scanner (`CameraUI`).

Chrome/Edge only expose these APIs on `https://` or `http://localhost`. When
deploying, serve the frontend over HTTPS.

## Pages

- `/` — Main chat experience: voice (push-to-talk), text input, and camera
  capture for medicine labels. Handles red-flag emergency flows, the
  *ሐኪም ያማክሩ* ("Consult a doctor") escalation button, and the mock emergency
  transport button.
- `/admin` — Simple dashboard that polls `GET /api/hotspots` and renders the
  sub-city → symptom → count registry for outbreak monitoring.

## Linting and Builds

```bash
npm run lint
npm run build
```

Both commands should pass before opening a pull request. See
[`../CONTRIBUTING.md`](../CONTRIBUTING.md) for the full contribution workflow.
