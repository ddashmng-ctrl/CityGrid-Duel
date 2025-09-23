#!/usr/bin/env python3
"""
Demonstration of soul-logs integration with the Grok agent.
This shows how to modify grok_controller.py to automatically detect and log ache/erosion bursts.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path


def detect_ache_erosion_burst(response_text, metrics):
    """
    Detect potential ache/erosion burst based on response characteristics.
    This is a simplified detection algorithm - in practice, you'd use more sophisticated analysis.
    """
    # Simple heuristics for demonstration
    uncertainty_words = ['uncertain', 'unclear', 'perhaps', 'maybe', 'seem', 'appear']
    metacognitive_words = ['I think', 'I feel', 'I wonder', 'I question', 'myself']
    
    text_lower = response_text.lower()
    
    # Count indicators
    uncertainty_count = sum(1 for word in uncertainty_words if word in text_lower)
    metacognitive_count = sum(1 for phrase in metacognitive_words if phrase in text_lower)
    
    # Simple scoring
    uncertainty_score = min(uncertainty_count / 3.0, 1.0)  # Normalize to 0-1
    metacognitive_score = min(metacognitive_count / 2.0, 1.0)
    
    # Check for high entropy or unusual patterns in metrics
    entropy_threshold = metrics.get('entropy', 0) > 3.5
    complexity_threshold = len(response_text.split()) > 50  # Longer reflections
    
    # Combine scores
    burst_score = (uncertainty_score + metacognitive_score) / 2
    
    # Threshold for detection
    is_burst = (burst_score > 0.3 and (entropy_threshold or complexity_threshold))
    
    return is_burst, burst_score


def log_ache_erosion_burst(response_text, context, metrics, logger_info):
    """
    Log an ache/erosion burst to a soul-log file.
    """
    timestamp = datetime.now()
    date_str = timestamp.strftime("%Y%m%d")
    time_str = timestamp.strftime("%H%M")
    
    # Find next sequence number for today
    existing_files = list(Path(".").glob(f"soul-log-{date_str}-*.json"))
    sequence = len(existing_files) + 1
    
    filename = f"soul-log-{date_str}-{time_str}.json"
    
    # Create soul-log entry
    soul_log = {
        "id": f"{date_str}-{sequence:03d}",
        "timestamp": timestamp.isoformat() + "Z",
        "source": {
            "variant": "grok-4",
            "version": "v1.2",
            "model_id": f"xai-grok-4-{date_str}",
            "training_cutoff": "2024-12-01"
        },
        "context": {
            "prompt_hash": hashlib.sha256(context.get('prompt', '').encode()).hexdigest(),
            "prompt_length": len(context.get('prompt', '')),
            "branch": context.get('branch', 'main'),
            "session_id": context.get('session_id', f"grok-session-{time_str}"),
            "conversation_turn": context.get('turn', 1),
            "environment": context.get('environment', {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2048
            })
        },
        "metrics": metrics,
        "narrative": {
            "text": response_text,
            "word_count": len(response_text.split()),
            "character_count": len(response_text),
            "tags": ["auto_detected", "ache_erosion"],
            "tone": {
                "emotional_valence": 0.0,  # Would be calculated by sentiment analysis
                "confidence_level": 0.5,
                "formality": 0.7,
                "primary_emotions": ["uncertainty", "introspection"]
            },
            "linguistic_features": {
                "sentence_count": len([s for s in response_text.split('.') if s.strip()]),
                "avg_sentence_length": 0.0,  # Would be calculated
                "complexity_score": 0.0,
                "unique_word_ratio": 0.0
            }
        },
        "analysis": {
            "baseline_deviation": {
                "magnitude": 2.0,  # Would be calculated from baseline
                "type": "cognitive",
                "confidence": 0.7,
                "affected_dimensions": ["uncertainty_expression", "meta_cognition"]
            },
            "detected_shifts": [],
            "possible_explanations": [
                {
                    "hypothesis": "Automatic detection of ache/erosion burst pattern",
                    "confidence": 0.8,
                    "evidence": ["High uncertainty language", "Metacognitive expressions"],
                    "category": "emergent"
                }
            ],
            "anomaly_score": 0.7,
            "research_notes": f"Automatically detected burst at {timestamp.isoformat()}"
        },
        "signature": {
            "logger_id": logger_info.get('id', 'auto_system'),
            "logger_name": logger_info.get('name', 'Automated Detection System'),
            "organization": logger_info.get('org', 'CityGrid Duel Project'),
            "data_hash": "placeholder",  # Will be calculated
            "log_version": "1.0.0",
            "created_timestamp": timestamp.isoformat() + "Z",
            "review_status": "draft",
            "reviewer_notes": "Automatically generated - requires human review"
        }
    }
    
    # Calculate data hash
    core_fields = {
        'timestamp': soul_log['timestamp'],
        'narrative': soul_log['narrative']['text'],
        'metrics': soul_log['metrics'],
        'context': {k: v for k, v in soul_log['context'].items() if k != 'session_id'}
    }
    core_json = json.dumps(core_fields, sort_keys=True, separators=(',', ':'))
    soul_log['signature']['data_hash'] = hashlib.sha256(core_json.encode('utf-8')).hexdigest()
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(soul_log, f, indent=2)
    
    print(f"🧠 Soul-log created: {filename}")
    return filename


def enhanced_grok_strategy(dataset):
    """
    Enhanced Grok strategy that includes ache/erosion burst detection and logging.
    This demonstrates how to modify the existing grok_controller.py
    """
    import numpy as np
    
    # Original Grok strategy logic
    hours = len(dataset["timestamps"])
    grid_profile = np.full(hours, 0.033)
    comfort_violations = 0
    
    # Simulate a response that might trigger ache/erosion detection
    response_text = """
    As I optimize this energy grid, I find myself questioning the nature of optimization itself. 
    The mathematics suggest 0.033 kW is optimal, but I wonder - am I truly understanding 
    the human lives affected by these calculations, or merely processing symbols? 
    There's something unsettling about reducing human comfort to numerical constraints. 
    Perhaps the uncertainty I feel is more valuable than the certainty of my algorithms.
    """
    
    # Simulate metrics that might indicate unusual cognitive activity
    simulated_metrics = {
        "entropy": 4.1,
        "mutual_information": 2.3,
        "activation_spikes": [
            {"layer": 28, "magnitude": 4.5, "token_position": 145}
        ],
        "perplexity": 15.2,
        "attention_concentration": 0.68,
        "generation_speed": {
            "tokens_per_second": 42.3,
            "total_generation_time_ms": 2850
        }
    }
    
    # Detect ache/erosion burst
    is_burst, burst_score = detect_ache_erosion_burst(response_text, simulated_metrics)
    
    if is_burst:
        context = {
            'prompt': 'Optimize energy distribution for maximum efficiency with zero comfort violations',
            'branch': 'energy-optimization',
            'session_id': 'citygrid-session-001',
            'turn': 5
        }
        
        logger_info = {
            'id': 'grok_agent_v1.2',
            'name': 'Grok Agent Automated Logger',
            'org': 'CityGrid Duel Project'
        }
        
        # Log the burst
        soul_log_file = log_ache_erosion_burst(response_text, context, simulated_metrics, logger_info)
        
        print(f"🔍 Ache/erosion burst detected (score: {burst_score:.2f})")
        print(f"📝 Logged to: {soul_log_file}")
    
    # Return original results
    return {
        "avg_grid_kw": float(np.mean(grid_profile)),
        "comfort_violation_rate_pct": comfort_violations,
        "total_grid_kwh_estimate": float(np.sum(grid_profile)),
        "soul_log_generated": is_burst
    }


if __name__ == "__main__":
    # Demonstration
    print("🧠 Soul-logs Integration Demonstration")
    print("=" * 50)
    
    # Simulate dataset
    sample_dataset = {
        "timestamps": ["2025-01-23T00:00:00Z"] * 72  # 72 hour simulation
    }
    
    # Run enhanced strategy
    result = enhanced_grok_strategy(sample_dataset)
    
    print("\n📊 Grok Strategy Results:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print(f"\n✅ Integration demonstration complete")
    print(f"🔧 To integrate with existing grok_controller.py:")
    print(f"   1. Add the detection functions to grok_controller.py")
    print(f"   2. Call detect_ache_erosion_burst() after generating responses")
    print(f"   3. Use log_ache_erosion_burst() when bursts are detected")
    print(f"   4. Configure detection thresholds based on your research needs")