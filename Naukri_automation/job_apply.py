
## This script is desigend to apply jobs on Naukri portal automatically according to inputs given to script for the job category you want.
## Author - Swapnil Dhamal
## Date - 1-18-2025

import time
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import logging
import configparser
from dotenv import load_dotenv
from job_apply_lib import *
import subprocess
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

def take_full_screenshot(driver, filename="screenshot.png"):
    """
    Takes a full-page screenshot of the current browser window.

    Args:
        driver: Selenium WebDriver instance.
        filename: Name of the screenshot file to save.
    """
    success = driver.save_screenshot(filename)
    if success:
        logger.info(f"Screenshot saved as {filename}")
    else:
        logger.error("Failed to take screenshot.")


def kill_browser(browser_choice):
    if browser_choice == "edge":
        kill_edge()
    elif browser_choice == "chrome":
        kill_chrome()

def get_browser_from_args(default="edge"):
    # Check if a browser argument is passed
    if len(sys.argv) > 1:
        browser = sys.argv[1].strip().lower()
        print(f"Browser specified via command line: {browser}")
    else:
        browser = default
        print(f"No browser specified. Using default: {browser}")
    return browser

def check_if_already_loggedin( li_xpaths ):
    try:
        logger.info(f"Start - check_if_already_loggedin()")
        profile_xpath = li_xpaths["profile_xpath"]
        profile_elements = driver.find_elements(By.XPATH, profile_xpath)
        if len(profile_elements) > 0:
            logger.info(f"Profile element present so considering user aready logged in")
            return True
        else:
            logger.info(f"Profile element not present so considering user not logged in")
            return False
            
    except Exception as e:
        logger.error(f"Failed in - check_if_already_loggedin() - {e}")

def linkedin_login( li_xpaths ):
    try:
        username = config["linkedin_config"]["login_usename"]
        logger.info(f"Username used for linkedin login is - {username}")
        password = config["linkedin_config"]["login_password"]

        logger.info(f"Start - linkedin_login( li_xpaths )")
        driver.find_element(By.XPATH, li_xpaths["sign_in"] ).click()
        driver.find_element(By.XPATH, li_xpaths["email_or_phone_input"]).send_keys(username)
        driver.find_element(By.XPATH, li_xpaths["pwd_input"]).send_keys(password)
        driver.find_element(By.XPATH, li_xpaths["sign_in_btn"]).click()  

        logged_in = check_if_already_loggedin(li_xpaths)
        if logged_in:
            logger.info(f"Login successful")
            return True
        else:
            logger.error(f"Login failed")
            return False

    except Exception as e:
        logger.error(f"Failed in - linkedin_login() - {e}")

def run_job_apply_automation( platform ):
    try:
        logger.info(f"Start - run_job_apply_automation( platform )")
        if platform.lower().strip() == "naukri":
           run_job_apply_for_naukri()
        elif platform.lower().strip() == "linkedin":
           success_job_list, failed_job_list =  run_job_apply_for_linkedin()
           logger.info(f"success_job_list - '{success_job_list}'")
           logger.info(f"failed_job_list - '{failed_job_list}'")

    except Exception as e:
        logger.error(f"Failed in - 'run_job_apply_automation( platform )' - {e}")
        raise e

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

def click_next_or_review():
    try:
        next_btn_els = driver.find_elements(By.XPATH, f"//button[contains( @aria-label, 'to next' )]")
        if len(next_btn_els) > 0:
            logger.info(f"Next button present on questions page")
            next_btn_els[0].click()
            logger.info(f"Clicked on next button")
            return True  # continue loop
        else:
            raise Exception(f"No next button present")

        # next_btn = driver.find_element(By.XPATH, "//button[span[text()='Next']]")
        # next_btn.click()
    except:
        try:
            ## check if submit application btn is there - if yes click
            submit_appl_btns =  driver.find_elements(By.XPATH, "//button[ contains( @aria-label, 'Submit application' ) ]")
            if len(submit_appl_btns) > 0:
                logger.info(f"Submit application btn present")
                submit_appl_btns[0].click()
                logger.info(f"Clicked on Submit application btn")
            else:
                ###
                driver.find_element(By.XPATH, f"//button[ contains( @aria-label, 'Review your application' ) ]" ).click()                
                logger.info(f"Clicked on review button")
                driver.find_element(By.XPATH, f"//button[contains(@aria-label, 'Submit application' ) ]" ).click()
                logger.info(f"Clicked on submit button")

            done_btns = driver.find_elements(By.XPATH, f"//button//span[ text() = 'Done']" )   
            if len(done_btns) > 0:
                done_btns[0].click()
                logger.info(f"Clicked on done btn") 
            else:
                logger.info(f"Done btn not present") 

            # driver.find_element(By.XPATH, f"//button//span[ text() = 'Done']" ).click()                
            
            close_popup_btns = driver.find_elements( By.XPATH, f"//button[contains( @aria-label, 'Dismiss')  and contains(@class, 'dismiss') ]")
            if len(close_popup_btns) > 0:
                close_popup_btns[0].click()
                logger.info(f"Clicked on close popup btn")
            else:
                logger.info(f"Close btn not present")                 

