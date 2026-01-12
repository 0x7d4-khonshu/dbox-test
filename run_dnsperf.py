#!/usr/bin/env python3
"""
Run dnsperf with periodic stats capture.
Sends SIGINT (Ctrl+C) every 2 seconds to capture stats, then logs results.
"""

import glob
import shlex
import subprocess
import time, sys
import signal
from multiprocessing import Process
from typing import Optional

DEFAULT_DNS_SERVER = "8.8.8.8"
DEFAULT_WORKERS = 3
STATS_INTERVAL = 2  # seconds between Ctrl+C


MAX_UNIQUE_CLIENT = 10
MAX_QUERIES = 1000000
MAX_OUTSTANDING_QUERIES = 1000000
MAX_THREADS = 6
MAX_TIME = 20
PRINT_STATS = 1
MAX_TIMEOUT = 30

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



def run_scan(
    dns_server: str,
    scan_file: str,
    total_runtime: int,
    restart_interval: int,
):
    """
    Run dnsperf in a loop, restarting it every restart_interval seconds,
    until total_runtime seconds have elapsed.
    """

    cmd = f"dnsperf -s {dns_server} -d {scan_file} -c {MAX_UNIQUE_CLIENT} -Q {MAX_QUERIES} -q {MAX_OUTSTANDING_QUERIES} -T {MAX_THREADS} -l {MAX_TIME} -S {PRINT_STATS} -t {MAX_TIMEOUT}"

    start_time = time.time()
    proc: Optional[subprocess.Popen] = None
    _proc: Optional[subprocess.Popen] = None
    
    while (not total_runtime) or (time.time() - start_time < total_runtime):
        while proc and proc.poll() is None:
            proc.send_signal(signal.SIGKILL)

        proc: Optional[subprocess.Popen] = _proc
        try:
            # Let it run for restart_interval seconds
            time.sleep(restart_interval)
        except Exception as ex:
            pass

        finally:
            _proc = subprocess.Popen(
                shlex.split(cmd),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN),
            )

            # Kill previous process only if it's still running
            if proc and proc.poll() is None:
                proc.send_signal(signal.SIGKILL)

    # Final cleanup and kill anything still running
    for p in (proc, _proc):
        if p and p.poll() is None:
            p.send_signal(signal.SIGKILL)


def run_parallel_scans(
    workers: int,
    dns_server: str,
    scan_file: str,
    total_runtime: int,
    restart_interval: int,
):
    """
    Launch multiple parallel dnsperf scan workers.
    """

    processes = []

    for _ in range(workers):
        p = Process(
            target=run_scan,
            args=(dns_server, scan_file, total_runtime, restart_interval),
        )
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file_number> [dns_server = 8.8.8.8] <workers = 3>")
        print(f"Example: {sys.argv[0]} 1 8.8.8.8 2")
        print()
        list_available_files()
        return 1
    
    file_num = sys.argv[1]
    dns_server = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DNS_SERVER
    worker_processes = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_WORKERS

    filename = find_csv_file(file_num)
    if not filename:
        print("Wrong file number")
        exit(1)

    run_parallel_scans(
        workers=worker_processes,
        dns_server=dns_server,
        scan_file=filename,
        total_runtime=None,       # run for 5 minutes
        restart_interval=STATS_INTERVAL,     # restart dnsperf every 2 seconds
    )


if __name__ == "__main__":
    main()

