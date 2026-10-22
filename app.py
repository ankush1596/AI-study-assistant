import os
import json
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__, static_folder="static")
CORS(app)

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

documents = {}

def ask_ai(prompt):
    if client is None:
        raise RuntimeError(
            "GEMINI_API_KEY .env file mein set nahi hai."
        )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text or ""

@app.get("/")
def home():
    return send_from_directory("static", "index.html")

@app.post("/api/upload")
def upload():
    if "file" not in request.files:
        return jsonify(error="No file uploaded"), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify(error="Please upload a PDF file."), 400

    try:
        reader = PdfReader(file)
        text = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    except Exception as e:
        return jsonify(error=f"Could not read PDF: {e}"), 400

    if not text:
        return jsonify(error="This PDF has no selectable text. Please use a text-based PDF."), 400

    doc_id = str(uuid.uuid4())
    # Keep a reasonable amount for a college demo.
    documents[doc_id] = text[:120000]

    return jsonify(
        document_id=doc_id,
        filename=file.filename,
        pages=len(reader.pages),
        characters=len(text)
    )

@app.post("/api/summary")
def summary():
    data = request.get_json(force=True)
    text = documents.get(data.get("document_id"))
    if not text:
        return jsonify(error="Document not found. Upload the PDF again."), 404

    prompt = f"""
You are an AI Study Assistant.
Create a clear student-friendly summary of the following study material.

Requirements:
- Give a short overview first.
- Use headings and bullet points.
- Explain important concepts in simple language.
- Include key definitions, formulas, dates or facts if present.
- End with 5 important exam points.
Do not invent information.

STUDY MATERIAL:
{text}
"""
    try:
        return jsonify(answer=ask_ai(prompt))
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.post("/api/ask")
def ask():
    data = request.get_json(force=True)
    text = documents.get(data.get("document_id"))
    question = (data.get("question") or "").strip()

    if not text:
        return jsonify(error="Document not found. Upload the PDF again."), 404
    if not question:
        return jsonify(error="Enter a question."), 400

    prompt = f"""
You are an AI Study Assistant answering only from the supplied study material.
Answer the student's question accurately and in simple language.
If the answer is not present in the material, clearly say:
"I couldn't find this in the uploaded material."
Do not make up facts.

STUDY MATERIAL:
{text}

STUDENT QUESTION:
{question}
"""
    try:
        return jsonify(answer=ask_ai(prompt))
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.post("/api/mcq")
def mcq():
    data = request.get_json(force=True)
    text = documents.get(data.get("document_id"))
    count = int(data.get("count", 5))
    count = max(3, min(count, 10))

    if not text:
        return jsonify(error="Document not found. Upload the PDF again."), 404

    prompt = f"""
You are an AI Study Assistant.
Create exactly {count} multiple-choice questions from the supplied study material.

Return ONLY valid JSON in this format:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": ["A", "B", "C", "D"],
      "answer": 0,
      "explanation": "Short explanation"
    }}
  ]
}}

Rules:
- answer is the zero-based index of the correct option.
- Questions must be based only on the material.
- Avoid duplicate questions.
- Make the questions useful for exam preparation.

STUDY MATERIAL:
{text}
"""
    try:
        raw = ask_ai(prompt)
        # Strip accidental markdown fences.
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            raw = raw.rsplit("```", 1)[0]
        return jsonify(**json.loads(raw))
    except Exception as e:
        return jsonify(error=f"Could not generate quiz: {e}"), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)

