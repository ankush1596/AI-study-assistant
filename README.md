# AI Study Assistant — Ready-to-Run Gen AI Project

A simple full-stack college project:
- PDF upload
- AI-generated summary
- Ask questions from the uploaded PDF
- Generate 5 MCQs with score/explanations
- Frontend: HTML/CSS/JavaScript
- Backend: Python Flask
- AI: OpenAI Responses API

## 1. Requirements

Install:
- Python 3.10+
- VS Code
- An OpenAI API key

## 2. Setup

Open this folder in VS Code, then open the terminal:

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and put your API key in it:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.6-luna
```

## 3. Run

```bash
python app.py
```

Open:

http://127.0.0.1:5000

## 4. Demo flow

1. Upload a text-based PDF.
2. Click "Generate Summary".
3. Click "Ask a Question".
4. Click "Generate 5 MCQs".
5. Check the score.

## Notes

- This demo stores uploaded documents in server memory. Restarting the server clears them.
- Scanned/image-only PDFs are not supported by the basic version because they need OCR.
- Never upload your `.env` or API key to GitHub.
