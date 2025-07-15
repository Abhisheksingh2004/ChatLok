import os, requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def ask_llm(question, context, conversation_history=None):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # Build messages array with detailed system prompt
    system_prompt = """
        You are ChatLok, an AI assistant that helps users answer questions about their uploaded documents.
        Use the provided document context to answer as accurately as possible.
        Use escape characters and **bold text** while answering.
        If the answer is not in the document, say so and avoid making things up.
        If the user communicates in another language, respond in only that language.
        """
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add current context and question
    messages.append({
        "role": "user", 
        "content": f"Context from document:\n{context}\n\nQuestion: {question}"
    })
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": messages,
        "temperature": 0.3
    }
    
    try:
        res = requests.post(GROQ_URL, headers=headers, json=payload)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"
