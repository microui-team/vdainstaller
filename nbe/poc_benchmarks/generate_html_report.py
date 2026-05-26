import os
import json
from datetime import datetime

def generate_report():
    report_dir = "poc_reports"
    output_file = "poc_metrics_dashboard.html"
    
    if not os.path.exists(report_dir):
        print(f"Directory {report_dir} not found.")
        return
        
    json_files = [f for f in os.listdir(report_dir) if f.endswith(".json") and not f.startswith("._")]
    
    metrics_data = []
    for f in json_files:
        with open(os.path.join(report_dir, f), 'r') as file:
            try:
                data = json.load(file)
                metrics_data.append(data)
            except Exception as e:
                print(f"Error reading {f}: {e}")
                
    # Sort by timestamp
    metrics_data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Let's generate a stunning HTML dashboard
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NBE Big Data POC - Performance Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-main: #0f172a;
                --bg-card: #1e293b;
                --text-main: #f8fafc;
                --text-muted: #94a3b8;
                --accent-primary: #3b82f6;
                --accent-success: #10b981;
                --accent-warning: #f59e0b;
                --border-color: #334155;
            }}
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Outfit', sans-serif;
                background-color: var(--bg-main);
                color: var(--text-main);
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 40px 20px;
            }}
            header {{
                text-align: center;
                margin-bottom: 50px;
                position: relative;
            }}
            h1 {{
                font-size: 3rem;
                font-weight: 800;
                margin: 0;
                background: linear-gradient(to right, #60a5fa, #c084fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            p.subtitle {{
                font-size: 1.2rem;
                color: var(--text-muted);
                margin-top: 10px;
            }}
            .dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 25px;
            }}
            .card {{
                background: var(--bg-card);
                border-radius: 16px;
                padding: 25px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                border: 1px solid var(--border-color);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            .card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1);
                border-color: var(--accent-primary);
            }}
            .card-header {{
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .card-title {{
                font-size: 1.4rem;
                font-weight: 600;
                margin: 0;
                color: var(--text-main);
                word-wrap: break-word;
            }}
            .metric-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }}
            .metric {{
                background: rgba(15, 23, 42, 0.5);
                border-radius: 8px;
                padding: 15px;
            }}
            .metric-label {{
                font-size: 0.85rem;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 5px;
            }}
            .metric-value {{
                font-size: 1.5rem;
                font-weight: 800;
                color: var(--accent-success);
            }}
            .metric-value.cpu {{ color: var(--accent-warning); }}
            .metric-value.ram {{ color: #a78bfa; }}
            .metric-value.io {{ color: #38bdf8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>NBE Big Data POC Dashboard</h1>
                <p class="subtitle">Performance Metrics & Resource Utilization Report</p>
                <p class="subtitle" style="font-size: 0.9rem;">Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </header>
            
            <div class="dashboard-grid">
    """
    
    for data in metrics_data:
        workload_name = data.get("workload_name", "Unknown Workload")
        duration = data.get("duration_seconds", 0)
        throughput = data.get("throughput_rows_per_sec", 0)
        rows = data.get("rows_processed", 0)
        max_cpu = data.get("max_system_cpu_percent", 0)
        max_ram = data.get("max_process_memory_rss_mb", 0)
        read_mb = data.get("total_disk_read_mb", 0)
        write_mb = data.get("total_disk_write_mb", 0)
        
        # Display formats
        throughput_str = f"{throughput:,.0f}" if throughput else "N/A"
        rows_str = f"{rows:,.0f}" if rows else "N/A"
        
        html_content += f"""
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">{workload_name}</h2>
                    </div>
                    <div class="metric-grid">
                        <div class="metric">
                            <div class="metric-label">Execution Time</div>
                            <div class="metric-value">{duration} s</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Max CPU</div>
                            <div class="metric-value cpu">{max_cpu}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Rows Processed</div>
                            <div class="metric-value">{rows_str}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Throughput (Rows/s)</div>
                            <div class="metric-value">{throughput_str}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Peak Memory (RSS)</div>
                            <div class="metric-value ram">{max_ram} MB</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Disk Read / Write</div>
                            <div class="metric-value io">{read_mb} / {write_mb} MB</div>
                        </div>
                    </div>
                </div>
        """
        
    html_content += """
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(output_file, 'w') as f:
        f.write(html_content)
        
    print(f"Successfully generated HTML dashboard: {output_file}")

if __name__ == "__main__":
    generate_report()
