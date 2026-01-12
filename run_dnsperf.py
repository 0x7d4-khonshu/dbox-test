#!/usr/bin/env python3
"""
Run dnsperf with periodic stats capture.
Sends SIGINT (Ctrl+C) every 2 seconds to capture stats, then logs results.
"""

import subprocess
import signal
import sys
import os
import glob
from datetime import datetime
import time

# Configuration
DEFAULT_DNS_SERVER = "8.8.8.8"
LOG_FILE = "run_log.txt"
STATS_INTERVAL = 2  # seconds between Ctrl+C

def log_message(message):
    """Log a message with timestamp to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {message}"
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def find_csv_file(file_num):
    """Find the CSV file matching the file number."""
    pattern = f"dnsperf_files/domains_{file_num}_*.csv"
    matches = glob.glob(pattern)
    if matches:
        return matches[0]
    return None

def list_available_files():
    """List available CSV files."""
    files = glob.glob("dnsperf_files/domains_*.csv")
    if files:
        print("Available files:")
        for f in sorted(files):
            print(f"  {f}")
    else:
        print("No CSV files found in dnsperf_files/")

def run_dnsperf(file_num, dns_server):
    """Run dnsperf and capture stats every 2 seconds."""
    csv_file = find_csv_file(file_num)
    
    if not csv_file:
        print(f"Error: No file found for number {file_num}")
        list_available_files()
        return 1
    
    # dnsperf command
    cmd = [
        "dnsperf",
        "-s", dns_server,
        "-d", csv_file,
        "-c", "100",
        "-Q", "1000000",
        "-q", "1000000",
        "-T", "6",
        "-l", "20",
        "-S", "1",
        "-t", "30"
    ]
    
    print("=" * 50)
    print("Running dnsperf with:")
    print(f"  File: {csv_file}")
    print(f"  DNS Server: {dns_server}")
    print(f"  Stats capture interval: {STATS_INTERVAL} seconds")
    print("=" * 50)
    
    log_message(f"File {file_num} STARTED - {csv_file} - DNS: {dns_server}")
    
    try:
        # Start dnsperf process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        start_time = time.time()
        output_lines = []
        
        # Read output while process runs
        while True:
            # Check if process has finished
            return_code = process.poll()
            if return_code is not None:
                # Process finished, read remaining output
                remaining = process.stdout.read()
                if remaining:
                    output_lines.append(remaining)
                    print(remaining, end='')
                break
            
            # Read available output
            try:
                line = process.stdout.readline()
                if line:
                    output_lines.append(line)
                    print(line, end='')
            except:
                pass
            
            # Check if it's time to send SIGINT for stats
            elapsed = time.time() - start_time
            if elapsed >= STATS_INTERVAL:
                try:
                    # Send SIGINT to get stats
                    process.send_signal(signal.SIGINT)
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Sent Ctrl+C for stats capture")
                    start_time = time.time()
                    time.sleep(0.5)  # Brief pause to let stats print
                except:
                    break
        
        # Save all output to log
        full_output = ''.join(output_lines)
        log_message(f"File {file_num} COMPLETED - Stats:\n{full_output}")
        
    except FileNotFoundError:
        print("Error: dnsperf not installed. Run: sudo apt install dnsperf")
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        process.terminate()
        log_message(f"File {file_num} INTERRUPTED by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        log_message(f"File {file_num} ERROR - {e}")
        return 1
    
    print("=" * 50)
    print(f"dnsperf completed for file {file_num}")
    print(f"Run logged to {LOG_FILE}")
    print("=" * 50)
    
    return 0

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file_number> [dns_server]")
        print(f"Example: {sys.argv[0]} 1 8.8.8.8")
        print()
        list_available_files()
        return 1
    
    file_num = sys.argv[1]
    dns_server = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DNS_SERVER
    
    return run_dnsperf(file_num, dns_server)

if __name__ == "__main__":
    sys.exit(main())
