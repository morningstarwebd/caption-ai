# Contributing to Caption AI

First off, thank you for considering contributing to Caption AI! Every contribution helps make video captioning more accessible to everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Project Structure](#project-structure)

---

## Code of Conduct

This project follows a simple rule: **be kind and respectful**. We're all here to build something useful together. Harassment, discrimination, or disrespectful behavior won't be tolerated.

---

## How Can I Contribute?

### 🐛 Report Bugs

Found a bug? [Open an issue](https://github.com/morningstarweb/caption-ai/issues/new?template=bug_report.md) with:
- Clear, descriptive title
- Steps to reproduce the problem
- Expected vs actual behavior
- Your OS, Python version, and Node version
- Relevant logs (check `storage/logs/` if available)

### 💡 Suggest Features

Have an idea? [Open a feature request](https://github.com/morningstarweb/caption-ai/issues/new?template=feature_request.md) and describe:
- The problem it would solve
- Your proposed solution
- Any alternatives you've considered

### 🔧 Submit Code

1. **Check existing issues** — avoid duplicate work
2. **Discuss major changes** in an issue first before coding
3. **Small, focused PRs** are easier to review than large ones

---

## Development Setup

### Backend (Python)

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/caption-ai.git
cd caption-ai

# Create virtual environment (Python 3.10+ required)
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your GROQ_API_KEY to .env

# Run backend
python -m server.main
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

### Verify Setup

- Backend: http://localhost:8000/api/health → `{"status":"ok","version":"5.0.0"}`
- Frontend: http://localhost:3000

---

## Pull Request Process

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** with clear, logical commits
4. **Test** your changes locally (backend runs, frontend renders, no console errors)
5. **Commit** with descriptive messages:
   - `feat: add Tamil language support`
   - `fix: correct alignment drift for short segments`
   - `docs: update API reference for export endpoint`
6. **Push** to your fork: `git push origin feature/your-feature-name`
7. **Open a PR** against `main` with:
   - Description of what changed and why
   - Link to related issue (if any)
   - Screenshots/recordings for UI changes

### PR Review

- Maintainers will review within a few days
- Address feedback promptly
- PRs need at least one approval before merge

---

## Code Style

### Python (Backend + AI Pipeline)

- Follow **PEP 8** conventions
- Use meaningful variable and function names in English
- Add docstrings for public functions in `ai_pipeline/` modules
- Type hints encouraged but not required
- Use `logging` module (not `print()`) for debug output

```python
# Good
def compute_dual_score(raw_text: str, refined_text: str) -> float:
    """Compute combined semantic + keyword similarity score."""
    ...

# Avoid
def score(t1, t2):
    print("scoring...")
    ...
```

### TypeScript / React (Frontend)

- Follow **ESLint** configuration (already set up)
- Use **Tailwind CSS** for styling — no inline styles or CSS modules
- Components go in `frontend/src/components/editor/`
- State management via **Zustand** stores in `frontend/src/store/`
- Types defined in `frontend/src/lib/types.ts`

```tsx
// Good — typed props, Tailwind classes
export default function CaptionBlock({ caption }: { caption: Caption }) {
  return <div className="p-2 rounded bg-white/5">{caption.text}</div>;
}
```

### Commits

- Use [Conventional Commits](https://www.conventionalcommits.org/) format:
  - `feat:` — new feature
  - `fix:` — bug fix
  - `docs:` — documentation only
  - `refactor:` — code change that neither fixes a bug nor adds a feature
  - `perf:` — performance improvement
  - `test:` — adding tests

---

## Project Structure

| Directory | Description | Language |
|-----------|-------------|----------|
| `ai_pipeline/` | 15-step AI captioning engine | Python |
| `server/` | FastAPI backend + database | Python |
| `server/api/` | REST + WebSocket endpoints | Python |
| `frontend/src/app/` | Next.js pages & layout | TypeScript |
| `frontend/src/components/editor/` | 12 editor UI components | TypeScript |
| `frontend/src/store/` | Zustand state stores | TypeScript |
| `frontend/src/hooks/` | Custom React hooks | TypeScript |
| `frontend/src/lib/` | API client, types, utilities | TypeScript |

### Key Files for New Contributors

- **Add a new language**: `ai_pipeline/config.py` (thresholds), `ai_pipeline/transcriber.py` (ASR), `frontend/src/lib/types.ts` (Language type)
- **Add a caption theme**: `frontend/src/lib/types.ts` (CAPTION_THEMES)
- **Add an API endpoint**: `server/api/` (new router or extend `jobs.py`)
- **Add a pipeline step**: `ai_pipeline/` (new module + integrate in `main.py`)

---

## Questions?

- Open a [Discussion](https://github.com/morningstarweb/caption-ai/discussions) for general questions
- Open an [Issue](https://github.com/morningstarweb/caption-ai/issues) for bugs or feature requests

Thank you for helping make Caption AI better! 🎬
