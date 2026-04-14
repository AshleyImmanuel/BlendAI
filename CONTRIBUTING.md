# Contributing to BlendAI

Welcome! We are thrilled that you want to help make BlendAI the best assistant for Blender. As an experimental project, community feedback and contributions are our lifeblood.

## 🎖️ Ways to Help
- **Testing**: Use the addon in your daily Blender workflows and report bugs or UX friction.
- **Agent Prompts**: Help us refine the specialized agent instructions in `backend/agents/specialized_agents.py`.
- **UI/UX**: Suggest improvements for the React-based Assistant UI.
- **Safety**: Help us audit the `SafetyGuard` and suggest new whitelisting patterns.

## 🛠️ Local Development
1. Clone the repository.
2. **Backend**: Install dependencies (`pip install fastapi uvicorn openai`) and run `python backend/main.py`.
3. **Frontend**: Install Node.js, run `npm install` and `npm run dev` in the `frontend` folder.
4. **Blender**: Install `blender_ai_agent.py` and point it to your local backend.

## 🧪 Running Tests
Prior to any Pull Request, please run the full audit to ensure no regressions:
```powershell
python backend/run_tests.py
```

## 📬 Communication
If you have big ideas, feel free to reach out to Ashley Immanuel via the contact info in the README or open an Issue.

Thank you for helping us evolve!
