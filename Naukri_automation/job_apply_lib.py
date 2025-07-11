import logging
import subprocess
from fpdf import FPDF
from datetime import datetime
import os
import smtplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException


logger = logging.getLogger(__name__)

global pdf

def kill_browser(browser_choice):
    if browser_choice == "edge":
        kill_edge()
    elif browser_choice == "chrome":
        kill_chrome()

def validate_job_title( job_title, keywords_list_for_job_title ):
    logger.info(f"In validate job function")

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

def get_mail_config(config):
    logger.info(f"Start - get_mail_config(config)")
    try:
        sender_email = config["email_config"]["sender_email"]
        receiver_email = config["email_config"]["receiver_email"]            
        sender_pwd = os.getenv("EMAIL_PASSWORD")
        smtp_server_name = config["email_config"]["smtp_server_name"]
        smtp_server_port = config["email_config"]["smtp_server_port"]

        logger.info(f"sender email - {sender_email}, receiver email -  {receiver_email}, smtp server name - {smtp_server_name}, smtp port - {smtp_server_port}")

        return sender_email, receiver_email, sender_pwd, smtp_server_name, smtp_server_port
    except Exception as e:
        logger.error(f"Failed to get email details - {e}")

def send_email( sender_email, sender_pwd, receiver_email, smtp_server_name, smtp_server_port, subject, body, full_file_path = None):

    try:
        message = MIMEMultipart("alternative")
        message["To"] = receiver_email
        message["From"] = sender_email
        message["Subject"] = subject
        message.attach( MIMEText(body,"html") )
        
        if full_file_path: 
            try:
                file_name = os.path.basename(full_file_path)
                with open(full_file_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)  # Encode the file in base64
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={file_name}",
                    )
                message.attach(part)
            except FileNotFoundError:
                logger.error(f"Error: File not found at {full_file_path}")
                body = body + "\n\nFailed to attach file to this email"
        else:
            logger.warning(f"Full file path is not given to attach file, skipping file attach")



 
        with smtplib.SMTP(smtp_server_name.strip(), int(smtp_server_port) ) as server:
            server.starttls()
            server.login(sender_email, sender_pwd)
            server.sendmail(sender_email, receiver_email, message.as_string() )
            logger.info(f"Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email - {e}")    

def kill_edge():
    try:
        # This command forcibly kills all Microsoft Edge processes
        subprocess.run("taskkill /F /IM msedge.exe", check=True, shell=True)
        subprocess.run("taskkill /F /IM msedgedriver.exe", check=True, shell=True)
        logger.info("All Edge processes killed.")
    except subprocess.CalledProcessError as e:
        logger.warning("No Edge processes found or already closed.")

def kill_chrome():
    try:
        os.system("taskkill /im chrome.exe /f")
        # This command forcibly kills all Microsoft Edge processes
        # subprocess.run("taskkill /F /IM msedge.exe", check=True, shell=True)
        # subprocess.run("taskkill /F /IM msedgedriver.exe", check=True, shell=True)
        logger.info("All Chromem processes killed.")
    except subprocess.CalledProcessError as e:
        logger.warning("No Chrome processes found or already closed.")


def click( element_name , xpath, driver):
    try:
        logger.info(f"Start click for '{element_name}' ")
        driver.find_element(By.XPATH, xpath).click()
        logger.info(f"Clicked successfully")
    except StaleElementReferenceException as e:
        try:
            logger.warning(f"Exception - '{e}'")
            logger.warning(f"Trying again")
            driver.find_element(By.XPATH, xpath).click()
            logger.info(f"Clicked successfully")

        except Exception as e:
            logger.error(f"Exception again - '{e}'")
            raise e

    except Exception as e:
        logger.error(f"Failed in - click() -  {e}")
        raise Exception(e)


def send_input( element_name , xpath, driver, keys):
    try:
        logger.info(f"Start send input for '{element_name}' ")
        driver.find_element(By.XPATH, xpath).send_keys(keys)
        logger.info(f"Sent keys successfully")

    except StaleElementReferenceException as e:
        try:
            logger.warning(f"Exception - '{e}'")
            logger.warning(f"Trying again")
            driver.find_element(By.XPATH, xpath).send_keys(keys)
            logger.info(f"Sent keys successfully")
        except Exception as e:
            logger.error(f"Exception again - '{e}'")
            raise e

    except Exception as e:
        logger.error(f"Failed in - send_input() -  {e}")
        raise Exception(e)


def js_scroll_to_element( element_name, driver, xpath ):
    try:
        logger.info(f"Start js_scroll_to_element '{element_name}' ")
        driver.execute_script( "arguments[0].scrollIntoView()", driver.find_element( By.XPATH, xpath ) )
        logger.info(f"Scrolled into view successfully")

    except StaleElementReferenceException as e:
        try:
            logger.warning(f"Exception - '{e}'")
            logger.warning(f"Trying again")
            driver.execute_script( "arguments[0].scrollIntoView()", driver.find_element( By.XPATH, xpath ) )
            logger.info(f"Scrolled into view successfully")

        except Exception as e:
            logger.error(f"Exception again - '{e}'")
            raise e

    except Exception as e:
        logger.error(f"Failed in - js_scroll_to_element() -  {e}")
        raise Exception(e)


def get_elements( element_name, driver, xpath ):
    try:
        logger.info(f"Start get_elements for '{element_name}' ")
        elements = driver.find_elements(By.XPATH, xpath)
        logger.info(f"Fetched elements successfully")
        return elements

    except StaleElementReferenceException as e:
        try:
            logger.warning(f"Exception - '{e}'")
            logger.warning(f"Trying again")
            elements = driver.find_elements(By.XPATH, xpath)
            logger.info(f"Fetched elements successfully")
            return elements

        except Exception as e:
            logger.error(f"Exception again - '{e}'")
            raise e

    except Exception as e:
        logger.error(f"Failed in - js_scroll_to_element() -  {e}")
        raise Exception(e)