# //button[contains( @aria-label, 'Dismiss')  and contains(@class, 'dismiss') ]            

            # review_btn = driver.find_element(By.XPATH, "//button[span[contains(text(), 'Review')]]")
            # review_btn.click()
            return False  # break loop
        except Exception as e:
            logger.error(f"Exception - {e}")
            return False  # neither found, safe to exit

def process_question( question_el ):
    try:
        input_el =question_el.find_elements(By.XPATH, f".//input")
        if not input_el:
            logger.info(f"No input element present")
            select_el = question_el.find_elements(By.XPATH, f".//select")
            if not select_el:
                logger.info(f"No select element present")
            else:
                logger.info(f"Select element present")
                label_element = select_el[0].find_element(By.XPATH, "./preceding-sibling::label[1]")
                logger.info(f"Question for select element - {label_element.text}")

                dropdown = Select(select_el[0])
                
                all_options = [option.text for option in dropdown.options]
                logger.info( all_options )

                dropdown.select_by_visible_text(all_options[1])
                logger.info(f"Selected option - '{ all_options[1] }'" )
        else:
            logger.info(f"Input element present")

            #check if checkbox
            input_el_class = input_el[0].get_attribute("class")
            logger.info(f"Class - {input_el_class}")

            if "checkbox" in input_el_class:
                logger.info(f"Radio button question")
                fieldset = input_el[0].find_element(By.XPATH, "./ancestor::fieldset")
                legend = fieldset.find_element(By.TAG_NAME, "legend")
                logger.info(f"Question - {legend.text}")
                labels = fieldset.find_elements(By.TAG_NAME, "label")
                for label in labels:
                    logger.info(f"Option - '{label.text}'")
                    if label.text.lower() == "yes":
                        label.click()
                        logger.info(f"Clicked on radio button label - '{label.text}'")
                        break

            else:
                total_exp_in_years = config["linkedin_config"]["total_exp_in_years"]
                current_ctc_in_years = config["linkedin_config"]["current_ctc_in_years"]
                expected_ctc_in_years = config["linkedin_config"]["expected_ctc_in_years"]            
                notice_in_days = config["linkedin_config"]["notice_in_days"]  
                rating = config["linkedin_config"]["rating"] 

                label = input_el[0].find_element(By.XPATH, f"./preceding-sibling::label" )
                logger.info(f"Label text - {label.text}")

                ip_value = input_el[0].get_attribute("value")
                if ip_value and ip_value.strip():
                    logger.info(f"Input element already have value - '{ip_value}'")
                else:
                    logger.info(f"Input element already does not have value, so adding value")

                    if "how many years" in label.text.lower() or "experience" in label.text.lower():
                        input_el[0].clear()
                        input_el[0].send_keys(total_exp_in_years)
                    elif "current ctc" in label.text.lower() or "fixed" in label.text.lower() or "current compensation" in label.text.lower():
                        input_el[0].clear()
                        input_el[0].send_keys(current_ctc_in_years)
                    elif "expected ctc" in label.text.lower() or "expected" in label.text.lower():
                        input_el[0].clear()
                        input_el[0].send_keys(expected_ctc_in_years)
                    elif "notice period" in label.text.lower() or "notice" in label.text.lower() or "how soon" in label.text.lower():
                        input_el[0].clear()
                        input_el[0].send_keys(notice_in_days)
                    elif "rating" in label.text.lower():
                        input_el[0].clear()
                        input_el[0].send_keys(rating)
                    elif "not referred" in label.text.lower():
                        input_el[0].clear()
                        input_el[0].send_keys("N/A")                
    except Exception as e:
        logger.error(f"Exception in process_question() - {e}")
        raise e

