import asyncio
import time
from app.database import SessionLocal
from app.services.retrieval import RetrievalService

# Golden test queries
QUERIES = [
    # Answerable & single-hop
    {"query": "How do you know when it's time to leave your job?", "expected_topics": ["leave", "stuck", "career"]},
    
    # Deliberately unanswerable (out of domain)
    {"query": "How do I fix a broken refrigerator?", "expected_topics": []},
    
    # Multi-hop / Conceptual
    {"query": "What are the common mistakes first-time founders make?", "expected_topics": ["founder", "mistake"]},
]

async def run_eval():
    print("Starting Golden Eval...")
    db = SessionLocal()
    retriever = RetrievalService(db)
    
    total_latency = 0
    
    for i, q in enumerate(QUERIES):
        print(f"\n--- Query {i+1}: '{q['query']}' ---")
        start = time.time()
        
        try:
            results = await retriever.hybrid_search(q['query'], limit=3)
            latency = time.time() - start
            total_latency += latency
            
            print(f"Latency: {latency:.3f}s | Hits: {len(results)}")
            for j, res in enumerate(results):
                preview = res['text'][:100].replace('\n', ' ')
                print(f"  [{j+1}] ({res['speaker']} @ {res['timestamp']}) {preview}...")
                
        except Exception as e:
            print(f"Failed to retrieve: {e}")
            # Expected if Ollama/DB isn't running
            
    print(f"\nAvg Latency: {total_latency/len(QUERIES):.3f}s")
    db.close()

if __name__ == "__main__":
    asyncio.run(run_eval())
