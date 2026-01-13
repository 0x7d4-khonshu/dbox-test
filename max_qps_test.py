#!/usr/bin/env python3
"""
Run resperf with tranco CSV to find maximum QPS the DNS server can handle.
Resperf gradually increases query rate to find the server's breaking point.
"""

import subprocess
import sys
import os
import csv
import tempfile
from datetime import datetime

# Configuration
DEFAULT_DNS_SERVER = "8.8.8.8"
LOG_FILE = "resperf_log.txt"
TRANCO_FILE = "tranco_4N6VX.csv"

def log_message(message):
    """Log a message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {message}"
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def convert_tranco_to_dnsperf(tranco_file, output_file):
    """Convert tranco CSV (rank,domain) to dnsperf format (domain A)."""
    print(f"Converting {tranco_file} to dnsperf format (full file)...")
    count = 0
    
    with open(tranco_file, 'r', encoding='utf-8') as infile:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            reader = csv.reader(infile)
            for row in reader:
                if len(row) >= 2:
                    domain = row[1].strip()
                    outfile.write(f"{domain} A\n")
                    count += 1
                    if count % 500000 == 0:
                        print(f"  Processed {count:,} domains...")
    
    print(f"Converted {count:,} domains to {output_file}")
    return count

def run_resperf(dns_server, data_file):
    """Run resperf to find maximum QPS."""
    
    # resperf command for max QPS testing
    # -m: max queries per second to attempt
    # -r: ramp up rate (QPS increase per second)
    # -c: constant queries per second after ramp
    # -d: duration after ramp
    cmd = [
        "resperf",
        "-s", dns_server,
        "-d", data_file,
        "-m", "500000",    # Max QPS to attempt
        "-r", "10000",     # Increase 10k QPS per second
        "-c", "60",        # Hold constant for 60 seconds after ramp
        "-C", "100",       # 100 concurrent clients
    ]
    
    print("=" * 60)
    print("Running resperf to find maximum QPS")
    print(f"  DNS Server: {dns_server}")
    print(f"  Data file: {data_file}")
    print(f"  Max QPS target: 500,000")
    print(f"  Ramp rate: 10,000 QPS/second")
    print("=" * 60)
    print("\nThis will gradually increase load until the server breaks.\n")
    
    log_message(f"RESPERF STARTED - DNS: {dns_server}")
    
    try:
        # Run resperf and capture output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        output_lines = []
        max_qps = 0
        
        for line in process.stdout:
            print(line, end='')
            output_lines.append(line)
            
            # Try to parse QPS from output
            if "responses/sec" in line.lower() or "qps" in line.lower():
                try:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.replace('.', '').replace(',', '').isdigit():
                            qps = float(part.replace(',', ''))
                            if qps > max_qps:
                                max_qps = qps
                except:
                    pass
        
        process.wait()
        
        # Log results
        full_output = ''.join(output_lines)
        log_message(f"RESPERF COMPLETED - Max QPS observed: {max_qps:.0f}")
        log_message(f"Full output:\n{full_output}")
        
        print("\n" + "=" * 60)
        print(f"Maximum QPS observed: {max_qps:.0f}")
        print(f"Results logged to {LOG_FILE}")
        print("=" * 60)
        
    except FileNotFoundError:
        print("Error: resperf not installed. Run: sudo apt install dnsperf")
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        process.terminate()
        log_message("RESPERF INTERRUPTED by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        log_message(f"RESPERF ERROR - {e}")
        return 1
    
    return 0

def main():
    dns_server = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DNS_SERVER
    tranco_file = sys.argv[2] if len(sys.argv) > 2 else TRANCO_FILE
    
    print(f"Usage: {sys.argv[0]} [dns_server] [tranco_csv_file]")
    print(f"Using DNS server: {dns_server}")
    print(f"Using tranco file: {tranco_file}")
    print()
    
    # Check if tranco file exists
    if not os.path.exists(tranco_file):
        print(f"Error: {tranco_file} not found")
        return 1
    
    # Create temporary dnsperf format file
    temp_file = "resperf_domains.txt"
    convert_tranco_to_dnsperf(tranco_file, temp_file)
    
    # Run resperf
    result = run_resperf(dns_server, temp_file)
    
    return result

if __name__ == "__main__":
    sys.exit(main())