def run_job_apply_for_linkedin():
    try:
        success_job_list = []
        failed_job_list = []

        logger.info(f"Start - run_job_apply_for_linkedin()")
        linkedin_url =  config["job_apply_config"]["linkedin_url"]
        logger.info(f"Linkedin URL - '{linkedin_url}'")
        
        driver.get(linkedin_url)
        li_xpaths = config["linkedin_xpaths"]
        
        already_loggedin = check_if_already_loggedin( li_xpaths )
        if already_loggedin:
            logger.info(f"Already logged in..")
        else:
            logger.warning(f"Not already logged in... login required")
            if linkedin_login( li_xpaths ):
                logger.info(f"Start of job apply actions for linkedin")
                click("Job button", li_xpaths["jobs_menu"], driver)
                job_search_keywords = config["linkedin_config"]["job_search_keywords"]
                logger.info(f"Linkedin job search keywords - '{job_search_keywords}'")
                driver.find_element(By.XPATH, li_xpaths["job_search_input"]).send_keys(job_search_keywords)
                driver.find_element(By.XPATH, li_xpaths["job_search_input"]).send_keys(Keys.ENTER)
                logger.info(f"Entered job search keywords")

                driver.find_element(By.XPATH, r"//*[@id='search-reusables__filters-bar']//ul/li//button[ normalize-space( . )  = 'Easy Apply' ]").click()
                logger.info(f"Clicked on easy apply filter")


                driver.execute_script( "arguments[0].scrollIntoView()", driver.find_element( By.XPATH, r"//button[ contains(@class, 'jobs-search-pagination__indicator-button--active')  ]") )
                time.sleep(3)
                listed_jobs_ul = driver.find_elements(By.XPATH, r"//*[contains(@class, 'scaffold-layout__list-detail-container') ]//div[contains(@class, 'scaffold-layout__list ') ]//ul")
                wait = WebDriverWait(driver, 20)
                logger.info(f"Total jobs - {len(listed_jobs_ul)}")

                index = 1
                ## Loop for per job processing
                while True:
                    logger.info(f"Processing job number - {index} from current page")
                    try:
                        listed_jobs_ul = driver.find_elements(By.XPATH, r"//*[contains(@class, 'scaffold-layout__list-detail-container') ]//div[contains(@class, 'scaffold-layout__list ') ]//ul")
                        logger.info(f"Total jobs - {len(listed_jobs_ul)}")
                        if len(listed_jobs_ul) == index + 1:
                            logger.info(f"Last job on this page")
                            continue

                        logger.info(f"Job number - {index}")
                                    
                        try:
                            job_li_el = wait.until( EC.presence_of_element_located( (By.XPATH, f"//*[contains(@class, 'scaffold-layout__list-detail-container') ]//div[contains(@class, 'scaffold-layout__list ') ]//ul/li[{index+1}]//*[contains(@class, 'full-width artdeco-entity-lockup__title')]") ) )
                        except Exception as e:
                            logger.warning(f"Exception while searching job element -{e}")
                            logger.warning(f"Trying again to get it")
                            job_li_el = wait.until( EC.visibility_of_element_located( (By.XPATH, f"//*[contains(@class, 'scaffold-layout__list-detail-container') ]//div[contains(@class, 'scaffold-layout__list ') ]//ul/li[{index+1}]//*[contains(@class, 'full-width artdeco-entity-lockup__title')]") ) )

                        driver.execute_script("arguments[0].scrollIntoView()",job_li_el)
                        logger.info(f"Scrolled into view")
                        job_box_text = job_li_el.text
                        job_li_el.click()
                        logger.info(f"Clicked on job record - '{job_box_text}'")
                        time.sleep(2)

                        already_applied_btns = driver.find_elements( By.XPATH, "//div/span[  contains( @class, 'artdeco-inline-feedback' ) ]" )
                        if len( already_applied_btns) > 0:
                            logger.warning(f"Job is already "+ already_applied_btns[0].text)
                            index = index + 1
                            continue

                        easy_apply_buttons = driver.find_elements( By.XPATH, f"//button[ contains( @class, 'jobs-apply-button') ][1]" )

                        if len(easy_apply_buttons) < 1:                    
                            logger.warning(f"No easy apply btn, probably applied for this job already")        
                            logger.warning(f"Already applied for this job")
                            index = index + 1
                            continue
                        easy_apply_buttons[0].click()
                        logger.info(f"Clicked on easy apply button")                                        
                        time.sleep(1)

                        while_loop_count = 0
                        logger.info(f"while_loop_count - {while_loop_count}")
                        continue_with_questions = False

                        ## while loop for questions popup box
                        while True:
                            try:

                                popup_headings = driver.find_elements( By.XPATH, f"//h3[contains( @class, 't-16' )]" )
                                if len(popup_headings) > 0:
                                    logger.info(f"Heading text - {popup_headings[0].text}")
                                    if popup_headings[0].text.lower().strip() == "contact info":
                                        logger.info(f"On contact info page")
                                        continue_with_questions = True

                                        # should_continue = click_next_or_review()
                                        # if not should_continue:
                                        #     break                                    

                                    elif popup_headings[0].text.lower().strip() == "resume":
                                        logger.info(f"On resume info page")                   
                                        should_continue = click_next_or_review()
                                        if not should_continue:
                                            break

                                    else:
                                        logger.info(f"On unknown heading page - '{popup_headings[0].text}'")  
                                        continue_with_questions = True
                                else:
                                    logger.info(f"No heading - continue to check for questions")
                                    continue_with_questions = True

                                if continue_with_questions:
                                    questions_el = wait.until( EC.presence_of_all_elements_located( (By.XPATH, f"//div[ contains( @class, 'ph5' ) ]//h3/following-sibling::div") )  )   
                                    logger.info(f"Quesstion's count - {len(questions_el)}")                            
                                    logger.info(f"while_loop_count - {while_loop_count + 1}")

                                    for question_el in questions_el:
                                        process_question( question_el )

                                    should_continue = click_next_or_review()
                                    if not should_continue:
                                        success_job_list.append( job_box_text )
                                        break

                            except Exception as e:
                                logger.error(f"Exception while working on questions popup of job - '{e}'")
                                driver.find_element(By.XPATH,"//button[ contains( @aria-label, 'Dismiss') and contains(@class,'__dismiss') ]" ).click()
                                logger.info(f"Clicked on close btn")
                                driver.find_element(By.XPATH,"//button[ contains( @class, 'confirm-dialog-btn') ]/span[   text()= 'Discard' ]" ).click()
                                logger.info(f"Clicked on close button")                               
                                failed_job_list.append( job_box_text ) 


                        logger.info(f"job_box_text -  {job_box_text}")                
                        index = index + 1

                        next_job_el = driver.find_elements(By.XPATH, f"//*[contains(@class, 'scaffold-layout__list-detail-container') ]//div[contains(@class, 'scaffold-layout__list ') ]//ul/li[{index}]/following-sibling::*") 
                        if next_job_el:
                            logger.info(f"Next job is available loop will continue")
                        else:
                            logger.info(f"Next job is not available loop will break")
                            print(f"Next job is not available loop will break")
                            time.sleep(100)
                            break

                    except StaleElementReferenceException as e:
                        index = index + 1
                        logger.warning(f"Stale element exception occurred - {e}")
                        job_li_el = wait.until( EC.presence_of_element_located( (By.XPATH, f"//*[contains(@class, 'scaffold-layout__list-detail-container') ]//div[contains(@class, 'scaffold-layout__list ') ]//ul/li[{index+1}]//*[contains(@class, 'full-width artdeco-entity-lockup__title')]") ) )
                        job_box_text = job_li_el.text
                        logger.info(job_box_text)
                        driver.execute_script("arguments[0].scrollIntoView()",job_li_el)
                        job_li_el.click()
                        time.sleep(2)
                        logger.info(f"Scrolled into view -s")                
                    except Exception as e:
                        index = index + 1
                        logger.error(f"Error - {e}")        

                return success_job_list, failed_job_list
            else:
                logger.error(f"Login failed")

    except Exception as e:
        logger.error(f"Failed in - run_job_apply_for_linkedin() - {e}")
        raise e

