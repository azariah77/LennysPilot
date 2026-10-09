from sqlalchemy.orm import Session
from sqlalchemy import text
from app.services.embeddings import EmbeddingService

class RetrievalService:
    def __init__(self, db: Session):
        self.db = db
        self.embedder = EmbeddingService()
        
    async def hybrid_search(self, query: str, limit: int = 5, vector_weight: float = 0.7):
        """
        Perform a hybrid search using TSVECTOR (full-text) and pgvector (semantic).
        Merges results using Reciprocal Rank Fusion (RRF).
        """
        query_embedding = await self.embedder.get_embedding(query)
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        # We use a raw SQL query for the RRF to execute everything in one go inside Postgres.
        # This requires both tsvector matches and vector proximity.
        # 
        # RRF formula: score = 1 / (k + rank)
        
        sql = text("""
        WITH semantic_search AS (
            SELECT id,
                   1 - (embedding <=> :embedding) AS vector_score,
                   row_number() OVER (ORDER BY embedding <=> :embedding) AS rank
            FROM chunks
            ORDER BY embedding <=> :embedding
            LIMIT 50
        ),
        keyword_search AS (
            SELECT id,
                   ts_rank_cd(search_vector, plainto_tsquery('english', :query)) AS keyword_score,
                   row_number() OVER (ORDER BY ts_rank_cd(search_vector, plainto_tsquery('english', :query)) DESC) AS rank
            FROM chunks
            WHERE search_vector @@ plainto_tsquery('english', :query)
            ORDER BY keyword_score DESC
            LIMIT 50
        )
        SELECT 
            COALESCE(s.id, k.id) AS chunk_id,
            COALESCE(1.0 / (60 + s.rank), 0.0) * :vector_weight + 
            COALESCE(1.0 / (60 + k.rank), 0.0) * (1.0 - :vector_weight) AS rrf_score
        FROM semantic_search s
        FULL OUTER JOIN keyword_search k ON s.id = k.id
        ORDER BY rrf_score DESC
        LIMIT :limit
        """)
        
        results = self.db.execute(sql, {
            "embedding": embedding_str,
            "query": query,
            "vector_weight": vector_weight,
            "limit": limit
        }).fetchall()
        
        # Fetch the actual chunk data for the top IDs
        chunk_ids = [row.chunk_id for row in results]
        
        if not chunk_ids:
            return []
            
        # We need to maintain the order from RRF
        placeholders = ','.join([f"'{cid}'" for cid in chunk_ids])
        
        fetch_sql = text(f"""
            SELECT c.id, c.document_id, c.speaker, c.timestamp, c.text, d.title
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE c.id IN ({placeholders})
        """)
        
        chunks = self.db.execute(fetch_sql).fetchall()
        
        # Sort chunks back to RRF order
        chunk_dict = {c.id: dict(c._mapping) for c in chunks}
        ordered_chunks = [chunk_dict[cid] for cid in chunk_ids if cid in chunk_dict]
        
        return ordered_chunks
