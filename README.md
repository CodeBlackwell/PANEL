# 🏛️ ArchitX

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white)](https://python.org)
[![Vue 3](https://img.shields.io/badge/Vue-3-4fc08d?logo=vuedotjs&logoColor=white)](https://vuejs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![AutoGen](https://img.shields.io/badge/AutoGen-Powered-ff6b35)](https://microsoft.github.io/autogen/)

> **Multi-agent AI system that transforms project ideas into comprehensive PRDs through expert debates and judicial review.**

---

## 📑 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Usage Example](#-usage-example)
- [Project Structure](#-project-structure)
- [Agents](#-agents)
- [API Reference](#-api-reference)
- [Configuration](#-configuration)
- [Output](#-output)
- [Development](#-development)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Smart Clarification** | AI asks targeted questions to understand your vision |
| 💬 **Expert Debate** | 13+ specialized agents debate best approaches |
| ⚖️ **Judicial Review** | 3 judges score business, technical & feasibility |
| 📡 **Real-time Streaming** | Watch agents discuss live via SSE |
| 📦 **Complete Output** | Download PRD + transcripts + exports as ZIP |

**Tech Stack:** Python + FastAPI + AutoGen | Vue 3 + Vite + Tailwind | OpenAI GPT-4o

---

## 🚀 Quick Start

**Prerequisites:** Python 3.10+ • Node.js 18+ • [Just](https://github.com/casey/just) • OpenAI API key

```bash
git clone https://github.com/yourusername/ArchitX.git
cd ArchitX
just setup              # Install all dependencies
# Edit backend/.env and add your OPENAI_API_KEY
just dev                # Start backend + frontend
```

**Open:** http://localhost:5173

<details>
<summary>Manual setup (without Just)</summary>

```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt && cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```
</details>

---

## 💡 Usage Example

```
1. Enter idea     →  "A marketplace for local farmers to sell directly to restaurants"
2. Configure      →  Select agents: Architect, Security, Backend Dev, UX
                     Debate rounds: 5
3. Clarify        →  Answer questions about target users, scale, budget
4. Watch debate   →  Agents discuss architecture, security, UX trade-offs
5. View scores    →  Business: 8/10 | Technical: 9/10 | Feasibility: 7/10
6. Download       →  Get PRD.md + transcripts + requirements.json
```

**Sample output in** `examples/prds/`

---

## 🏗️ Project Structure

```
ArchitX/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry
│   │   ├── agents/              # AutoGen definitions
│   │   │   ├── definitions.py   # Agent prompts
│   │   │   ├── teams.py         # GroupChat configs
│   │   │   └── orchestrator.py  # Workflow control
│   │   ├── api/routes/          # Endpoints
│   │   └── services/            # Business logic
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── views/               # Page components
│       ├── components/          # UI components
│       └── stores/              # Pinia state
├── agents/                      # Agent definitions
└── examples/prds/               # Sample outputs
```

---

## 🤖 Agents

### Debate Agents (select 2-6)

| Agent | Focus | Agent | Focus |
|-------|-------|-------|-------|
| 🏗️ Architect | System design, patterns | 🔐 Security | Auth, compliance |
| ⚙️ DevOps | CI/CD, infrastructure | 🎨 UX | Experience, a11y |
| 🧪 QA | Testing, quality | 📋 Product Manager | Stories, roadmap |
| 🗄️ Data Engineer | Pipelines, ETL | 🤖 ML Engineer | Models, MLOps |
| 🖥️ Frontend Dev | UI, performance | ⚡ Backend Dev | APIs, caching |
| 📱 Mobile Dev | iOS/Android | 📊 Business Analyst | Requirements, ROI |
| 👨‍💻 Tech Lead | Code quality | | |

### Judge Agents

| ⚖️ Business | ⚖️ Technical | ⚖️ Feasibility |
|-------------|--------------|----------------|
| Market fit, revenue | Architecture, security | Resources, timeline, risks |

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/sessions` | Create session |
| `GET` | `/api/v1/sessions/{id}` | Get status |
| `POST` | `/api/v1/sessions/{id}/idea` | Submit idea |
| `POST` | `/api/v1/sessions/{id}/config` | Configure agents |
| `GET` | `/api/v1/sessions/{id}/clarify/stream` | SSE: Clarification |
| `POST` | `/api/v1/sessions/{id}/answers` | Submit answers |
| `GET` | `/api/v1/sessions/{id}/debate/stream` | SSE: Debate |
| `GET` | `/api/v1/sessions/{id}/judge/stream` | SSE: Evaluation |
| `GET` | `/api/v1/sessions/{id}/download` | Download ZIP |

---

## ⚙️ Configuration

Edit `backend/.env`:

```env
OPENAI_API_KEY=your_key_here
MODEL_NAME=gpt-4o
DEFAULT_DEBATE_ROUNDS=5
MAX_DEBATE_ROUNDS=15
STORAGE_PATH=./sessions
```

---

## 📦 Output

Generated ZIP structure:

```
prd_{session_id}.zip
├── PRD.md                    # Final document
├── original_prompt.txt       # Your idea
├── transcripts/
│   ├── clarification.md      # Q&A phase
│   ├── debate.md             # Expert discussion
│   └── review.md             # Judge evaluations
├── metadata/
│   └── scores.json           # Numeric scores
└── exports/
    ├── requirements.json     # Structured reqs
    └── decisions.json        # Key decisions
```

---

## 🛠️ Development

```bash
just test               # Run all tests
just build              # Production frontend build
just help               # List all commands
```

| Recipe | Description |
|--------|-------------|
| `just dev` | Run backend + frontend |
| `just backend` | Backend only |
| `just frontend` | Frontend only |
| `just test` | Run all tests |
| `just build` | Production build |
| `just clean` | Remove generated files |

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with <a href="https://microsoft.github.io/autogen/">AutoGen</a> + GPT-4o
</p>
