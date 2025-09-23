#!/usr/bin/env python3
"""
Generate a static HTML dashboard from README.md and aggregated_logs.csv
"""

import csv
import os
import markdown
from pathlib import Path

def read_readme():
    """Read and convert the README.md content to HTML."""
    readme_path = "docs/soul_debate/README.md"
    if not os.path.exists(readme_path):
        return "<p>README.md not found</p>"
    
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Convert markdown to HTML
    html = markdown.markdown(content)
    return html

def read_csv_data():
    """Read the aggregated logs CSV and return data for visualization."""
    csv_path = "logs/aggregated_logs.csv"
    if not os.path.exists(csv_path):
        return []
    
    data = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    
    return data

def generate_table_html(data):
    """Generate HTML table from CSV data."""
    if not data:
        return "<p>No data available</p>"
    
    html = '<table class="data-table">\n'
    
    # Header
    html += '  <thead>\n    <tr>\n'
    for key in data[0].keys():
        html += f'      <th>{key.replace("_", " ").title()}</th>\n'
    html += '    </tr>\n  </thead>\n'
    
    # Body
    html += '  <tbody>\n'
    for row in data:
        html += '    <tr>\n'
        for value in row.values():
            html += f'      <td>{value}</td>\n'
        html += '    </tr>\n'
    html += '  </tbody>\n'
    
    html += '</table>\n'
    return html

def generate_charts_html(data):
    """Generate simple charts using HTML/CSS."""
    if not data:
        return ""
    
    # Separate soul debate logs from simulation results
    soul_logs = [row for row in data if row['source'] == 'soul_debate_logs']
    sim_results = [row for row in data if row['source'] == 'simulation_results']
    
    charts_html = ""
    
    # Chart 1: Entropy vs Mutual Information (for soul debate logs)
    if soul_logs:
        charts_html += '''
    <div class="chart-container">
        <h3>Soul Debate Logs: Entropy vs Mutual Information</h3>
        <div class="simple-chart">
            <div class="chart-grid">'''
        
        for i, row in enumerate(soul_logs):
            if row['entropy'] and row['mutual_information']:
                entropy = float(row['entropy'])
                mi = float(row['mutual_information'])
                # Normalize values for visualization (0-100 scale)
                entropy_percent = min(100, (entropy / 3.0) * 100)  # Assuming max entropy ~3
                mi_percent = min(100, (mi / 1.0) * 100)  # Assuming max MI ~1
                
                charts_html += f'''
                <div class="chart-point" style="left: {entropy_percent}%; bottom: {mi_percent}%;">
                    <div class="point-tooltip">
                        <strong>{row['filename']}</strong><br>
                        Entropy: {entropy}<br>
                        MI: {mi}
                    </div>
                </div>'''
        
        charts_html += '''
            </div>
            <div class="chart-labels">
                <span class="x-label">Entropy →</span>
                <span class="y-label">Mutual Information ↑</span>
            </div>
        </div>
    </div>'''
    
    # Chart 2: Grid Draw Comparison (for simulation results)
    if sim_results:
        max_value = max([float(row['avg_grid_draw_kw']) for row in sim_results if row['avg_grid_draw_kw']], default=1)
        
        charts_html += '''
    <div class="chart-container">
        <h3>Simulation Results: Average Grid Draw (kW)</h3>
        <div class="bar-chart">'''
        
        colors = ['#ff6384', '#36a2eb', '#ffcd56', '#4bc0c0']
        
        for i, row in enumerate(sim_results):
            if row['avg_grid_draw_kw']:
                value = float(row['avg_grid_draw_kw'])
                height_percent = (value / max_value) * 100
                color = colors[i % len(colors)]
                
                charts_html += f'''
            <div class="bar-item">
                <div class="bar" style="height: {height_percent}%; background-color: {color};">
                    <span class="bar-value">{value}</span>
                </div>
                <span class="bar-label">{row['model']}</span>
            </div>'''
        
        charts_html += '''
        </div>
    </div>'''
    
    return charts_html

