#!/bin/bash

# Update package lists and install dnsperf
git clone https://github.com/0x7d4-khonshu/dbox-test.git
cd dbox-test
sudo apt -y update
sudo apt -y install dnsperf

echo "dnsperf installation complete!"

# Make the run script executable
chmod +x run_dnsperf.sh

echo ""
echo "To run dnsperf, use:"
echo "  ./run_dnsperf.sh <file_number> [dns_server]"
echo ""
echo "Example for anchor 1: ./run_dnsperf.sh 1 8.8.8.8"
echo "Example for anchor 5: ./run_dnsperf.sh 5 1.1.1.1"
