"""
Idempotent Ingestion CLI.
Parses transcript markdown files, chunks them by speaker turns, checks content hashes,
and ingests new/modified documents into the vector database.
"""
import os
import glob
import yaml
import re
import hashlib
import asyncio
from app.database import SessionLocal
from app.models.knowledge import Document, Chunk
from app.services.embeddings import EmbeddingService

# Use a static regex from Phase 0 spike
SPEAKER_PATTERN = re.compile(r'^(.*?)\s*\((\d{2}:\d{2}:\d{2})\):\n', re.MULTILINE)

def hash_content(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def parse_transcript_file(file_path: str) -> tuple[dict, list[dict]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    metadata = {}
    body = content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            metadata = yaml.safe_load(parts[1]) or {}
            body = parts[2]
            
    matches = list(SPEAKER_PATTERN.finditer(body))
    chunks = []
    
    for i, match in enumerate(matches):
        speaker = match.group(1).strip()
        timestamp = match.group(2)
        start_idx = match.end()
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(body)
        text = body[start_idx:end_idx].strip()
        
        if len(text) > 5: # Skip empty/tiny chunks
            chunks.append({
                "speaker": speaker,
                "timestamp": timestamp,
                "text": text
            })
            
    return metadata, chunks, body

async def ingest_directory(directory_path: str):
    print(f"Starting ingestion from {directory_path}...")
    db = SessionLocal()
    embedder = EmbeddingService()
    
    files = glob.glob(os.path.join(directory_path, "*.md"))
    
    for file_path in files:
        filename = os.path.basename(file_path)
        guest_slug = filename.replace('.md', '')
        
        print(f"Processing {filename}...")
        try:
            metadata, chunks, raw_body = parse_transcript_file(file_path)
            content_hash = hash_content(raw_body)
            
            # Check idempotency
            existing_doc = db.query(Document).filter(Document.id == guest_slug).first()
            if existing_doc and existing_doc.content_hash == content_hash:
                print(f"  Skipping {filename} - no changes detected.")
                continue
                
            print(f"  Ingesting {len(chunks)} chunks for {filename}...")
            
            # Upsert Document
            if not existing_doc:
                doc = Document(
                    id=guest_slug,
                    guest_slug=guest_slug,
                    title=metadata.get("title", guest_slug),
                    content_hash=content_hash,
                    metadata_json=metadata
                )
                db.add(doc)
            else:
                existing_doc.content_hash = content_hash
                existing_doc.metadata_json = metadata
                existing_doc.title = metadata.get("title", guest_slug)
                
            db.commit()
            
            # Delete old chunks
            db.query(Chunk).filter(Chunk.document_id == guest_slug).delete()
            
            # Process and insert new chunks
            for i, chunk_data in enumerate(chunks):
                text_to_embed = f"Speaker: {chunk_data['speaker']}\nContent: {chunk_data['text']}"
                # Get embeddings from Ollama asynchronously
                try:
                    embedding = await embedder.get_embedding(text_to_embed)
                except Exception as e:
                    print(f"  Failed to embed chunk {i}: {e}. Skipping chunk.")
                    continue
                    
                chunk_record = Chunk(
                    id=f"{guest_slug}_{i}",
                    document_id=guest_slug,
                    chunk_index=i,
                    speaker=chunk_data['speaker'],
                    timestamp=chunk_data['timestamp'],
                    text=chunk_data['text'],
                    embedding=embedding
                )
                db.add(chunk_record)
                
            db.commit()
            print(f"  Successfully ingested {filename}.")
            
        except Exception as e:
            print(f"  Error processing {filename}: {e}")
            db.rollback()
            
    db.close()
    print("Ingestion complete.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest podcast transcripts.")
    parser.add_argument("--dir", type=str, default="transcripts", help="Directory containing markdown transcripts")
    args = parser.parse_args()
    
    asyncio.run(ingest_directory(args.dir))
