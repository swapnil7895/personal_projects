
## This script is desigend to apply jobs on Naukri portal automatically according to inputs given to script for the job category you want.
## Author - Swapnil Dhamal
## Date - 1-18-2025

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import logging
import configparser
from dotenv import load_dotenv





import subprocess



import sys

def get_browser_from_args(default="edge"):
    # Check if a browser argument is passed
    if len(sys.argv) > 1:
        browser = sys.argv[1].strip().lower()
        print(f"Browser specified via command line: {browser}")
    else:
        browser = default
        print(f"No browser specified. Using default: {browser}")
    return browser

# Example usage




from job_apply_lib import *


def run_job_apply_automation( platform ):
    try:
        logger.info(f"Start - run_job_apply_automation( platform )")
        if platform.lower().strip() == "naukri":
           run_job_apply_for_naukri()
        elif platform.lower().strip() == "linkedin":
           run_job_apply_for_linkedin()
    except Exception as e:
        logger.error(f"Failed in - 'run_job_apply_automation( platform )' - {e}")


def run_job_apply_for_naukri():
    try:
        job_apply_count = 0
        job_skip_count = 0
        job_apply_success_count = 0        
        logger.info(f"Start - 'run_job_apply_for_naukri()'")

        pdf_file_name = initialize_pdf( config )

        keywords_to_search = config["naukri_config"]["keywords_job_search"]
        logging.info(f"Keywords to search for job - {keywords_to_search}")        
        xpaths = config["naukri_xpaths"]

        naukri_job_site_url = config["naukri_config"]["job_site_url"]
        driver.get( naukri_job_site_url )
        logging.info("URL Launched")
        # driver.execute_script("window.stop();")\\\

        driver.find_element(By.XPATH, xpaths["jobs_btn"]).click()
        logging.info("Clicked on 'jobs' button")

        driver.find_element(By.XPATH, xpaths["search_jobs_here_btn"]).click()
        logging.info("Clicked on 'Search jobs here' button")
        driver.find_element(By.XPATH, xpaths["jobsearch_textarea"]).send_keys(f"{keywords_to_search}")
        logging.info(f"Entered text '{keywords_to_search}'")
      
        if config["naukri_config"]["search_jobs_by_loc"].lower() == "true":
            joblocation_to_search = config["naukri_config"]["job_search_location"]
            driver.find_element(By.XPATH, xpaths["joblocation_input"]).send_keys(f"{joblocation_to_search}")
            logger.info(f"Searching jobs with location - '{joblocation_to_search}'")
        else:
            logger.info(f"Searching jobs without location")            

        driver.find_element(By.XPATH, xpaths["jobsearch_textarea"] ).send_keys(Keys.ENTER)
        logging.info(f"Pressed ENTER")

        if config["naukri_config"]["sort_jobs_by_date"].lower() == "true":
            logging.info(f"Sorting jobs by date")
            driver.find_element(By.XPATH, xpaths["sort_filter_btn"]).click()
            logging.info(f"Clicked on sort FILTER")
            driver.find_element(By.XPATH, xpaths["sort_filter_date_field"]).click()
            logging.info(f"Clicked on DATE item from DROPDOWN")
        else:
            logger.info(f"Keeping default sort job filter")    
        
        pages_to_check = 5 # default pages to check for jobs
        pages_to_check = config["naukri_config"]["pages_to_check"]
        logger.info(f"Job search pages to check - {pages_to_check}")

        while True:

            all_jobs_on_page_el = driver.find_elements(By.XPATH, xpaths["all_jobs_on_page"])
            logging.info(f"All jobs count from this page - {str(len( all_jobs_on_page_el))}")       
            logging.info(f"Looping over all jobs of this page")

            current_page = driver.find_element(By.XPATH, xpaths["current_page_number"]).text
            logging.info(f"Current page number - '{current_page}'")
            if current_page == pages_to_check:
                break

            for i in range( 1, len( all_jobs_on_page_el) + 1, 1 ):
                try:
                    job_apply_count = job_apply_count + 1 
                    logging.info(f"")       
                    logging.info(f"************")                   
                    logging.info(f"Iteration - {i}")       
                    time.sleep(2)
                    # all_jobs_on_page_el2 = driver.find_elements(By.XPATH, r'//div[ @class = "srp-jobtuple-wrapper"]')
                    # title = all_jobs_on_page_el2[i].find_element(By.XPATH, r"//*[ @class = ' row1']/a").get_attribute("title")

                    # job_title = driver.find_element(By.XPATH, r'(//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row1"]/a)['+str(i)+']').get_attribute("title")                    
                    each_job_dtls_xpath_row1 = xpaths["each_job_dtls_row1"]  + f"{i}]"
                    driver.execute_script("arguments[0].scrollIntoView(true);", driver.find_element(By.XPATH, each_job_dtls_xpath_row1 ) )

                    job_title = driver.find_element(By.XPATH, each_job_dtls_xpath_row1 ).get_attribute("title")

                    each_job_dtls_xpath_row2 = xpaths["each_job_dtls_row2"]  + f"{i}]"
                    # job_company = driver.find_element(By.XPATH, r'(//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row2"]//a)['+str(i)+']').get_attribute("title")              
                    job_company = driver.find_element(By.XPATH, each_job_dtls_xpath_row2 ).get_attribute("title")
                    logging.info(f"Job title - '{job_title}' at company - '{job_company}'")

                    keywords_list_for_job_title = config["naukri_config"]["keywords_list_for_job_title_filter"].split(",")                    
                    validated_job = validate_job_title( job_title, keywords_list_for_job_title )
                    validated_company = validate_company_title( job_company )

                    set_pdf_font("Arial", size=14, style="B")
                    # pdf.set_font("Arial", size=14, style="B")
                    add_line_to_pdf( txt=f"Job title - {job_title}" )
                    # pdf.cell(200, 10, txt=f"Job title - {job_title}", ln=True, align='L')
                    set_pdf_font("Arial", size=12)
                    # pdf.set_font("Arial", size=12)

                    # pdf.cell(200, 10, txt=f"Company - {job_company}", ln=True, align='L')
                    add_line_to_pdf( txt=f"Company - {job_company}" )                    

                    if validated_job:
                    
                        logging.info("title - " + str(job_title))            
                        each_job_dtls_xpath_row6 = xpaths["each_job_dtls_row6"] + f"{i}]"
                        # job_days_old = driver.find_element(By.XPATH, r'(//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row6"]/span[@class = "job-post-day " ])['+str(i)+']').text        
                        job_days_old = driver.find_element(By.XPATH, each_job_dtls_xpath_row6).text        

                        job_days_old = job_days_old.lower()
                        # job_old_str_list = [ "just now", "few hours ago", "days ago", "day ago"]
                        if "30+" in job_days_old:
                            logging.warning(f"Job '{job_title}' is posted 30 days back so ignoring") 
                            job_skip_count =job_skip_count + 1 
                            continue
                        
                        if "just now" in job_days_old or "few hours ago" in job_days_old or "days ago" in job_days_old or "day ago"  in job_days_old:
                            logging.info(f"Job '{job_title}' is posted - {job_days_old}") 
                            # driver.find_element(By.XPATH, r'(//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row1"]/a)['+str(i)+']').click()
                            driver.find_element(By.XPATH, each_job_dtls_xpath_row6).click()
                            logging.info(f"Clicked on job - '{job_title}'")
                            window_handles = driver.window_handles
                            driver.switch_to.window( window_handles[1] )

                            try:
                                apply_button = driver.find_element(By.ID, xpaths["apply_btn_id"])
                                apply_button.click()

                                logging.info(f"Clicked on apply button")
                                try:                                    
                                    apply_message = driver.find_element(By.XPATH, xpaths["apply_msg_textarea"]).text
                                    if "You have successfully applied" in apply_message:
                                        job_apply_success_count = job_apply_success_count + 1
                                        logging.info(f"Successfully applied to job - {job_title}")

                                        # pdf.cell(200, 10, txt=f"Successfully applied to job - {job_title}", ln=True, align='L')
                                        add_line_to_pdf( f"Successfully applied to job - {job_title}" )

                                        driver.close()
                                        driver.switch_to.window( window_handles[0] )
                                        logging.info(f"Switched back to main window -'{driver.current_window_handle}'")
                                        continue

                                except Exception as e:
                                    logging.info(f"Apply success message is not there, checking chatbot popup")

                                # //*[@class = "apply-message"]
                                logging.info(f"Checking if chatbot popup present")
                                try:
                                    chatbot_popup_el = driver.find_element(By.XPATH, xpaths["chatbot_popup_window"])
                                    logging.info(f"Chatbot window present")


                                    # pdf.cell(200, 10, txt=f"Skipping applying this job (chatbot popup present)", ln=True, align='L')
                                    add_line_to_pdf( txt=f"Skipping applying this job (chatbot popup present)" )

                                    ## for now, chatbot pop window feature is not ready so skipping it
                                    current_w_h = driver.current_window_handle
                                    logging.debug(f"Window handle will be closed - {driver.current_window_handle}")
                                    driver.close()
                                    driver.switch_to.window( window_handles[0] )
                                    logging.info(f"Switched back to main window -'{driver.current_window_handle}'")

                                    job_skip_count = job_skip_count + 1
                                    continue

                                    # find chats list
                                    chat_list_elements = driver.find_elements(By.XPATH, "//div[@class = 'chatbot_Drawer chatbot_right']//*/ul/li")
                                    logging.debug(f"List items chat bot - '{chat_list_elements}'")
                                    last_q_text = chat_list_elements[-1].find_element(By.XPATH, "./div[contains( @class, 'botMsg')]//*/span").text
                                    logging.info(f"Chatbot latest question text - '{last_q_text}'")
                                    # //div[@class = 'chatbot_Drawer chatbot_right']//*/ul/li
                                    # //div[@class = "chatbot_InputContainer"]

                                except Exception as e:
                                    job_skip_count = job_skip_count + 1                                    
                                    logging.info(f"Chatbot popup not present")

                                logging.debug(f"After chatbot check------------")
                                driver.close()
                                logging.info(f"Closed window - '{window_handles[1]}'") 
                                driver.switch_to.window(window_handles[0])               
                                logging.info(f"Switched back to main window") 

                            except Exception as e:
                                job_skip_count = job_skip_count + 1
                                logging.warning(f"Apply button not found for this job")
                                # pdf.cell(200, 10, txt=f"Apply button not found - FAILED TO APPLY", ln=True, align='L')
                                add_line_to_pdf( txt=f"Apply button not found - FAILED TO APPLY" )

                                driver.close()
                                logging.info(f"Closed window - '{window_handles[1]}'") 
                                driver.switch_to.window(window_handles[0])               
                                logging.info(f"Switched back to main window")
                    else:
                        job_skip_count = job_skip_count + 1
                        # pdf.set_font(size=12, family="Arial", style="B")
                        set_pdf_font("Arial", size=12, style="B")

                        # pdf.cell(200,10, txt="Job not suitable - SKIPPING", ln=True, align="L")
                        add_line_to_pdf( txt="Job not suitable - SKIPPING" )

                        logging.warning(f"Not applying for this job - '{job_title}'")
                        # pdf.set_font(size=12, family="Arial")
                        set_pdf_font("Arial", size=12 )

                    # pdf.ln(10)
                    add_line_to_pdf(empty_line=True)

                    if len(all_jobs_on_page_el) == i:
                        # driver.refresh()                    
                        logging.info(f"Last job on this page checked, going to next page")
                        driver.execute_script("arguments[0].scrollIntoView();", driver.find_element(By.XPATH, xpaths["next_job_page_btn"]))
                        driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, xpaths["next_job_page_btn"]))                        
                        # driver.find_element(By.XPATH, xpaths["next_job_page_btn"]).click()
                        logging.info(f"Clicked on next button -->")

                except Exception as e:            
                    driver.save_screenshot("error_screenshot.png")
                    logging.error(f"Exception - {e}")

        logging.info(f"Success job apply count - {job_apply_success_count}")
        logging.info(f"Total jobs cheked - {job_apply_count}")
        logging.info(f"Job skip count - {job_skip_count}")
        add_line_to_pdf( txt=f"Success job apply count - {job_apply_success_count}" )                    
        add_line_to_pdf( txt=f"Total jobs cheked - {job_apply_count}" )                    
        add_line_to_pdf( txt=f"Job skip count - {job_skip_count}" )                            

        # pdf.output(pdf_file_name)  
        write_pdf_file(pdf_file_name)  
     
        # send status email
        subject =  f"{str(job_search_platform.capitalize() )}: Job apply status report - {str(datetime.now().strftime('%d-%m-%Y'))}"
        body = f"""
                    <html><br>Job search platform - Naukri
                    <br>Jobs applied with keywords searched - {keywords_to_search}<br>
                    <br>Success job apply count - {job_apply_success_count}
                    <br>Total jobs cheked - {job_apply_count}
                    <br>Job skip count - {job_skip_count}<br></html>
                    
                """
        send_email( sender_email, sender_pwd, receiver_email, smtp_server_name, smtp_server_port, subject, body, pdf_file_name)
                    # //a[contains( @class, "styles_btn-secondary")]//span[contains( text(), "Next")]
                    # '//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row1"]/a'
                    # '//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row1"]/span[@class = "job-post-day " ]'            
                    # //div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row6"]/span[@class = "job-post-day " ]
                    # placeholder="Enter keyword / designation / companies"


    except Exception as e:
        logger.error(f"Failed in - 'run_job_apply_for_naukri()' -{e}")
        body = f"Failed to execute job apply automation with error - {e}"
        subject =  f"{str(job_search_platform.capitalize())} Job apply status report - {datetime.now().strftime('%d-%m-%Y')} - FAILED"
        send_email( sender_email, sender_pwd, receiver_email, smtp_server_name, smtp_server_port, subject, body)        