def generate_dashboard():
    """Generate the complete HTML dashboard."""
    
    # Read data
    readme_html = read_readme()
    csv_data = read_csv_data()
    table_html = generate_table_html(csv_data)
    charts_html = generate_charts_html(csv_data)
    
    # HTML template
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CityGrid Duel Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #24292f;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5rem;
        }}
        
        .header p {{
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }}
        
        .section {{
            margin: 2rem 0;
            padding: 1.5rem;
            background: #f6f8fa;
            border-radius: 8px;
            border-left: 4px solid #0969da;
        }}
        
        .section h2 {{
            margin-top: 0;
            color: #0969da;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            background: white;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .data-table th,
        .data-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #d1d9e0;
        }}
        
        .data-table th {{
            background-color: #f6f8fa;
            font-weight: 600;
            color: #24292f;
        }}
        
        .data-table tr:hover {{
            background-color: #f6f8fa;
        }}
        
        .chart-container {{
            margin: 2rem 0;
            padding: 1rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .chart-container h3 {{
            margin-top: 0;
            color: #24292f;
        }}
        
        .simple-chart {{
            position: relative;
            width: 100%;
            height: 300px;
            border: 1px solid #d1d9e0;
            border-radius: 4px;
            background: linear-gradient(to top, #f8f9fa 0%, #ffffff 100%);
        }}
        
        .chart-grid {{
            position: absolute;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(to right, #e1e5e9 1px, transparent 1px),
                linear-gradient(to top, #e1e5e9 1px, transparent 1px);
            background-size: 20% 20%;
        }}
        
        .chart-point {{
            position: absolute;
            width: 12px;
            height: 12px;
            background-color: #0969da;
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            cursor: pointer;
            transform: translate(-50%, 50%);
            transition: all 0.2s ease;
        }}
        
        .chart-point:hover {{
            background-color: #0550ae;
            transform: translate(-50%, 50%) scale(1.2);
        }}
        
        .chart-point:hover .point-tooltip {{
            display: block;
        }}
        
        .point-tooltip {{
            display: none;
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #24292f;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            white-space: nowrap;
            z-index: 10;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .point-tooltip::after {{
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 5px solid transparent;
            border-top-color: #24292f;
        }}
        
        .chart-labels {{
            margin-top: 10px;
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            color: #656d76;
        }}
        
        .y-label {{
            transform: rotate(-90deg);
            position: absolute;
            left: -30px;
            top: 50%;
            transform-origin: center;
        }}
        
        .bar-chart {{
            display: flex;
            align-items: end;
            gap: 20px;
            height: 250px;
            padding: 20px;
            background: linear-gradient(to top, #f8f9fa 0%, #ffffff 100%);
            border: 1px solid #d1d9e0;
            border-radius: 4px;
        }}
        
        .bar-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            max-width: 120px;
        }}
        
        .bar {{
            width: 80%;
            max-width: 80px;
            background-color: #0969da;
            border-radius: 4px 4px 0 0;
            position: relative;
            transition: all 0.3s ease;
            min-height: 20px;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding-top: 8px;
        }}
        
        .bar:hover {{
            opacity: 0.8;
            transform: scale(1.05);
        }}
        
        .bar-value {{
            color: white;
            font-weight: 600;
            font-size: 0.85rem;
            text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        }}
        
        .bar-label {{
            margin-top: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            text-align: center;
            color: #24292f;
        }}
        
        .readme-content {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
        }}
        
        .readme-content h3 {{
            color: #0969da;
            border-bottom: 1px solid #d1d9e0;
            padding-bottom: 0.5rem;
        }}
        
        .readme-content ul {{
            padding-left: 1.5rem;
        }}
        
        .readme-content li {{
            margin: 0.5rem 0;
        }}
        
        .timestamp {{
            color: #656d76;
            font-size: 0.9rem;
            text-align: center;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #d1d9e0;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .data-table {{
                font-size: 0.9rem;
            }}
            
            .data-table th,
            .data-table td {{
                padding: 8px;
            }}
            
            .bar-chart {{
                gap: 10px;
                padding: 15px;
                height: 200px;
            }}
            
            .simple-chart {{
                height: 250px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 CityGrid Duel Dashboard</h1>
        <p>Real-time insights from Soul Debate Logs and Simulation Results</p>
    </div>
    
    <div class="section">
        <h2>📋 Soul Debate Documentation</h2>
        <div class="readme-content">
            {readme_html}
        </div>
    </div>
    
    <div class="section">
        <h2>📊 Data Visualization</h2>
        {charts_html}
    </div>
    
    <div class="section">
        <h2>📈 Complete Data Table</h2>
        {table_html}
    </div>
    
    <div class="timestamp">
        <p>Dashboard generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <p>🔄 Updated automatically via GitHub Actions</p>
    </div>
</body>
</html>'''
    
    # Ensure output directory exists
    os.makedirs("dashboard_output", exist_ok=True)
    
    # Write the HTML file
    output_path = "dashboard_output/index.html"
    with open(output_path, 'w') as f:
        f.write(html_template)
    
    print(f"Dashboard generated: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_dashboard()