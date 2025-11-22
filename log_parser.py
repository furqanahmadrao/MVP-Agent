import os
import json
import csv
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_log_file(file_path):
    """
    Parses a single JSON log file and extracts timestamp, level, and message.
    Handles missing fields gracefully by returning empty strings.
    """
    extracted_data = []
    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line)
                    timestamp = entry.get('timestamp', '')
                    level = entry.get('level', '')
                    message = entry.get('message', '')
                    extracted_data.append({'timestamp': timestamp, 'level': level, 'message': message})
                except json.JSONDecodeError:
                    logging.warning(f"Skipping malformed JSON line in {file_path}:{line_num}: {line.strip()}")
                except Exception as e:
                    logging.error(f"Error processing line {line_num} in {file_path}: {e}")
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
    return extracted_data

def process_log_directory(directory_path):
    """
    Iterates over all .json files in a given directory, parses them,
    and collects extracted log data.
    """
    all_extracted_data = []
    if not os.path.isdir(directory_path):
        logging.error(f"Directory not found: {directory_path}")
        return []

    logging.info(f"Processing directory: {directory_path}")
    for root, _, files in os.walk(directory_path):
        for file_name in files:
            if file_name.endswith('.json'):
                file_path = os.path.join(root, file_name)
                logging.info(f"Parsing file: {file_path}")
                data = parse_log_file(file_path)
                all_extracted_data.extend(data)
    return all_extracted_data

def write_summary_to_csv(data, output_csv_path='log_summary.csv'):
    """
    Saves the extracted log data into a single CSV file.
    """
    if not data:
        logging.info("No data to write to CSV.")
        return

    fieldnames = ['timestamp', 'level', 'message']
    try:
        with open(output_csv_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logging.info(f"Successfully wrote log summary to {output_csv_path}")
    except Exception as e:
        logging.error(f"Error writing to CSV file {output_csv_path}: {e}")

def main():
    """
    Main function to parse command-line arguments and run the log parser.
    """
    parser = argparse.ArgumentParser(description='Parse JSON log files and generate a CSV summary.')
    parser.add_argument('log_directory', type=str,
                        help='Path to the directory containing JSON log files.')
    parser.add_argument('--output', type=str, default='log_summary.csv',
                        help='Name of the output CSV file. Defaults to log_summary.csv')

    args = parser.parse_args()

    logging.info("Starting JSON log parsing process...")
    extracted_logs = process_log_directory(args.log_directory)
    write_summary_to_csv(extracted_logs, args.output)
    logging.info("JSON log parsing process completed.")

if __name__ == '__main__':
    main()
