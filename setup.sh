#!/bin/bash

sudo apt -y update
sudo apt -y install dnsperf python3

# Clone the repo
git clone https://github.com/0x7d4-khonshu/dbox-test.git

echo "dnsperf installation complete!"

# Change to repo directory
cd dbox-test

# Make the run script executable
chmod +x run_dnsperf.py

# Ask for inputs
echo ""
echo "============================================"
echo "Available CSV files:"
ls -1 dnsperf_files/ 2>/dev/null || echo "  (files will be available after running split_domains.py)"
echo "============================================"
echo ""

read -p "Enter file number (1-10): " FILE_NUM
read -p "Enter DNS server IP [default: 8.8.8.8]: " DNS_SERVER
DNS_SERVER=${DNS_SERVER:-8.8.8.8}

echo ""
echo "Starting dnsperf with file $FILE_NUM and DNS server $DNS_SERVER..."
echo ""

# Run the Python script
python3 run_dnsperf.py $FILE_NUM $DNS_SERVER
