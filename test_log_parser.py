import os
import csv
import shutil
from log_parser import process_log_directory, save_to_csv

# Setup test environment
TEST_LOG_DIR = "test_log_files"
OUTPUT_CSV = "log_summary.csv"

def setup_test_environment():
    if os.path.exists(TEST_LOG_DIR):
        shutil.rmtree(TEST_LOG_DIR)
    os.makedirs(TEST_LOG_DIR)

    # Create dummy log files
    with open(os.path.join(TEST_LOG_DIR, "test_log1.json"), 'w') as f:
        f.write('{"timestamp": "2025-01-01T00:00:00Z", "level": "INFO", "message": "Test message 1"}\n')
        f.write('{"timestamp": "2025-01-01T00:00:01Z", "level": "DEBUG", "message": "Test message 2"}\n')

    with open(os.path.join(TEST_LOG_DIR, "test_log2.json"), 'w') as f:
        f.write('{"level": "ERROR", "message": "Test message 3 (missing timestamp)"}\n')
        f.write('{"timestamp": "2025-01-01T00:00:03Z", "message": "Test message 4 (missing level)"}\n')
        f.write('{"timestamp": "2025-01-01T00:00:04Z", "level": "CRITICAL"}\n') # missing message
        f.write('{invalid json line\n') # malformed json

def cleanup_test_environment():
    if os.path.exists(TEST_LOG_DIR):
        shutil.rmtree(TEST_LOG_DIR)
    if os.path.exists(OUTPUT_CSV):
        os.remove(OUTPUT_CSV)

def run_tests():
    print("Setting up test environment...")
    setup_test_environment()

    print(f"Processing log directory: {TEST_LOG_DIR}...")
    extracted_data = process_log_directory(TEST_LOG_DIR)

    print(f"Saving extracted data to {OUTPUT_CSV}...")
    save_to_csv(extracted_data, OUTPUT_CSV)

    print("Verifying output CSV...")
    try:
        with open(OUTPUT_CSV, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            expected_rows = [
                {'timestamp': '2025-01-01T00:00:00Z', 'level': 'INFO', 'message': 'Test message 1'},
                {'timestamp': '2025-01-01T00:00:01Z', 'level': 'DEBUG', 'message': 'Test message 2'},
                {'timestamp': 'N/A', 'level': 'ERROR', 'message': 'Test message 3 (missing timestamp)'},
                {'timestamp': '2025-01-01T00:00:03Z', 'level': 'N/A', 'message': 'Test message 4 (missing level)'},
                {'timestamp': '2025-01-01T00:00:04Z', 'level': 'CRITICAL', 'message': 'N/A'},
            ]

            assert len(rows) == len(expected_rows), f"Expected {len(expected_rows)} rows, got {len(rows)}"
            for i, row in enumerate(rows):
                assert row == expected_rows[i], f"Row {i} mismatch: Expected {expected_rows[i]}, got {row}"
        print("Test successful: Output CSV matches expected data.")
    except AssertionError as e:
        print(f"Test failed: {e}")
    except FileNotFoundError:
        print(f"Test failed: Output CSV file {OUTPUT_CSV} not found.")
    except Exception as e:
        print(f"An unexpected error occurred during verification: {e}")
    finally:
        print("Cleaning up test environment...")
        cleanup_test_environment()

if __name__ == "__main__":
    run_tests()
