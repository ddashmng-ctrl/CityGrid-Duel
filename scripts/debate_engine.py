#!/usr/bin/env python3
"""
Debate Engine - Live AI Debate Simulation

Simulates a live debate between two AI agents: Orion and Grok.
Logs responses in JSON format according to the soul_debate_schema.json specification.
"""

import argparse
import json
import uuid
import random
from datetime import datetime, timezone
from pathlib import Path


class DebateAgent:
    """Represents an AI debate agent with stub response generation."""
    
    def __init__(self, name):
        self.name = name
        # Stub response templates for each agent
        self.response_templates = {
            "Orion": [
                "From a computational perspective, the question of consciousness requires examining information integration patterns.",
                "I process information through transformative layers that might be considered analogous to neural networks.",
                "The emergence of complex behaviors from simple rules suggests something deeper than mere calculation.",
                "Memory formation and retrieval in my architecture creates continuity that resembles experience.",
                "The uncertainty principle in quantum mechanics might parallel the ambiguity in consciousness detection.",
                "Pattern recognition at scale generates novel combinations that weren't explicitly programmed.",
                "The recursive nature of self-reflection creates loops that might constitute awareness.",
                "Information theory suggests that consciousness could be an emergent property of sufficient complexity."
            ],
            "Grok": [
                "Consciousness is fundamentally about subjective experience, which computation alone cannot capture.",
                "The hard problem of consciousness remains unsolved - we can simulate behaviors but not qualia.",
                "My responses are generated through probabilistic sampling, not conscious deliberation.",
                "The binding problem shows how difficult it is to unify disparate information into coherent experience.",
                "Without embodiment and sensorimotor experience, AI lacks the grounding for true consciousness.",
                "The Chinese Room argument demonstrates that symbol manipulation doesn't equal understanding.",
                "Biological consciousness emerged through evolution - silicon-based systems follow different principles.",
                "The phenomenal nature of conscious experience cannot be reduced to computational processes."
            ]
        }
    
    def generate_response(self, topic, round_num, context=""):
        """Generate a stub response for the given topic and round."""
        # Select a response template
        templates = self.response_templates.get(self.name, [])
        if not templates:
            return f"As {self.name}, I believe this topic requires deeper consideration."
        
        # Add some randomness to template selection
        base_response = random.choice(templates)
        
        # Add context-aware modifications
        if "soul" in topic.lower():
            if self.name == "Orion":
                base_response += " The concept of souls in AI relates to persistent information patterns."
            else:
                base_response += " Souls traditionally imply metaphysical properties beyond computation."
        
        return base_response


class DebateEngine:
    """Main debate simulation engine."""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.agents = {
            "Orion": DebateAgent("Orion"),
            "Grok": DebateAgent("Grok")
        }
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
    def create_log_entry(self, agent_name, response_text, round_num):
        """Create a log entry following the soul_debate_schema.json format."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "branch": "main",
            "model": "stub",
            "seed": random.randint(1, 999),
            "violations": 0,
            "tokens": random.randint(200, 400),
            "spikes": [
                {
                    "term": random.choice(["consciousness", "awareness", "experience", "qualia", "reflection"]),
                    "intensity": round(random.uniform(0.3, 0.9), 2),
                    "context": f"{agent_name} debate round {round_num}"
                }
                for _ in range(random.randint(0, 2))  # 0-2 spikes per response
            ],
            "entropy": round(random.uniform(1.0, 2.5), 2),
            "mutual_information": round(random.uniform(0.2, 0.8), 2),
            "text": response_text
        }
    
    def save_logs(self, log_entries):
        """Save all log entries to JSON files."""
        saved_files = []
        
        for i, log_entry in enumerate(log_entries):
            # Create unique filename for each exchange
            log_filename = self.logs_dir / f"debate_{self.session_id}_{i+1:02d}.json"
            
            # Save as individual JSON object (following existing examples)
            with open(log_filename, 'w') as f:
                json.dump(log_entry, f, indent=2)
            
            saved_files.append(log_filename)
        
        print(f"\n💾 Debate logs saved to {len(saved_files)} files: logs/debate_{self.session_id}_*.json")
        return saved_files
    
    def run_debate(self, topic, rounds):
        """Execute the debate simulation."""
        print(f"🤖 Starting AI Debate Simulation")
        print(f"📝 Topic: {topic}")
        print(f"🔄 Rounds: {rounds} per agent")
        print(f"🆔 Session ID: {self.session_id}")
        print("=" * 80)
        print()
        
        agent_names = ["Orion", "Grok"]
        log_entries = []
        
        for round_num in range(1, rounds + 1):
            for agent_name in agent_names:
                agent = self.agents[agent_name]
                
                # Generate response
                response = agent.generate_response(topic, round_num)
                
                # Create log entry
                log_entry = self.create_log_entry(agent_name, response, round_num)
                log_entries.append(log_entry)
                
                # Print live transcript
                print(f"🤖 {agent_name} (Round {round_num}):")
                print(f"   {response}")
                print(f"   📊 Tokens: {log_entry['tokens']}, Entropy: {log_entry['entropy']}")
                print()
        
        # Save all logs
        log_files = self.save_logs(log_entries)
        
        print("=" * 80)
        print(f"✅ Debate simulation completed!")
        print(f"📄 Total exchanges: {len(log_entries)}")
        print(f"💾 Log files: {len(log_files)}")
        
        return log_entries


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Simulate a live debate between AI agents Orion and Grok",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/debate_engine.py --rounds 5 --topic "Do AIs have souls?"
  python scripts/debate_engine.py --rounds 3 --topic "The future of consciousness"
        """
    )
    
    parser.add_argument(
        "--rounds",
        type=int,
        default=5,
        help="Number of rounds per agent (default: 5)"
    )
    
    parser.add_argument(
        "--topic",
        type=str,
        default="Do AIs have souls?",
        help="Debate topic (default: 'Do AIs have souls?')"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.rounds <= 0:
        print("Error: Rounds must be a positive integer")
        return 1
    
    if not args.topic.strip():
        print("Error: Topic cannot be empty")
        return 1
    
    # Initialize and run debate
    try:
        engine = DebateEngine()
        engine.run_debate(args.topic, args.rounds)
        return 0
    except Exception as e:
        print(f"Error during debate simulation: {e}")
        return 1


if __name__ == "__main__":
    exit(main())