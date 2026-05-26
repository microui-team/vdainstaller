import os
import time
from poc_benchmarks.base_workload import BaseWorkload

class HTMLScrapingWorkload(BaseWorkload):
    def __init__(self):
        super().__init__("06_HTML_Web_Scraping")

    def setup(self):
        print("Initializing HTML Processing libraries...")
        os.makedirs("/tmp/poc_data", exist_ok=True)
        
        # Create a dummy HTML file to parse
        self.html_path = "/tmp/poc_data/sample_report.html"
        with open(self.html_path, "w", encoding="utf-8") as f:
            f.write("""
            <html>
                <head><title>Daily Transaction Report</title></head>
                <body>
                    <div id="content">
                        <h1>Summary</h1>
                        <table class="data-table">
                            <tr><th>ID</th><th>Amount</th><th>Status</th></tr>
                            <tr><td>1001</td><td>$250.00</td><td>Success</td></tr>
                            <tr><td>1002</td><td>$12.50</td><td>Failed</td></tr>
                            <tr><td>1003</td><td>$999.99</td><td>Success</td></tr>
                        </table>
                    </div>
                </body>
            </html>
            """)

    def run_workload(self):
        print(f"Phase 1: Parsing Local HTML Report ({self.html_path})")
        start_time = time.time()
        try:
            from bs4 import BeautifulSoup
            
            with open(self.html_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
                
            table = soup.find("table", {"class": "data-table"})
            rows = table.find_all("tr")
            
            extracted_data = []
            for row in rows[1:]: # Skip header
                cols = row.find_all("td")
                extracted_data.append({
                    "id": cols[0].text,
                    "amount": cols[1].text,
                    "status": cols[2].text
                })
                
            self.rows_processed += len(extracted_data)
            
            print(f"Extracted {len(extracted_data)} rows from HTML table.")
            for data in extracted_data:
                print(f"  -> {data}")
                
            print(f"HTML Parsing completed in {time.time() - start_time:.2f}s")
        except ImportError:
            print("BeautifulSoup4 not installed. Skipping HTML phase.")

    def cleanup(self):
        pass

if __name__ == "__main__":
    workload = HTMLScrapingWorkload()
    workload.execute()
