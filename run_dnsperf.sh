#!/bin/bash

# Run dnsperf with a specific CSV file
# Usage: ./run_dnsperf.sh <file_number> <dns_server>
# Example: ./run_dnsperf.sh 1 8.8.8.8

FILE_NUM=$1
DNS_SERVER=${2:-"8.8.8.8"}  # Default to Google DNS if not specified
LOG_FILE="run_log.txt"

if [ -z "$FILE_NUM" ]; then
    echo "Usage: $0 <file_number> [dns_server]"
    echo "Example: $0 1 8.8.8.8"
    echo ""
    echo "Available files:"
    ls -1 dnsperf_files/
    exit 1
fi

# Find the CSV file matching the file number
CSV_FILE=$(ls dnsperf_files/domains_${FILE_NUM}_*.csv 2>/dev/null)

if [ -z "$CSV_FILE" ]; then
    echo "Error: No file found for number $FILE_NUM"
    echo "Available files:"
    ls -1 dnsperf_files/
    exit 1
fi

echo "============================================"
echo "Running dnsperf with:"
echo "  File: $CSV_FILE"
echo "  DNS Server: $DNS_SERVER"
echo "============================================"

# Log the start of run
echo "$(date '+%Y-%m-%d %H:%M:%S') - File $FILE_NUM STARTED - $CSV_FILE - DNS: $DNS_SERVER" >> $LOG_FILE

# Run dnsperf with max QPS settings
# -c: number of clients (100)
# -Q: max queries per second (1000000)
# -q: number of queries to send (1000000)
# -T: number of threads (6)
# -l: run limit in seconds (20)
# -S: stats interval (1)
# -t: timeout in seconds (30)
dnsperf -s $DNS_SERVER -d $CSV_FILE -c 100 -Q 1000000 -q 1000000 -T 6 -l 20 -S 1 -t 30

# Log the completed run
echo "$(date '+%Y-%m-%d %H:%M:%S') - File $FILE_NUM COMPLETED - $CSV_FILE - DNS: $DNS_SERVER" >> $LOG_FILE

echo "============================================"
echo "dnsperf completed for file $FILE_NUM"
echo "Run logged to $LOG_FILE"
echo "============================================"
