import os
import json
import csv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_json_log_file(filepath):
    """
    Parses a single JSON log file and extracts timestamp, level, and message.
    Handles missing fields gracefully.
    """
    extracted_data = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    timestamp = entry.get('timestamp', 'N/A')
                    level = entry.get('level', 'N/A')
                    message = entry.get('message', 'N/A')
                    extracted_data.append({'timestamp': timestamp, 'level': level, 'message': message})
                except json.JSONDecodeError:
                    logging.warning(f"Skipping malformed JSON line in {filepath}: {line.strip()}")
                except AttributeError:
                    logging.warning(f"Skipping non-dictionary entry in {filepath}: {line.strip()}")
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
    except Exception as e:
        logging.error(f"Error reading file {filepath}: {e}")
    return extracted_data

def process_log_directory(directory_path):
    """
    Iterates over all .json files in a given directory, processes them,
    and returns a consolidated list of extracted data.
    """
    all_extracted_data = []
    if not os.path.isdir(directory_path):
        logging.error(f"Directory not found: {directory_path}")
        return all_extracted_data

    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            filepath = os.path.join(directory_path, filename)
            logging.info(f"Processing file: {filepath}")
            data = parse_json_log_file(filepath)
            all_extracted_data.extend(data)
    return all_extracted_data

def save_to_csv(data, output_filepath):
    """
    Saves the extracted log data into a single CSV file.
    """
    if not data:
        logging.warning("No data to save to CSV.")
        return

    keys = data[0].keys()
    try:
        with open(output_filepath, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        logging.info(f"Successfully saved summarized report to {output_filepath}")
    except Exception as e:
        logging.error(f"Error saving to CSV file {output_filepath}: {e}")

def main():
    """
    Main function to run the script from the command line.
    Expects a single argument: the path to the directory containing JSON log files.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Parse JSON log files and generate a summarized CSV report.")
    parser.add_argument('folder_path', type=str,
                        help='Path to the directory containing JSON log files.')
    args = parser.parse_args()

    input_folder = args.folder_path
    output_csv = "log_summary.csv"

    logging.info(f"Starting log processing for directory: {input_folder}")
    extracted_logs = process_log_directory(input_folder)
    save_to_csv(extracted_logs, output_csv)
    logging.info("Log processing complete.")

if __name__ == "__main__":
    main()