if __name__ == "__main__":

    sender_email=None 
    receiver_email=None
    sender_pwd=None
    smtp_server_name=None 
    smtp_server_port=None
    driver = None

    logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    config = configparser.ConfigParser()
    config.read('./job_apply.conf')
    browser_choice = get_browser_from_args()

    if browser_choice.lower() == "edge":
        kill_browser(browser_choice)
        # edge_driver_path = r'C:\Users\Admin\Documents\Swapnil\PP\personal_projects\Naukri_automation\driver\msedgedriver.exe'
        edge_driver_path = config["job_apply_config"]["edgedriver_path"]
        logger.info(f"Driver path used -  {edge_driver_path}")
        service = Service(executable_path=edge_driver_path)
        driver = webdriver.Edge(service=service)    

    else:    
        kill_browser(browser_choice)
        webdriver_path = config["job_apply_config"]["webdriver_path"]
        chrome_options = Options()

        user_data_dir = config["job_apply_config"]["user_data_dir"]
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        chrome_options.add_argument(f"profile-directory=Default")
        chrome_options.add_argument(f"--remote-debugging-port=9222")
        chrome_options.add_argument(f"--no-sandbox")
        chrome_options.add_argument(f"--disable-dev-shm-usage")
        chrome_options.add_argument(f"--disable-extensions")

        service = Service(webdriver_path)
        logging.info("Service set")
        driver = webdriver.Chrome(service=service, options=chrome_options)

    logging.info("Driver set")
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
        if driver:
            take_full_screenshot(driver, filename="screenshot.png")

        if logger is not None:
            logger.info(f"Exception - {e}")
        if sender_email and receiver_email and sender_pwd and smtp_server_name and smtp_server_port:
            body = f"Failed to execute job apply automation with error - {e}"
            subject =  f"Job apply status report - {datetime.now().strftime('%d-%m-%Y')} - FAILED"
            send_email( sender_email, sender_pwd, receiver_email, smtp_server_name, smtp_server_port, subject, body)

    finally:
        driver.quit()
