
import os
import json
import csv
import logging
import argparse

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_log_file(filepath):
    """
    Reads a single JSON log file, extracts timestamp, level, and message.
    Handles missing fields gracefully.
    """
    extracted_data = []
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    timestamp = entry.get('timestamp')
                    level = entry.get('level')
                    message = entry.get('message')
                    extracted_data.append({
                        'timestamp': timestamp,
                        'level': level,
                        'message': message
                    })
                except json.JSONDecodeError:
                    logging.warning(f"Skipping malformed JSON line {line_num} in {filepath}: {line.strip()}")
                except Exception as e:
                    logging.error(f"Error processing line {line_num} in {filepath}: {e} - Line: {line.strip()}")
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
    except Exception as e:
        logging.error(f"Error reading file {filepath}: {e}")
    return extracted_data

def process_directory(directory_path):
    """
    Iterates over all .json files in a given folder and extracts log data.
    """
    all_extracted_data = []
    if not os.path.isdir(directory_path):
        logging.error(f"Directory not found: {directory_path}")
        return []

    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            filepath = os.path.join(directory_path, filename)
            logging.info(f"Processing file: {filepath}")
            data = parse_log_file(filepath)
            all_extracted_data.extend(data)
    return all_extracted_data

def write_csv_report(data, output_filepath='log_summary.csv'):
    """
    Saves the extracted log data into a single CSV file.
    """
    if not data:
        logging.info("No data to write to CSV.")
        return

    keys = ['timestamp', 'level', 'message'] # Ensure consistent header order
    try:
        with open(output_filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        logging.info(f"Report successfully saved to {output_filepath}")
    except IOError as e:
        logging.error(f"Error writing CSV report to {output_filepath}: {e}")

def main():
    """
    Main function to run the script from the command line.
    """
    parser = argparse.ArgumentParser(description='Parse JSON log files and generate a CSV summary.')
    parser.add_argument('folder_path', type=str, help='Path to the folder containing JSON log files.')
    parser.add_argument('--output', type=str, default='log_summary.csv',
                        help='Optional: Output CSV file name. Defaults to log_summary.csv.')

    args = parser.parse_args()

    logging.info(f"Starting JSON log parsing for folder: {args.folder_path}")
    extracted_data = process_directory(args.folder_path)
    write_csv_report(extracted_data, args.output)
    logging.info("Finished JSON log parsing.")

if __name__ == '__main__':
    main()
