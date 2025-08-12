from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import openai
import chromadb
import re

app = Flask(__name__)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "quiz_knowledge"
QUESTIONS_PER_PAGE = 10
N_ANN = 4
MODEL = "gpt-4.1"
SYSTEM_PROMPT = "You are an expert in X. Answer based on the provided examples."
EMBEDDING_MODEL = "text-embedding-3-small"

def embed(text):
    response = openai.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

def format_question(text):
    # Insert a newline before each numbered option (e.g., " 1. ", " 2. ", etc.)
    return re.sub(r'(\s\d+\.\s)', r'\n\1', text)

@app.route('/get_new_answer', methods=['POST'])
def get_new_answer():
    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()

    if not question or not answer:
        return jsonify({"ok": False, "message": "Missing question or answer"}), 400

    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_or_create_collection(name=COLLECTION_NAME)

        # Check if the question already exists
        try:
            existing = collection.get(ids=[question])
            exists = len(existing.get('ids', [])) > 0
        except Exception:
            exists = False

        if exists:
            return jsonify({
                "ok": True,
                "exists": True,
                "message": f"The question already exists. Insert a different one."
            }), 200

        # embedding_vector = embed(question)
        embedding_vector = [0.0] * 1536
        collection.add(
            documents=[question],
            embeddings=[embedding_vector],
            metadatas=[{'response': answer}],
            ids=[question]
        )

        return jsonify({
            "ok": True,
            "exists": False,
            "message": f"Question saved."
        }), 201

    except Exception as e:
        return jsonify({"ok": False, "message": f"Error with ChromaDB: {e}"}), 500

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/questions')
def questions():
    page = int(request.args.get('page', 1))
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    try:
        results = collection.get()
        ids = results.get('ids', [])
        metadatas = results.get('metadatas', [])
        total = len(ids)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = []
        for i in range(start, min(end, total)):
            answer = metadatas[i].get('response', '') if i < len(metadatas) else ''
            questions.append((ids[i], answer))
        has_next = end < total
        has_prev = start > 0
        total_pages = (total + QUESTIONS_PER_PAGE - 1) // QUESTIONS_PER_PAGE
    except Exception:
        questions = []
        has_next = False
        has_prev = False
        total_pages = 1
    return render_template(
        'qdisplay.html',
        questions=questions,
        page=page,
        has_next=has_next,
        has_prev=has_prev,
        total_pages=total_pages
    )

@app.route('/delete_question', methods=['POST'])
def delete_question():
    question_id = request.form.get('question_id', '').strip()
    if not question_id:
        return jsonify({"ok": False, "message": "Missing question id"}), 400
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_or_create_collection(name=COLLECTION_NAME)
        collection.delete(ids=[question_id])
        return jsonify({"ok": True, "message": f"Question '{question_id}' deleted."}), 200
    except Exception as e:
        return jsonify({"ok": False, "message": f"Error deleting: {e}"}), 500

@app.route('/chat', methods=['GET'])
def chat_page():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def handle_chat():
    data = request.get_json()
    if not data or 'new_question' not in data:
        return jsonify({"error": "Missing 'new_question' field in request body"}), 400

    new_question = data['new_question']

    # Generate embedding for the new question
    embedding_new = embed(new_question)

    # Query ChromaDB for the most similar examples
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    results = collection.query(
        query_embeddings=[embedding_new],
        n_results=N_ANN
    )

    # Build dynamic prompt with ChromaDB results
    examples_text = ""
    similar_docs = results['documents'][0]
    similar_metas = results['metadatas'][0]

    for i, (doc, meta) in enumerate(zip(similar_docs, similar_metas), 1):
        formatted_q = format_question(doc)
        examples_text += f"#### {formatted_q}\n   Correct answer: {meta['response']}\n\n"

    formatted_new_q = format_question(new_question)

    prompt = f"""
### Reference Examples:
{examples_text}
### Current Task:
New question: {formatted_new_q}
Answer:"""

    # Call GPT with context
    try:
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT },
                {"role": "user", "content": prompt}
            ]
        )
        gpt_answer = response.choices[0].message.content
        return jsonify({"answer": gpt_answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)