from openai import OpenAI
import os
from dotenv import load_dotenv, find_dotenv
from fpdf import FPDF
import json
import PyPDF2

def text_2_json (ppt_text):
    load_dotenv(find_dotenv()) 
    api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    response_format={ "type": "json_object" },
    messages=[
        {"role": "system", "content": """You are a helpful assistant designed to output JSON for a powerpoint slide. ONLY return the JSON, nothing else
        The schema to be returned is the following: 
        {\'title':'Put the title of the slide here', 'paragraph': ['paragraph 1','paragraph 2',...] } 
        
        example: 
        Title: Vehicles
        Paragraph 1: I like to fly planes
        Paragraph 2: I like to drive cars
        Paragraph 3: I like to drive boats
        
        
        JSON output:  {\'title':'Vehicles', 'paragraph': ['I like to fly planes','I like to drive cars','I like to drive boats'] } """},
        
        {"role": "user", "content": ppt_text}
        ]
    )
    json_str = response.choices[0].message.content
    print(json_str) #debugging
    json_data = json.loads(json_str)
    return json_data

# Your text_2_json function remains the same

class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define the path for regular and bold font files
        font_path_regular = 'dejavu-sans/DejaVuSansCondensed.ttf'
        font_path_bold = 'dejavu-sans/DejaVuSansCondensed-Bold.ttf'
        font_path_italic = 'dejavu-sans/DejaVuSansCondensed-Oblique.ttf'  # Adjust with the actual file name
        
        # Add a Unicode font (DejaVu) in Regular, Bold, and Italic
        self.add_font('DejaVu', '', font_path_regular, uni=True)
        self.add_font('DejaVu', 'B', font_path_bold, uni=True)
        self.add_font('DejaVu', 'I', font_path_italic, uni=True)  # Italic
        # Set the font to DejaVu with size 14 for regular text
        self.set_font('DejaVu', '', 14)
        
    def header(self):
        # Use DejaVu Bold for header
        self.set_font('DejaVu', 'B', 12)
        # Your header content here

    def footer(self):
        self.set_y(-15)
        # Use DejaVu Italic for footer
        self.set_font('DejaVu', 'I', 8)
        # Your footer content here

def pdf_gen(ppt_text, pdf_path='presentation.pdf'):
    # Check if the PDF already exists
    if not os.path.exists(pdf_path):
        # Convert text to JSON
        json_data = text_2_json(ppt_text)

        # Initialize PDF
        pdf = PDF(orientation='L')
        pdf.add_page()
        pdf.set_font("Arial", size=20)  # Changed to Arial for simplicity, replace with DejaVu if you have it

        # Parse JSON for the title of the slide and set as title
        title = json_data.get('title', ' Welcome ')  # Provide a default title if none is found
        pdf.cell(200, 10, txt=title, ln=True, align="C")

        # Parse paragraphs and add them to the PDF
        pdf.set_font("Arial", size=14)  # Same font change as above
        paragraphs = json_data.get('paragraph', [])  # Returns an empty list if 'paragraph' is not found
        for paragraph in paragraphs:
            pdf.cell(0, 10, txt=paragraph, ln=True)
            pdf.ln(2)  # Add a small line break after each paragraph

        # Save the PDF
        pdf.output(pdf_path)


def append_pdf(single_pdf_path, output_pdf_path):
    # Check if output_pdf_path exists, and create an empty PDF if it doesn't
    if not os.path.exists(output_pdf_path):
        # Create a new PDF Writer
        pdf_writer = PyPDF2.PdfWriter()
        with open(output_pdf_path, "wb") as out:
            pdf_writer.write(out)
    # Open the existing PDF
    existing_pdf = PyPDF2.PdfReader(open(output_pdf_path, "rb"))
    
    # Open the single page PDF
    new_pdf = PyPDF2.PdfReader(open(single_pdf_path, "rb"))

    # Create a PDF writer to save the output
    pdf_writer = PyPDF2.PdfWriter()

    # Append all pages from the existing PDF to the writer
    for page_num in range(len(existing_pdf.pages)):
        page = existing_pdf.pages[page_num]
        pdf_writer.add_page(page)

    # Append the new page to the writer
    pdf_writer.add_page(new_pdf.pages[0])

    # Write out the combined PDF
    with open(output_pdf_path, "wb") as out:
        pdf_writer.write(out)