def run_job_apply_for_linkedin():
    try:
        logger.info(f"Start - run_job_apply_for_linkedin()")
        driver.get(f"https://linkedin.com")
        # time.sleep(100000)
        li_xpaths = config["linkedin_xpaths"]
        
        check_if_already_loggedin()
# //*[@id="ember16"]
        driver.find_element(By.XPATH, li_xpaths["sign_in"] ).click()


    except Exception as e:
        logger.error(f"Failed in - run_job_apply_for_linkedin()")

if __name__ == "__main__":
    # logger =None
    sender_email=None 
    receiver_email=None
    sender_pwd=None
    smtp_server_name=None 
    smtp_server_port=None
    
    logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    config = configparser.ConfigParser()
    config.read('./job_apply.conf')

    browser_choice = get_browser_from_args()

    if browser_choice.lower() == "edge":
        kill_edge()
        edge_driver_path = r'C:\Users\Admin\Documents\Swapnil\PP\personal_projects\Naukri_automation\driver\msedgedriver.exe'

        # Set up Edge options (optional)
        # edge_options = Options()
        # edge_options.use_chromium = True
        service = Service(executable_path=edge_driver_path)
        # driver = webdriver.Edge(service=service, options=edge_options)
        driver = webdriver.Edge(service=service)    



    else:    
        os.system("taskkill /im chrome.exe /f")

        webdriver_path = config["job_apply_config"]["webdriver_path"]
        chrome_options = Options()

        user_data_dir = config["job_apply_config"]["user_data_dir"]
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        chrome_options.add_argument(f"profile-directory=Default")
        chrome_options.add_argument(f"--remote-debugging-port=9222")
        chrome_options.add_argument(f"--no-sandbox")
        chrome_options.add_argument(f"--disable-dev-shm-usage")
        chrome_options.add_argument(f"--disable-extensions")

        # chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
        # profile_dir = "Default"  # or "Profile 1", "Profile 2", etc.
        # service = Service(ChromeDriverManager().install())

        service = Service(webdriver_path)
        logging.info("Service set")
        driver = webdriver.Chrome(service=service, options=chrome_options)


    logging.info("Driver set")
    # driver.get("https://www.linkedin.com")
    driver.maximize_window()
    driver.implicitly_wait(10)

    load_dotenv()

    job_search_platforms = config["job_apply_config"]["job_search_platforms"].split(",")
    logger.info(f"Job search platforms - {job_search_platforms}")

    try:

        sender_email, receiver_email, sender_pwd, smtp_server_name, smtp_server_port = get_mail_config( config ) 

        if job_search_platforms == [] or job_search_platforms == None:
            logger.warning(f"No platform is present to check jobs, check config")

        for job_search_platform in job_search_platforms:
            logger.info(f"Job search started for platform - '{job_search_platform}'")
            if job_search_platform.lower() == "naukri":
                run_job_apply_automation( platform = job_search_platform)
            elif job_search_platform.lower() == "linkedin":
                run_job_apply_automation( platform = job_search_platform)

            else:
                logger.warning(f"Unknown job search platform  - '{job_search_platform}'")

    except Exception as e:
        if logger is not None:
            logger.info(f"Exception - {e}")
        if sender_email and receiver_email and sender_pwd and smtp_server_name and smtp_server_port:
            body = f"Failed to execute job apply automation with error - {e}"
            subject =  f"Job apply status report - {datetime.now().strftime('%d-%m-%Y')} - FAILED"
            send_email( sender_email, sender_pwd, receiver_email, smtp_server_name, smtp_server_port, subject, body)

    finally:
        driver.quit()
