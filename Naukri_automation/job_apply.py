
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
from job_apply_lib import *


if __name__ == "__main__":
    
    job_apply_count = 0
    job_skip_count = 0
    job_apply_success_count = 0

    logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    config = configparser.ConfigParser()
    config.read('./job_apply.conf')
    xpaths = config["xpaths"]

    keywords_to_search = config["job_apply_config"]["keywords_job_search"]
    logging.info(f"Keywords to search for job - {keywords_to_search}")

    print("start")
    webdriver_path = r'./driver/chromedriver.exe'
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=C:/Users/swapn/AppData/Local/Google/Chrome/User Data")
    chrome_options.add_argument(f"profile-directory=Default")
    chrome_options.add_argument(f"--remote-debugging-port=9222")
    chrome_options.add_argument(f"--no-sandbox")
    chrome_options.add_argument(f"--disable-dev-shm-usage")
    chrome_options.add_argument(f"--disable-extensions")

    # chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    # user_data_dir = r"C:\Users\swapn\AppData\Local\Google\Chrome\User Data"
    # profile_dir = "Default"  # or "Profile 1", "Profile 2", etc.
    # service = Service(ChromeDriverManager().install())

    service = Service(webdriver_path)
    logging.info("Service set")

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    logging.info("Driver set")
    driver.maximize_window()

    try:
        naukri_job_site_url = config["job_apply_config"]["job_site_url"]
        driver.get( naukri_job_site_url )
        logging.info("URL Launched")
        # driver.execute_script("window.stop();")\\\

        driver.find_element(By.XPATH, xpaths["jobs_btn"]).click()
        logging.info("Clicked on 'jobs' button")

        driver.find_element(By.XPATH, xpaths["search_jobs_here_btn"]).click()
        logging.info("Clicked on 'Search jobs here' button")
        driver.find_element(By.XPATH, xpaths["jobsearch_textarea"]).send_keys(f"{keywords_to_search}")
        logging.info(f"Entered text '{keywords_to_search}'")
        driver.find_element(By.XPATH, xpaths["jobsearch_textarea"] ).send_keys(Keys.ENTER)
        logging.info(f"Pressed ENTER")

        if config["job_apply_config"]["sort_jobs_by_date"].lower() == "true":
            logging.info(f"Sorting jobs by date")
            driver.find_element(By.XPATH, xpaths["sort_filter_btn"]).click()
            logging.info(f"Clicked on sort FILTER")
            driver.find_element(By.XPATH, xpaths["sort_filter_date_field"]).click()
            logging.info(f"Clicked on DATE item from DROPDOWN")
        else:
            logger.info(f"Keeping default sort job filter")    
        
        pdf_file_name = initialize_pdf( config )

        while True:

            all_jobs_on_page_el = driver.find_elements(By.XPATH, xpaths["all_jobs_on_page"])
            logging.info(f"All jobs count from this page - {str(len( all_jobs_on_page_el))}")       
            logging.info(f"Looping over all jobs of this page")


            current_page = driver.find_element(By.XPATH, xpaths["current_page_number"]).text
            logging.info(f"Current page number - '{current_page}'")
            if current_page == "3":
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
                    validated_job = validate_job_title( job_title, config )
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
                    # //a[contains( @class, "styles_btn-secondary")]//span[contains( text(), "Next")]
                    # '//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row1"]/a'
                    # '//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row1"]/span[@class = "job-post-day " ]'            
                    # //div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row6"]/span[@class = "job-post-day " ]
                    # placeholder="Enter keyword / designation / companies"

    finally:
        driver.quit()
