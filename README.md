# 🏗️ Ethio-HealthBridge
**Multimodal AI Healthcare Assistant for the Ethiopian Context**

Ethio-HealthBridge is an AI-powered system designed to provide grounded medical guidance using the **Ethiopian Ministry of Health (MoH)** protocols. It supports Amharic voice, text, and image inputs to ensure accessibility for all.

## 🚀 Key Features
* **Amharic Voice-to-Voice:** Speak in Amharic and hear the AI respond in a natural neural voice.
* **Medical RAG:** Advice is strictly grounded in official MoH Clinical Guidelines using ChromaDB.
* **Medicine Scanner:** Analyze drug labels and expiry dates using Gemini 1.5 Flash Vision.
* **Emergency Mode:** Real-time detection of "Red Flag" symptoms with 912 integration.

## 🛠️ Tech Stack
* **Brain:** Gemini 1.5 Flash (RAG & Vision)
* **Ear:** Faster-Whisper (Amharic STT)
* **Voice:** Azure Neural / Gemini TTS
* **Database:** ChromaDB (Vector Store)
* **Frontend:** Next.js 14 + Tailwind CSS
* **Backend:** FastAPI (Python)

## 📂 Project Architecture

```text
ethio-healthbridge/
├── backend/                        # Python / FastAPI Root
│   ├── main.py                     # System Orchestrator & API Logic
│   ├── core/                       # The "Engines" of the AI
│   │   ├── stt_engine.py           # Amharic Speech-to-Text (Faster-Whisper)
│   │   ├── tts_engine.py           # Amharic Text-to-Speech (Neural Synthesis)
│   │   ├── rag_engine.py           # Medical RAG (ChromaDB + LlamaIndex)
│   │   └── vision_eval.py          # Gemini 1.5 Flash Vision Analysis
│   ├── data/                       # Knowledge Base & Storage
│   │   ├── guidelines/             # MoH Amharic Medical Protocols (PDFs)
│   │   ├── vector_db/              # Persistent ChromaDB Vector Store
│   │   └── audio_outputs/          # Temporary AI voice response files (.mp3)
│   ├── utils/                      # Internal System Utilities
│   │   ├── mapping.py              # Ge'ez-to-Medical terminology dictionary
│   │   └── emergency.py            # Red-flag symptom triage & classification
│   └── requirements.txt            # Backend dependencies
├── frontend/                       # Next.js 14 Web Application
│   ├── src/
│   │   ├── app/                    # Chat UI & Navigation pages
│   │   ├── components/             # MicButton, AudioPlayer, CameraUI
│   │   ├── hooks/                  # useVoiceProcessor.js (Audio logic)
│   │   └── lib/                    # API client & Axios configurations
│   └── public/fonts/               # Noto Sans Ethiopic (Ge'ez support)
└── README.md                       # Project documentation
---
*Note: This is a medical prototype for hackathon purposes. Always consult a real doctor for medical emergencies.*