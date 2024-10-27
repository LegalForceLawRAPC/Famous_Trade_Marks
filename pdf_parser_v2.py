from concurrent.futures import ThreadPoolExecutor, wait
import fitz, io, os, json, re
from typing import Optional, Tuple, List, Dict
from PIL import Image
import easyocr

# Initialize OCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Function to extract images from a PDF page
def extract_images_from_page(pdf_document, page_num: int, image_dir: str) -> List[str]:
    page = pdf_document.load_page(page_num)
    images_on_page = page.get_images(full=True)
    image_paths = []
    
    for img_index, img in enumerate(images_on_page):
        xref = img[0]
        base_image = pdf_document.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        image_filename = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
        image_path = os.path.join(image_dir, image_filename)
        
        with open(image_path, "wb") as image_file:
            image_file.write(image_bytes)
        
        image_paths.append(image_path)
    return image_paths

# Function to perform OCR on an image and extract text
def extract_text_from_image(image_path: str) -> str:
    logo_text = reader.readtext(image_path, detail=0)
    trademark_name = ' '.join(logo_text).strip()
    return trademark_name

# Function to parse application number and applicant name from page text
def parse_application_info(text: str) -> Tuple[Optional[str], Optional[str]]:
    
    application_number_match = re.search(r'Well-\s*known\s*Applicatio\nn\s*No\.\s*(\d+)', text, re.IGNORECASE)
    applicant_name_match = re.search(r'Applicant\s*and\s*Address\s*\n([^\n]+)', text, re.IGNORECASE)

    application_number = application_number_match.group(1) if application_number_match else None
    applicant_name = applicant_name_match.group(1).strip() if applicant_name_match else None
    return application_number, applicant_name

# Function to parse PDF, extract images, and collect table data
def parse_pdf(pdf_path: str) -> List[Dict[str, str]]:
    pdf_document = fitz.open(pdf_path)
    table_data = []
    image_dir = "extracted_images"
    os.makedirs(image_dir, exist_ok=True)
    found_heading = False

    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text = page.get_text("text")

        # Check if the heading is on the current page
        if "Inclusion of the Trade Marks in the list of Well-known Trade Marks" in text:
            print(f"Found the heading on page {page_num + 1}")
            found_heading = True

        if "CORRIGENDA" in text:
            print(f"Found CORRIGENDA page on page {page_num + 1}, exiting loop.")
            break   

        if found_heading:
        # Extract images from page
            image_paths = extract_images_from_page(pdf_document, page_num, image_dir)
            # Process each image and extract relevant data
            for image_path in image_paths:
                try:
                    trademark_name = extract_text_from_image(image_path)
                    #application_number, applicant_name = parse_application_info(text)
                    
                    table_data.append({
                        "trademark_name": trademark_name,
                    })
                    print(f"Extracted data for trademark: {trademark_name}")
                except Exception as e:
                    print(f"Error processing image {image_path}: {e}")

    return table_data

# Function to save extracted data to a JSON file
def save_to_json(data: List[Dict[str, str]], json_path: str) -> None:
    with open(json_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data saved to {json_path}")

# Main function to run the extraction and saving process
def main(pdf_path: str, json_path: str) -> None:
    data = parse_pdf(pdf_path)
    save_to_json(data, json_path)
    print(data)

if __name__ == '__main__':
    pdf_path = "./pdfs/2177/test.pdf"
    json_path = "./json/trademark_data.json"
    
    main(pdf_path, json_path)
