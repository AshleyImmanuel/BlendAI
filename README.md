# BlendAI: Autonomous Agent Swarm for Blender (v1.7.0)

> [!CAUTION]
> **LEGAL DISCLAIMER & RISK WARNING**: Use this tool at your own risk. The author (Ashley Immanuel) is not responsible for any scene corruption, data loss, or technical issues that may arise from using this software. **Sorry for any trouble this experimental project may cause.** It was built as a rapid "One-Day Sprint" and is currently unverified by the author in a production environment.

> [!WARNING]
> **AUTHOR'S NOTE OF UNCERTAINTY**: The creator has not yet manually loaded the UI or executed AI scripts within Blender. All "Green Light" status is currently based on automated AI-driven verification (Titanium 32-suite audit).

---

**BlendAI** is a production-grade, multi-agent autonomous swarm integrated directly into Blender. It transforms complex 3D modeling, texturing, and lighting tasks into simple natural language conversations.

![BlendAI Logo](file:///C:/Users/Ashley%20Immanuel/.gemini/antigravity/brain/e28cd90f-fdf4-4eac-8100-de4049af4fc4/blendai_ui_mockup_1776112832356.png)

---

## 🎖️ Contributors Wanted!
This is a **One-Day Challenge Project**. I would be happy for anyone to help me field-test this tool! If you are a Blender developer, AI enthusiast, or 3D artist, your feedback, bug reports, and pull requests are extremely welcome. Help me turn this experimental swarm into a production standard.

---

## The One-Click Experience (v1.7.0 Optimized)
BlendAI manages its own lifecycle directly from the Blender interface. 

1. **Install**: Install `blender_ai_agent.py` as a standard Blender addon.
2. **Configure**: Navigate to `Edit > Preferences > Addons > BlendAI`.
3. **Prepare**: Click **"Prepare Environment"** (Installs fastapi, uvicorn, requests, etc.).
4. **Launch**: Click **"Launch AI Backend"** (Starts the local swarm on port 8000).

---

## 🛡️ v1.7.0 Features
- **Privacy First: Local AI Support**: Support for **Ollama**, **LM Studio**, and **Groq**. Just change the "API Base URL" in settings. Use your own hardware for $0.00 usage cost.
- **Shielded Swarm Architecture**: Multi-layer defense against **Prompt Injection** and **Data Poisoning**.
- **Non-Destructive Evolution**: Swarm saves new versions of skills (`_v2`, `_v3`) without overwriting your originals.
- **Pro Skill Library**: Foldered repository (`backend/skills/`) pre-loaded with lighting and material experts.
- **High-Speed Caching**: MTime-aware disk caching for near-instant mission planning.
- **Persistent Memory**: Contextual session history stored in Markdown (`backend/memory/`).
- **Professional Auditing**: Centralized technical logging in `blendai_swarm.log`.

---

## 🏠 Running Locally (Ollama)
For 100% private, zero-cost AI:
- **Endpoint**: Set your "API Base URL" to `http://localhost:11434/v1`.
- **Key**: You still need to enter a placeholder string in the "API Key" field to satisfy the system.
- **Model**: Matches your local model name (e.g., `llama3`, `mistral`).

---

## Requirements
- Blender 3.0+
- OpenAI-compatible API Key (OpenAI, Groq, DeepSeek, etc.)
- Python 3.10+ (Standard with modern Blender)

---

## 📬 Contact & Community
This is a community-driven project. If you encounter bugs, have architectural suggestions, or wish to collaborate, please reach out:

- **Email**: [immanuelashley77@gmail.com](mailto:immanuelashley77@gmail.com)
- **LinkedIn**: [Ashley Immanuel](https://www.linkedin.com/in/ashley-immanuel-81609731b/)
- **Issues**: Please open an issue on the GitHub repository for technical bug tracking.

---

## ⚖️ Licensing
Licensed under the **MIT License**.
Copyright (c) 2026 **Ashley Immanuel**.
See [LICENSE](file:///d:/BlendPlugin/LICENSE) for full details.

---
*Verified Production Release [v1.7.0] - The Shielded Swarm*
