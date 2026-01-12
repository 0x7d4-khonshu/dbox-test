#!/bin/bash

# Run resperf with a specific CSV file
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
echo "Running resperf with:"
echo "  File: $CSV_FILE"
echo "  DNS Server: $DNS_SERVER"
echo "============================================"

# Log the start of run
echo "$(date '+%Y-%m-%d %H:%M:%S') - File $FILE_NUM STARTED - $CSV_FILE - DNS: $DNS_SERVER" >> $LOG_FILE

# Run resperf with max QPS settings
# -m: max queries per second (100000)
# -c: number of clients (100)
# -r: ramp up rate - queries per second increase per second (10000)
resperf -s $DNS_SERVER -d $CSV_FILE -m 100000 -c 100 -r 10000

# Log the completed run
echo "$(date '+%Y-%m-%d %H:%M:%S') - File $FILE_NUM COMPLETED - $CSV_FILE - DNS: $DNS_SERVER" >> $LOG_FILE

echo "============================================"
echo "resperf completed for file $FILE_NUM"
echo "Run logged to $LOG_FILE"
echo "============================================"
