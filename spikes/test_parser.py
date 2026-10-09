import yaml
import re

def parse_transcript(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            metadata_str = parts[1]
            body = parts[2]
            
            metadata = yaml.safe_load(metadata_str)
            print("--- METADATA ---")
            for k, v in metadata.items():
                val_str = str(v).encode('ascii', 'replace').decode('ascii')
                print(f"{k}: {val_str}")
            print("\n--- BODY ---")
            
            # Now let's extract speaker chunks
            # Format is: Speaker Name (HH:MM:SS):
            speaker_pattern = re.compile(r'^(.*?)\s*\((\d{2}:\d{2}:\d{2})\):\n', re.MULTILINE)
            chunks = []
            
            matches = list(speaker_pattern.finditer(body))
            for i, match in enumerate(matches):
                speaker = match.group(1).strip()
                timestamp = match.group(2)
                
                start_idx = match.end()
                end_idx = matches[i+1].start() if i + 1 < len(matches) else len(body)
                
                text = body[start_idx:end_idx].strip()
                chunks.append({
                    "speaker": speaker,
                    "timestamp": timestamp,
                    "text": text
                })
            
            print(f"Found {len(chunks)} speaker turns.")
            if chunks:
                print(f"First chunk: {chunks[0]['speaker']} [{chunks[0]['timestamp']}] -> {chunks[0]['text'][:50]}...")
            
    else:
        print("No frontmatter found.")

if __name__ == '__main__':
    parse_transcript('c:/Users/sanzy/Lenozen/spikes/sample_transcript.md')
