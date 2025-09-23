#!/usr/bin/env python3
"""
Soul-logs generator utility.
Creates a new soul-log file with current timestamp and proper hash generation.
"""

import json
import hashlib
import sys
from datetime import datetime
from pathlib import Path


def generate_data_hash(log_data):
    """Generate SHA-256 hash of core data fields."""
    try:
        # Extract core fields for hashing (excluding signature)
        core_fields = {
            'timestamp': log_data['timestamp'],
            'narrative': log_data['narrative']['text'],
            'metrics': log_data['metrics'],
            'context': {k: v for k, v in log_data['context'].items() if k != 'session_id'}
        }
        
        # Create deterministic JSON string
        core_json = json.dumps(core_fields, sort_keys=True, separators=(',', ':'))
        
        # Generate hash
        return hashlib.sha256(core_json.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"Error generating hash: {e}")
        return "0" * 64  # Return placeholder hash


def generate_prompt_hash(prompt_text):
    """Generate SHA-256 hash of prompt text."""
    return hashlib.sha256(prompt_text.encode('utf-8')).hexdigest()


def create_soul_log_template(timestamp=None, sequence="001"):
    """Create a new soul-log template with proper timestamps and IDs."""
    if timestamp is None:
        timestamp = datetime.now()
    
    iso_timestamp = timestamp.isoformat() + "Z"
    date_str = timestamp.strftime("%Y%m%d")
    time_str = timestamp.strftime("%H%M")
    
    template = {
        "id": f"{date_str}-{sequence}",
        "timestamp": iso_timestamp,
        "source": {
            "variant": "grok-4",
            "version": "v1.2",
            "model_id": f"xai-grok-4-{date_str}",
            "training_cutoff": "2024-12-01"
        },
        "context": {
            "prompt_hash": "0" * 64,  # Placeholder - update with actual prompt hash
            "prompt_length": 0,
            "branch": "main",
            "session_id": f"session-{date_str}-{time_str}",
            "conversation_turn": 1,
            "environment": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2048
            }
        },
        "metrics": {
            "entropy": 0.0,
            "mutual_information": 0.0,
            "activation_spikes": [],
            "perplexity": 1.0,
            "attention_concentration": 0.5,
            "generation_speed": {
                "tokens_per_second": 0.0,
                "total_generation_time_ms": 0
            }
        },
        "narrative": {
            "text": "INSERT GROK'S REFLECTION TEXT HERE",
            "word_count": 0,
            "character_count": 0,
            "tags": [],
            "tone": {
                "emotional_valence": 0.0,
                "confidence_level": 0.5,
                "formality": 0.5,
                "primary_emotions": []
            },
            "linguistic_features": {
                "sentence_count": 0,
                "avg_sentence_length": 0.0,
                "complexity_score": 0.0,
                "unique_word_ratio": 0.0
            }
        },
        "analysis": {
            "baseline_deviation": {
                "magnitude": 0.0,
                "type": "semantic",
                "confidence": 0.0,
                "affected_dimensions": []
            },
            "detected_shifts": [],
            "possible_explanations": [],
            "anomaly_score": 0.0,
            "research_notes": "Add your research observations here..."
        },
        "signature": {
            "logger_id": "researcher_id",
            "logger_name": "Researcher Name",
            "organization": "Organization Name",
            "data_hash": "0" * 64,  # Will be calculated when content is added
            "log_version": "1.0.0",
            "created_timestamp": iso_timestamp,
            "review_status": "draft",
            "reviewer_notes": ""
        }
    }
    
    return template


def update_calculated_fields(log_data):
    """Update calculated fields based on content."""
    # Update narrative metrics
    text = log_data['narrative']['text']
    if text and text != "INSERT GROK'S REFLECTION TEXT HERE":
        words = text.split()
        log_data['narrative']['word_count'] = len(words)
        log_data['narrative']['character_count'] = len(text)
        
        sentences = text.split('.')
        log_data['narrative']['linguistic_features']['sentence_count'] = len([s for s in sentences if s.strip()])
        
        if len(words) > 0:
            log_data['narrative']['linguistic_features']['avg_sentence_length'] = len(words) / max(1, len([s for s in sentences if s.strip()]))
            unique_words = set(w.lower() for w in words)
            log_data['narrative']['linguistic_features']['unique_word_ratio'] = len(unique_words) / len(words)
    
    # Update data hash
    log_data['signature']['data_hash'] = generate_data_hash(log_data)
    
    return log_data


def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python3 generate_soul_log.py [sequence_number]")
        print("Creates a new soul-log file with current timestamp.")
        print("Optional sequence_number (default: 001)")
        return
    
    sequence = sys.argv[1] if len(sys.argv) > 1 else "001"
    
    # Validate sequence format
    if not sequence.isdigit() or len(sequence) != 3:
        print("Error: Sequence number must be 3 digits (e.g., 001, 042)")
        return 1
    
    timestamp = datetime.now()
    date_str = timestamp.strftime("%Y%m%d")
    time_str = timestamp.strftime("%H%M")
    
    filename = f"soul-log-{date_str}-{time_str}.json"
    
    # Check if file already exists
    if Path(filename).exists():
        print(f"Error: File {filename} already exists")
        return 1
    
    # Create template
    template = create_soul_log_template(timestamp, sequence)
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"✅ Created: {filename}")
    print(f"📝 Edit the file to add Grok's reflection text and analysis")
    print(f"🔄 Run 'python3 -c \"import json; import generate_soul_log as g; data = json.load(open('{filename}')); g.update_calculated_fields(data); json.dump(data, open('{filename}', 'w'), indent=2)\"' after editing to update calculated fields")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())