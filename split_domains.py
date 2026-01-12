"""
Script to split a large CSV file of domains into smaller CSV files for dnsperf.
Each output file contains 100,000 (1 lakh) domains in the format: domain A
"""

import csv
import os

# Configuration
INPUT_FILE = "tranco_4N6VX.csv"
OUTPUT_DIR = "dnsperf_files"
DOMAINS_PER_FILE = 100000  # 1 lakh
MAX_DOMAINS = 1000000  # 1 million

def main():
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    domain_count = 0
    file_count = 0
    current_file = None
    writer = None

    with open(INPUT_FILE, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        
        for row in reader:
            # Stop if we've processed 1 million domains
            if domain_count >= MAX_DOMAINS:
                print(f"\nReached {MAX_DOMAINS:,} domains. Stopping.")
                break
            
            # Extract domain (second column)
            if len(row) >= 2:
                domain = row[1].strip()
            else:
                continue
            
            # Create new file if needed (every 1 lakh domains)
            if domain_count % DOMAINS_PER_FILE == 0:
                # Close previous file
                if current_file:
                    current_file.close()
                
                file_count += 1
                start = domain_count + 1
                end = min(domain_count + DOMAINS_PER_FILE, MAX_DOMAINS)
                filename = os.path.join(OUTPUT_DIR, f"domains_{file_count}_{start}_to_{end}.csv")
                
                current_file = open(filename, 'w', newline='', encoding='utf-8')
                writer = csv.writer(current_file, delimiter=' ')
                print(f"Creating file {file_count}: {filename}")
            
            # Write domain in dnsperf format: domain A
            writer.writerow([domain, 'A'])
            domain_count += 1
            
            # Progress indicator
            if domain_count % 100000 == 0:
                print(f"  Processed {domain_count:,} domains...")

    # Close the last file
    if current_file:
        current_file.close()

    print(f"\n{'='*50}")
    print(f"Processing complete!")
    print(f"Total domains processed: {domain_count:,}")
    print(f"Total files created: {file_count}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
