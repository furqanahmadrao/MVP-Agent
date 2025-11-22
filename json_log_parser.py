import os
import json
import csv
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_log_files(directory_path):
    """
    Iterates over all .json files in a given directory, extracts specific fields,
    and returns a list of dictionaries.
    """
    log_entries = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            filepath = os.path.join(directory_path, filename)
            logging.info(f"Processing file: {filepath}")
            with open(filepath, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        timestamp = entry.get('timestamp', 'N/A')
                        level = entry.get('level', 'N/A')
                        message = entry.get('message', 'N/A')
                        log_entries.append({
                            'timestamp': timestamp,
                            'level': level,
                            'message': message
                        })
                    except json.JSONDecodeError as e:
                        logging.warning(f"Skipping malformed JSON line in {filename}: {line.strip()} - Error: {e}")
                    except Exception as e:
                        logging.error(f"Error processing line in {filename}: {line.strip()} - Error: {e}")
    return log_entries

def generate_csv_report(log_entries, output_csv_path):
    """
    Saves the extracted log data into a single CSV file.
    """
    if not log_entries:
        logging.info("No log entries to write to CSV.")
        return

    keys = log_entries[0].keys()
    with open(output_csv_path, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(log_entries)
    logging.info(f"CSV report generated successfully: {output_csv_path}")

def main():
    """
    Main function to parse command line arguments and execute the log parsing.
    """
    parser = argparse.ArgumentParser(description="Parse JSON log files and generate a CSV summary.")
    parser.add_argument("directory_path", help="Path to the directory containing JSON log files.")
    parser.add_argument("--output_file", default="log_summary.csv",
                        help="Name of the output CSV file (default: log_summary.csv).")
    args = parser.parse_args()

    if not os.path.isdir(args.directory_path):
        logging.error(f"Error: Directory not found at {args.directory_path}")
        return

    logging.info(f"Starting JSON log parsing in directory: {args.directory_path}")
    log_entries = parse_log_files(args.directory_path)
    generate_csv_report(log_entries, args.output_file)
    logging.info("JSON log parsing completed.")

if __name__ == "__main__":
    main()
