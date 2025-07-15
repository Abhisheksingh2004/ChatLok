import os, pandas as pd, fitz, sqlite3
from docx import Document

def load_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return "\n".join([p.get_text() for p in fitz.open(path)])
    elif ext == ".docx":
        return "\n".join(p.text for p in Document(path).paragraphs)
    elif ext == ".txt" or ext == ".sql":
        return open(path, encoding="utf-8", errors="ignore").read()
    elif ext in [".csv", ".xlsx", ".xls"]:
        df = pd.read_csv(path) if ext == ".csv" else pd.read_excel(path)
        return df.to_string()
    elif ext == ".db":
        return extract_db(path)
    return "Unsupported file type"

def extract_db(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    result = ""
    for t in tables:
        df = pd.read_sql_query(f"SELECT * FROM {t[0]} LIMIT 10", conn)
        result += f"\nTable: {t[0]}\n{df.to_string()}\n"
    conn.close()
    return result
