import logging
from fpdf import FPDF
from datetime import datetime


logger = logging.getLogger(__name__)

global pdf

def validate_job_title( job_title, config ):
    logger.info(f"In validate job function")
    keywords_list_for_job_title = config["job_apply_config"]["keywords_list_for_job_title_filter"].split(",")
    for job_title_keyword in keywords_list_for_job_title:
        if job_title_keyword.lower() in job_title.lower():
            logger.info(f"Job validated")
            return True        
    return False

def validate_company_title( job_company ):
    if "rgb" in job_company.lower():
        return False
    else:
        return True


def initialize_pdf( config ):
    global pdf
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    date_str = datetime.now().strftime("%d-%m-%Y")
    pdf_file_name = f"job_apply_{date_str}.pdf"
    return pdf_file_name

def set_pdf_font( font_family, size, style = None):
    global pdf
    if style is None:
        pdf.set_font(font_family , size=size )
    else:
        pdf.set_font(font_family , size=size, style=style)

def add_line_to_pdf(txt = None , empty_line = False):
    global pdf
    if empty_line ==  True:
        pdf.ln(10)
    else:
        pdf.cell(200, 10, txt=f"{txt}", ln=True, align='L')


def write_pdf_file( pdf_file_name ):
    global pdf
    pdf.output(pdf_file_name)  
