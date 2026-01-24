# ArchitX - Multi-Agent PRD Generator

A multi-agentic system using Microsoft AutoGen that transforms project ideas into comprehensive Product Requirements Documents (PRDs) through AI-powered clarification, expert debates, and judicial review.

## Features

- **Smart Clarification**: AI asks targeted questions to understand your project vision
- **Expert Debate**: 13+ specialized agents (Architect, Security, DevOps, UX, etc.) debate the best approaches
- **Judicial Review**: 3 judges evaluate business viability, technical soundness, and feasibility
- **Real-time Streaming**: Watch the AI agents discuss in real-time via Server-Sent Events
- **Comprehensive Output**: Download a ZIP with PRD, transcripts, and structured exports

## Tech Stack

- **Backend**: Python + FastAPI + AutoGen
- **Frontend**: Vue 3 + Vite + TailwindCSS (Dark mode)
- **Real-time**: Server-Sent Events (SSE)
- **LLM**: OpenAI GPT-4o

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Visit http://localhost:5173 to access the application.

## Project Structure

```
ArchitX/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration
│   │   ├── api/routes/          # API endpoints
│   │   ├── agents/              # AutoGen agent definitions
│   │   │   ├── definitions.py   # Agent system prompts
│   │   │   ├── teams.py         # GroupChat configurations
│   │   │   └── orchestrator.py  # Workflow controller
│   │   ├── services/            # Business logic
│   │   └── models/              # Pydantic models
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── views/               # Vue page components
│   │   ├── components/          # Reusable components
│   │   ├── composables/         # Vue composables
│   │   ├── stores/              # Pinia stores
│   │   └── services/            # API client
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## User Flow

1. **Landing**: Enter your project idea
2. **Configure**: Select expert agents (2-6) and debate rounds (3-10)
3. **Clarify**: Answer AI-generated questions about your project
4. **Debate**: Watch experts discuss architecture, security, UX, and more
5. **Judge**: View scores from Business, Technical, and Feasibility judges
6. **Download**: Get your complete PRD package as a ZIP file

## Available Agents

### Debate Agents (User-selectable)
| Agent | Focus Area |
|-------|------------|
| Architect | System design, scalability, patterns |
| DevOps | CI/CD, infrastructure, monitoring |
| Security | Auth, encryption, compliance |
| UX | User experience, accessibility |
| QA | Testing strategies, quality gates |
| Product Manager | User stories, roadmap |
| Data Engineer | Pipelines, storage, ETL |
| ML Engineer | Models, training, MLOps |
| Frontend Dev | UI frameworks, performance |
| Backend Dev | APIs, databases, caching |
| Mobile Dev | iOS/Android, cross-platform |
| Business Analyst | Requirements, ROI |
| Tech Lead | Code quality, practices |

### Judge Agents
- **Business Judge**: Market fit, value prop, revenue potential
- **Technical Judge**: Architecture, scalability, security
- **Feasibility Judge**: Resources, timeline, risks

## API Endpoints

```
POST   /api/v1/sessions                   # Create session
GET    /api/v1/sessions/{id}              # Get session status
POST   /api/v1/sessions/{id}/idea         # Submit project idea
GET    /api/v1/sessions                   # List available agents
POST   /api/v1/sessions/{id}/config       # Configure agents & rounds
GET    /api/v1/sessions/{id}/clarify/stream   # SSE: Clarification
POST   /api/v1/sessions/{id}/answers      # Submit answers
GET    /api/v1/sessions/{id}/debate/stream    # SSE: Debate
GET    /api/v1/sessions/{id}/judge/stream     # SSE: Evaluation
GET    /api/v1/sessions/{id}/download     # Download ZIP
```

## Configuration

Edit `backend/.env` to customize:

```env
# LLM
OPENAI_API_KEY=your_key_here
MODEL_NAME=gpt-4o

# Debate
DEFAULT_DEBATE_ROUNDS=5
MAX_DEBATE_ROUNDS=15
MAX_CLARIFICATION_ROUNDS=10

# Storage
STORAGE_PATH=./sessions
```

## Output Structure

The generated ZIP contains:

```
prd_{session_id}.zip
├── README.md
├── PRD.md
├── original_prompt.txt
├── transcripts/
│   ├── clarification.md
│   ├── debate.md
│   └── review.md
├── metadata/
│   ├── session.json
│   └── scores.json
└── exports/
    ├── requirements.json
    └── decisions.json
```

## Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

### Building for Production

```bash
# Frontend
cd frontend
npm run build

# Backend (using Docker)
docker build -t architx-backend .
```

## License

MIT License - see LICENSE file for details.

---

Built with AutoGen + GPT-4o
