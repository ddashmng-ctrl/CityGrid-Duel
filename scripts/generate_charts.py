#!/usr/bin/env python3
"""
Chart generation script for CityGrid-Duel Dashboard
Reads logs/aggregated_logs.csv and generates visualization charts
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

def main():
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    csv_path = os.path.join(repo_root, 'logs', 'aggregated_logs.csv')
    assets_dir = os.path.join(repo_root, 'docs', 'assets')
    
    # Ensure assets directory exists
    os.makedirs(assets_dir, exist_ok=True)
    
    # Check if CSV file exists
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found!")
        sys.exit(1)
    
    # Read the CSV data
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} rows from {csv_path}")
        print(f"Columns: {list(df.columns)}")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    # Generate Entropy vs Run ID chart
    plt.figure(figsize=(10, 6))
    plt.plot(df['run_id'], df['entropy'], marker='o', linewidth=2, markersize=8)
    plt.title('Entropy vs. Run ID', fontsize=16, fontweight='bold')
    plt.xlabel('Run ID', fontsize=12)
    plt.ylabel('Entropy', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    entropy_chart_path = os.path.join(assets_dir, 'entropy_vs_run_id.png')
    plt.savefig(entropy_chart_path, dpi=300, bbox_inches='tight')
    print(f"Saved entropy chart to {entropy_chart_path}")
    plt.close()
    
    # Generate MI (Mutual Information) vs Run ID chart
    plt.figure(figsize=(10, 6))
    plt.plot(df['run_id'], df['mutual_information'], marker='s', color='red', linewidth=2, markersize=8)
    plt.title('Mutual Information vs. Run ID', fontsize=16, fontweight='bold')
    plt.xlabel('Run ID', fontsize=12)
    plt.ylabel('Mutual Information', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    mi_chart_path = os.path.join(assets_dir, 'mi_vs_run_id.png')
    plt.savefig(mi_chart_path, dpi=300, bbox_inches='tight')
    print(f"Saved MI chart to {mi_chart_path}")
    plt.close()
    
    print("Chart generation completed successfully!")
    print(f"Charts saved in: {assets_dir}")

if __name__ == "__main__":
    main()