from dotenv import load_dotenv
import os, uuid

load_dotenv()

from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename
from file_handler import load_file
from vector_store import store_document, query_document, clear_vectors
from llm import ask_llm
from chat_memory import chat_memory

app = Flask(__name__)
app.secret_key = os.getenv("API_SECRET_KEY", "secret")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify(success=False, error="No file uploaded")

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        content = load_file(filepath)
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id
        session["filename"] = filename
        session["chat_history"] = []

        # Initialize chat memory for this session
        chat_memory.add_message(session_id, "system", f"Document '{filename}' has been uploaded and processed.")

        store_document(session_id, content)

        return jsonify(success=True, filename=filename)
    except Exception as e:
        error_message = str(e)
        
        # Handle rate limit errors with more helpful messages
        if "rate limit" in error_message.lower() or "429" in error_message:
            return jsonify(
                success=False, 
                error="Temporary rate limit reached. Please wait a moment and try again.",
                error_type="rate_limit"
            )
        else:
            return jsonify(success=False, error=error_message)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    session_id = session.get("session_id")

    if not session_id:
        return jsonify(success=False, error="No file loaded")

    try:
        # Get relevant context from document
        context = query_document(session_id, question)
        
        # Get conversation history for LLM context
        conversation_history = chat_memory.get_context_for_llm(session_id)
        
        # Ask LLM with context and conversation history
        answer = ask_llm(question, context, conversation_history)

        # Add user question and assistant response to chat memory
        chat_memory.add_message(session_id, "user", question)
        chat_memory.add_message(session_id, "assistant", answer)

        # Also maintain session-based chat history for compatibility
        if "chat_history" not in session:
            session["chat_history"] = []

        session["chat_history"].append({"type": "user", "content": question})
        session["chat_history"].append({"type": "assistant", "content": answer})
        session.modified = True

        return jsonify(success=True, answer=answer)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route("/get_chat_history")
def get_history():
    session_id = session.get("session_id")
    
    # Get both session-based and memory-based history
    session_history = session.get("chat_history", [])
    memory_history = chat_memory.get_conversation_history(session_id) if session_id else []
    
    return jsonify(
        success=True,
        chat_history=session_history,
        memory_history=memory_history,
        has_file="filename" in session,
        filename=session.get("filename"),
        session_summary=chat_memory.get_session_summary(session_id) if session_id else None
    )

@app.route("/export_conversation")
def export_conversation():
    session_id = session.get("session_id")
    if not session_id:
        return jsonify(success=False, error="No active session")
    
    conversation_json = chat_memory.export_conversation(session_id)
    return jsonify(success=True, conversation=conversation_json)

@app.route("/get_memory_stats")
def get_memory_stats():
    session_id = session.get("session_id")
    if not session_id:
        return jsonify(success=False, error="No active session")
    
    stats = chat_memory.get_session_summary(session_id)
    return jsonify(success=True, stats=stats)

@app.route("/clear", methods=["POST"])
def clear():
    session_id = session.pop("session_id", None)
    filename = session.pop("filename", None)
    session.pop("chat_history", None)

    if session_id:
        clear_vectors(session_id)
        chat_memory.clear_session(session_id)

    if filename:
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(path):
            try: os.remove(path)
            except: pass

    return jsonify(success=True)

@app.route("/clear_chat_only", methods=["POST"])
def clear_chat_only():
    session_id = session.get("session_id")
    if session_id:
        clear_vectors(session_id)
        chat_memory.clear_session(session_id)
    session.pop("chat_history", None)
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(debug=True)
