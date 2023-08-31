import requests
import PyPDF2
import io

'''
TODO: extract and isolate voter statements from manually inputted voter pamphlet pdfs
TODO: Fix the "Rosie McCarter" problem
'''
class Extractor:
    def download_pdf(url):
        response = requests.get(url)
        if response.status_code == 200:
            return io.BytesIO(response.content)
        else:
            print(f"Failed to download PDF: {response.status_code}")
            return None

    def extract_text_from_pdf_stream(pdf_stream):
        reader = PyPDF2.PdfReader(pdf_stream)
        text = ""
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
        return text