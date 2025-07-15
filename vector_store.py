import chromadb
import os
import time

# Set the CHROMA_COHERE_API_KEY environment variable from COHERE_API_KEY before importing
cohere_key = os.getenv("COHERE_API_KEY")
if cohere_key:
    os.environ["CHROMA_COHERE_API_KEY"] = cohere_key

from chromadb.utils.embedding_functions import CohereEmbeddingFunction

# Use Cohere embeddings
embed_fn = CohereEmbeddingFunction(api_key=cohere_key)
chroma_client = chromadb.Client()
collections = {}

def store_document(session_id, content):
    """Store document efficiently using Cohere embeddings"""
    # Use reasonable chunk size for better performance
    chunks = [content[i:i+800] for i in range(0, len(content), 800)]
    collection = chroma_client.get_or_create_collection(session_id, embedding_function=embed_fn)
    collections[session_id] = collection
    
    # Process chunks in reasonable batches
    batch_size = 10  # Process 10 chunks at a time
    
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i+batch_size]
        batch_ids = [f"{session_id}_{j}" for j in range(i, min(i + batch_size, len(chunks)))]
        
        try:
            collection.add(documents=batch_chunks, ids=batch_ids)
            
            # Small delay only for very large batches
            if len(chunks) > 50 and i + batch_size < len(chunks):
                time.sleep(0.5)  # Minimal delay only for large documents
                
        except Exception as e:
            if "rate limit" in str(e).lower() or "429" in str(e):
                print(f"Rate limit encountered, waiting briefly...")
                time.sleep(5)  # Wait 5 seconds on rate limit
                # Retry the batch once
                try:
                    collection.add(documents=batch_chunks, ids=batch_ids)
                except Exception as retry_error:
                    print(f"Failed to process batch after retry: {retry_error}")
                    raise retry_error
            else:
                raise e

def query_document(session_id, query):
    collection = collections.get(session_id)
    if not collection: return ""
    result = collection.query(query_texts=[query], n_results=3)
    return "\n".join(result["documents"][0]) if result["documents"] else ""

def clear_vectors(session_id):
    if session_id in collections:
        chroma_client.delete_collection(session_id)
        collections.pop(session_id, None)
