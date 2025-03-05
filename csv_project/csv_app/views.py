from django.shortcuts import render

import os  
import csv  
import PyPDF2  
from django.conf import settings  
from django.shortcuts import render, redirect  
from django.http import HttpResponse  

# -------------------- CSV Handling --------------------
CSV_FILE = os.path.join(settings.BASE_DIR, 'data.csv')  

def get_csv_data():  # Function to read CSV data
    data = []  
    try:  
        with open(CSV_FILE, 'r', encoding='utf-8') as file:  
            reader = csv.DictReader(file)  
            for row in reader:  
                data.append({'name': row['name'], 'value': row['value']})  
    except FileNotFoundError:  # If the CSV file doesn't exist
        pass  
    except Exception as e:  # Catch any other exceptions during CSV reading
        print(f"Error reading CSV: {e}")  
        return []  
    return data  

def save_csv_data(name, value):  # Function to save data to the CSV
    try:  
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:  
            writer = csv.writer(file)  
            writer.writerow([name, value])  
    except Exception as e:  # Catch any exceptions during CSV writing
        print(f"Error writing to CSV: {e}")  

# -------------------- PDF Processing --------------------
def extract_page_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)  
        max_text_length = 0
        most_relevant_page_num = 0

        for page_num in range(num_pages):  
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            text_length = len(page_text)

            if text_length > max_text_length:  # Check if current page has more text
                max_text_length = text_length
                most_relevant_page_num = page_num

        relevant_page = pdf_reader.pages[most_relevant_page_num]
        relevant_page_text = relevant_page.extract_text()
        return relevant_page_text

    except (FileNotFoundError, PyPDF2.errors.PdfReadError) as e:
        return f"Error processing PDF: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# -------------------- Views --------------------
def index(request):
    csv_data = get_csv_data()

    if request.method == 'POST':
        if 'upload_csv' in request.POST and 'csv_upload' in request.FILES:  # CSV upload form
            csv_file = request.FILES['csv_upload']

            if not csv_file.name.lower().endswith('.csv'):
                return HttpResponse("Invalid file type. Please upload a CSV file.")

            try:
                decoded_file = csv_file.read().decode('utf-8')
                reader = csv.DictReader(decoded_file.splitlines())
                for row in reader:
                    save_csv_data(row['name'], row['value'])
                return redirect('index')
            except Exception as e:
                return HttpResponse(f"Error processing uploaded CSV: {e}")

        elif 'csv_name' in request.POST:  # Add data form
            name = request.POST.get('csv_name')
            value = request.POST.get('csv_value')
            save_csv_data(name, value)
            return redirect('index')

        elif 'pdf_file' in request.FILES:  # PDF form
            pdf_file = request.FILES['pdf_file']
            if not pdf_file.name.lower().endswith('.pdf'):
                return HttpResponse("Invalid file type. Please upload a PDF.")
            relevant_text = process_pdf(pdf_file)
            return render(request, 'index.html', {'csv_data': csv_data, 'relevant_text': relevant_text})

    return render(request, 'index.html', {'csv_data': csv_data})


@csrf_exempt  # Exempt from CSRF for AJAX requests (handle CSRF in JS)
def edit_csv_row(request, row_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Get data from AJAX request
            name = data.get('name')
            value = data.get('value')

            updated_csv_data = []
            with open(CSV_FILE, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for i, row in enumerate(reader):
                    if i + 1 == int(row_id): # Row IDs start from 1
                        updated_csv_data.append({'name': name, 'value': value})
                    else:
                        updated_csv_data.append(row)

            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['name', 'value']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(updated_csv_data)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def delete_csv_row(request, row_id):
    if request.method == 'POST':
        try:
            updated_csv_data = []
            with open(CSV_FILE, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for i, row in enumerate(reader):
                    if i + 1 != int(row_id): # Row IDs start from 1
                        updated_csv_data.append(row)

            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['name', 'value']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(updated_csv_data)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
