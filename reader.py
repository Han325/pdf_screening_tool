import csv
import requests
import fitz  # PyMuPDF
import re

def extract_emails_from_pdf(pdf_content):
    try:
        pdf = fitz.open(stream=pdf_content, filetype="pdf")
        text = ""

        for page_num in range(len(pdf)):
            page = pdf.load_page(page_num)
            text += page.get_text()

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        emails = re.findall(email_pattern, text)

        return emails[0] if emails else None

    except fitz.fitz.FileDataError as e:
        print(f"Could not process the document: {e}")
        return None

def process_csv(csv_path, output_csv_path, num_rows=None):
    with open(csv_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames + ['email']

        with open(output_csv_path, mode='w', newline='') as write_file:
            writer = csv.DictWriter(write_file, fieldnames=fieldnames)
            writer.writeheader()

            for i, row in enumerate(reader):
                if num_rows and i >= num_rows:
                    break  # Stop after reading num_rows

                pdf_url = row['candidate_cv']
                try:
                    response = requests.get(pdf_url)
                    response.raise_for_status()
                    email = extract_emails_from_pdf(response.content)
                    row['email'] = email
                except requests.exceptions.RequestException as e:
                    print(f"Failed to fetch PDF from {pdf_url}: {e}")
                    row['email'] = None
                except fitz.fitz.FileDataError as e:
                    print(f"Failed to process PDF from {pdf_url}: {e}")
                    row['email'] = None

                writer.writerow(row)

def remove_lines_from_csv(input_csv_path, output_csv_path, line_numbers):
    # Initialize an empty set for cleaned line numbers
    clean_line_numbers = set()

    # Ensure each line number is an integer
    for line_num in line_numbers:
        try:
            # Attempt to convert each line number to an integer and add to the set
            clean_line_numbers.add(int(line_num))
        except ValueError:
            # Handle the case where the conversion fails
            print(f"Warning: Line number {line_num} is not an integer and will be ignored.")

    with open(input_csv_path, 'r', newline='') as input_file, open(output_csv_path, 'w', newline='') as output_file:
        reader = csv.reader(input_file)
        writer = csv.writer(output_file)

        # Write rows that are not in the clean_line_numbers set
        for index, row in enumerate(reader, start=1):
            if index not in clean_line_numbers:
                writer.writerow(row)



# Paths to your CSV files
input_csv_path = './Application-Automate-Output.csv'
output_csv_path = './Application-Automate-Output-Removed.csv'
lines_to_remove = [20, 27, 28, 30, 36, 41, 51, 54, 58, 59, 60, 63, 75, 77, 81, 82, 84, 88, 90, 92, 95, 101, 116, 121, 123, 135, 141, 147, 157, 158, 164, 178, 179, 188, 189, 190, 207, 209, 219, 224, 225, 232]  # Example line numbers to remove

# Call the function to remove specified lines from the CSV
remove_lines_from_csv(input_csv_path, output_csv_path, lines_to_remove)


# Process the CSV to fetch emails and write them back, specify the number of rows for testing
# process_csv(input_csv_path, output_csv_path, num_rows=237)
