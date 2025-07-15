# ChatLok: RAG Model Demo

ChatLok is a Retrieval-Augmented Generation (RAG) demo application. It allows users to upload documents, process them into a vector store, and interact with a chatbot that leverages both LLM and document retrieval for more accurate responses.

## Features
- Upload PDF documents
- Store and search document embeddings
- Chat interface powered by LLM and retrieval
- Simple web UI

## Project Structure
```
ChatLok/
  app.py                # Main application entry point
  chat_memory.py        # Chat memory management
  file_handler.py       # File upload and processing
  llm.py                # LLM integration
  requirements.txt      # Python dependencies
  simple_vector_store.py# Simple vector store implementation
  vector_store.py       # Vector store logic
  static/               # Static files (JS, CSS, images)
  templates/            # HTML templates
  uploads/              # Uploaded files
```

## Setup Instructions
1. **Clone the repository**
2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```
3. **Run the application**
   ```powershell
   python app.py
   ```
4. **Open your browser** and go to `http://localhost:5000` (or the port shown in the terminal)

## Requirements
- Python 3.8+
- See `requirements.txt` for Python packages

## Usage

## License
This project is for educational/demo purposes.


## Requirements Explained

### Flask
- **Pros:** Simple, lightweight, easy to learn, flexible for small to medium web apps.
- **Cons:** Not as feature-rich as Django, may require extra setup for larger projects.

### python-dotenv
- **Pros:** Easy management of environment variables, keeps secrets out of code.
- **Cons:** Not secure by itself; secrets can still be exposed if .env is not protected.

### pandas
- **Pros:** Powerful data manipulation, supports many file formats, widely used in data science.
- **Cons:** Can be memory-intensive for very large datasets.

### python-docx
- **Pros:** Simple interface for reading/writing Word files, no need for Microsoft Office.
- **Cons:** Limited support for advanced Word features and formatting.

### PyMuPDF
- **Pros:** Fast PDF processing, supports text and image extraction, lightweight.
- **Cons:** Documentation can be sparse, some advanced PDF features may not be supported.

### openpyxl
- **Pros:** Reads/writes Excel files without Excel installed, supports many Excel features.
- **Cons:** Slower with very large files, limited to .xlsx format.

### cohere
- **Pros:** Easy access to powerful LLMs and embeddings, good documentation.
- **Cons:** Requires API key, usage may incur costs.

### chromadb
- **Pros:** Efficient vector search, easy to use for RAG and embedding storage.
- **Cons:** Still maturing, may lack some advanced features of larger vector DBs.

### requests
- **Pros:** Simple and intuitive HTTP library, widely used, good documentation.
- **Cons:** Not asynchronous, less suitable for high-concurrency needs.
