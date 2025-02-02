
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
import openai
import google.generativeai as genai
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from job_apply_lib import *


def call_chatgpt(question_):
    try:
        logger.info(f"In call_chatgpt()")
        logger.info(f"Question- {question_}")

        # # openai.api_key = 'your-api-key'
        # openai.api_key = os.getenv("OPENAI_API_KEY")    

        # def get_answer(question):
        #     response = openai.Completion.create(
        #         model="gpt-3.5-turbo",  # Or any other available GPT model
        #         prompt=question,
        #         max_tokens=150
        #     )
        #     answer = response['choices'][0]['text'].strip()
        #     return answer
        # # question = "What is the capital of France?"
        # answer = get_answer(question_)
        # print(answer)
        
        my_info = """my name is swapnil dhamal. I am having 3.5 years of experience in Python, Ansible, java, selenium and automation. 
        I am writing this prompt to let you give anwser of below question according to my information in very short way. 
        For example if question is 'How many year of exp you have in python' answer should be '3.5'.
        my 10th percentage is 76
        my 12th percentage is 60
        my graduation percentage/ cgpa is 9.16 

        Below is the question (This question is not for you its for me, so even if its mentioned 'you' consider itv as me and answer ). \n\n"""

        question_ = my_info + question_
        print(f"Question - {question_}")

        api_key = os.getenv("GEMINI_API_KEY")  
        # genai.configure(api_key=r"AIzaSyCmzWETgqauRDxDzo8KXZd3_lxD06D6j1o")
        genai.configure(api_key=api_key)        
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(question_)
        print(f"Response - {resp.text}")
        logger.info(f"Response - {resp.text}")        

        return resp.text.lower()
    except  Exception as e:
        logger.error(f"Failed in - call_chatgpt(question) - {e}")

def run_job_apply_automation( platform ):
    try:
        logger.info(f"Start - run_job_apply_automation( platform )")
        if platform.lower().strip() == "naukri":
           run_job_apply_for_naukri()
        if platform.lower().strip() == "linkedin":
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

        next_page = 1
        while True:

            driver.refresh()

            all_jobs_on_page_el = driver.find_elements(By.XPATH, xpaths["all_jobs_on_page"])
            logging.info(f"All jobs count from this page - {str(len( all_jobs_on_page_el))}")       
            logging.info(f"Looping over all jobs of this page")

            current_page = driver.find_element(By.XPATH, xpaths["current_page_number"]).text
            logging.info(f"Current page number - '{current_page}'")

            if current_page == next_page:
                logger.warning(f"Even after clicking next button still on same page, probably next page is not fully loaded")
                time.sleep(3)

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
                                    # current_w_h = driver.current_window_handle
                                    # logging.debug(f"Window handle will be closed - {driver.current_window_handle}")
                                    # driver.close()
                                    # driver.switch_to.window( window_handles[0] )
                                    # logging.info(f"Switched back to main window -'{driver.current_window_handle}'")

                                    job_skip_count = job_skip_count + 1

                                    # find chats list
                                    chat_list_elements = driver.find_elements(By.XPATH, "//div[@class = 'chatbot_Drawer chatbot_right']//*/ul/li")
                                    logging.debug(f"List items chat bot - '{chat_list_elements}'")
                                    last_q_text = chat_list_elements[-1].find_element(By.XPATH, "./div[contains( @class, 'botMsg')]//*/span").text
                                    logging.info(f"Chatbot latest question text - '{last_q_text}'")

                                    answer = call_chatgpt(last_q_text)

                                    ##
                                    input_box_present = driver.find_elements( By.XPATH, r"//div[@class = 'chatbot_Drawer chatbot_right']//*/ul/following-sibling::div//*[ contains( @class, 'chatbot_InputContainer')]" )
                                    if input_box_present:
                                        logger.info(f"Input box present { len(input_box_present) }")

                                    singleselect_radio_button_present = driver.find_elements(By.XPATH, r"//div[@class = 'chatbot_Drawer chatbot_right']//*/ul/following-sibling::div//*[ contains( @class, 'singleselect-radiobutton-container')]")                                        
                                    if singleselect_radio_button_present:
                                        logger.info(f"Radio button present { len(singleselect_radio_button_present) }")
                                    ##check for answer input field or check box
                                    checkbox_present = driver.find_element(By.XPATH, f"//div[@class = 'chatbot_Drawer chatbot_right']//*/ul/following-sibling::*[contains(@class, 'multiselectcheckboxes') ]")
                                    # checkbox_present

                                    driver.find_element(By.XPATH, f"//div[@class = 'chatbot_Drawer chatbot_right']//*/ul/following-sibling::*[contains(@class, 'multiselectcheckboxes') ]//label[contains( @for, '{answer.capitalize()}') ]" ).click()

                                    # //div[@class = 'chatbot_Drawer chatbot_right']//*/ul/following-sibling::*[1]//input[ contains( @type, "checkbox") ]

                                    ## to check if checkbox is there
                                    # //div[@class = 'chatbot_Drawer chatbot_right']//*/ul/following-sibling::*[contains(@class, "multiselectcheckboxes") ]

                                    # get q
                                    # call open ai api
                                    #get anwser

                                    continue

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
                        print("Clicked on next button")
                        time.sleep(5)
                        next_page = 1 + next_page
                        # time.sleep(100)


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
        logger.info(f"***********Start - run_job_apply_for_linkedin()")
        linkedin_job_site_url = config["linkedin_config"]["job_site_url"]
        driver.get( linkedin_job_site_url )
        logging.info("URL Launched")
        # input("press any key to continue")
        
        # driver.find_element(By.XPATH, r'//*[contains( @id, "jobs-search-box-keyword-id" )]').send_keys("Python Developer")
        driver.find_element(By.XPATH, r'//div[contains( @class, "search-global-typeahead" )]').click()  
        logger.info(f"Clcied")      
        time.sleep(5)
        driver.find_element(By.XPATH, r'//*[contains( @class, "search-global-typeahead" )]//input').send_keys("Python Developer")
        logger.info(f"Entered text")      
        driver.find_element(By.XPATH, r'//*[contains( @class, "search-global-typeahead" )]//input').send_keys(Keys.ENTER)
        logger.info(f"Entered text")      
        driver.find_element(By.XPATH, r"//*[@id='search-reusables__filters-bar']//ul/li//button[ normalize-space( . )  = 'Jobs' ]").click()
        logger.info(f"clcikedd on jobs")      
        driver.find_element(By.XPATH, r"//*[@id='search-reusables__filters-bar']//ul/li//button[ normalize-space( . )  = 'Easy Apply' ]").click()
        logger.info(f"clcikedd on easy apply")      

        driver.execute_script( "arguments[0].scrollIntoView()", driver.find_element( By.XPATH, r"//button[ contains(@class, 'jobs-search-pagination__indicator-button--active')  ]") )
        time.sleep(3)
        listed_jobs_ul = driver.find_elements(By.XPATH, r"//*[contains(@class, 'scaffold-layout__list-detail-container') ]//div[contains(@class, 'scaffold-layout__list ') ]//ul")

        wait = WebDriverWait(driver, 20)

        logger.info(f"Total jobs - {len(listed_jobs_ul)}")

        # for index, job_li in enumerate( listed_jobs_ul ):
        index = 1
        while True:
            logger.info(f"Processing job number - {index} from current page")
            try:
                listed_jobs_ul = driver.find_elements(By.XPATH, r"//*[contains(@class, 'scaffold-layout__list-detail-container') ]//div[contains(@class, 'scaffold-layout__list ') ]//ul")
                logger.info(f"Total jobs - {len(listed_jobs_ul)}")                    
                if len(listed_jobs_ul) == index+1:
                    logger.info(f"Last job on this page")
                    continue

                logger.info(f"Job number - {index}")
                            
                try:
                    job_li_el = wait.until( EC.presence_of_element_located( (By.XPATH, f"//*[contains(@class, 'scaffold-layout__list-detail-container') ]//div[contains(@class, 'scaffold-layout__list ') ]//ul/li[{index+1}]//*[contains(@class, 'full-width artdeco-entity-lockup__title')]") ) )
                except Exception as e:
                    job_li_el = wait.until( EC.visibility_of_element_located( (By.XPATH, f"//*[contains(@class, 'scaffold-layout__list-detail-container') ]//div[contains(@class, 'scaffold-layout__list ') ]//ul/li[{index+1}]//*[contains(@class, 'full-width artdeco-entity-lockup__title')]") ) )


                driver.execute_script("arguments[0].scrollIntoView()",job_li_el)
                logger.info(f"Scrolled into view")
                t = job_li_el.text
                job_li_el.click()
                logger.info(f"Clicked on job record")
                time.sleep(2)

                # click on easy apply
                # easy_apply_button = wait.until( EC.presence_of_element_located( (By.XPATH, f"//button[ contains( @class, 'jobs-apply-button') ][1]") )  ).click()
                easy_apply_button = wait.until( EC.presence_of_all_elements_located( (By.XPATH, f"//button[ contains( @class, 'jobs-apply-button') ][1]") )  )
                if not easy_apply_button:
                    logger.Warning(f"Already applied for this job")
                    continue
                easy_apply_button[0].click()

                logger.info(f"Clicked on easy apply button")                
                time.sleep(1)
                wait.until( EC.presence_of_element_located( (By.XPATH, f"//button[ @aria-label ='Continue to next step' ]") )  ).click()
                time.sleep(1)
                wait.until( EC.presence_of_element_located( (By.XPATH, f"//button[ @aria-label ='Continue to next step' ]") )  ).click()

                time.sleep(1)
                questions_el = wait.until( EC.presence_of_all_elements_located( (By.XPATH, f"//div[ contains( @class, 'ph5' ) ]//h3/following-sibling::div") )  )   
                logger.info(f"Quesstion's count - {len(questions_el)}")

                for question_el in questions_el:                    
                    input_el =question_el.find_elements(By.XPATH, f".//input")
                    if not input_el:
                        logger.info(f"No input element present")
                        select_el =question_el.find_elements(By.XPATH, f".//select")
                        if not select_el:
                            logger.info(f"No select element present")
                        else:
                            logger.info(f"Select element present")
                    else:
                        logger.info(f"Input element present")

                        #
                        #check if checkbox
                        input_el_class = input_el[0].get_attribute("class")
                        logger.info(f"Class - {input_el_class}")

                        if "checkbox" in input_el_class:
                            logger.info(f"Radio button question")
                        else:
                            label = input_el[0].find_element(By.XPATH, f"./preceding-sibling::label" )
                            logger.info(f"Label text - {label.text}")
                            if "how many years" in label.text.lower():
                                input_el[0].clear()
                                input_el[0].send_keys('3')
                            elif "current ctc" in label.text.lower():
                                input_el[0].clear()
                                input_el[0].send_keys('500000')
                            elif "expected ctc" in label.text.lower():
                                input_el[0].clear()
                                input_el[0].send_keys('1000000')


                # click on review btn
                
                driver.find_element(By.XPATH, f"//button[ contains( @aria-label, 'Review your application' ) ]" ).click()                
                logger.info(f"Clicked on review button")
                driver.find_element(By.XPATH, f"//button[contains(@aria-label, 'Submit application' ) ]" ).click()
                logger.info(f"Clicked on submit button")
                driver.find_element(By.XPATH, f"//button//span[ text() = 'Done']" ).click()                
                logger.info(f"Clicked on Done")
                



                # t = driver.find_element( By.XPATH, rf"//*[contains(@class, 'scaffold-layout__list-detail-container') ]//div[contains(@class, 'scaffold-layout__list ') ]//ul/li[{index}]//*[contains(@class, 'full-width artdeco-entity-lockup__title')]" ).text
                logger.info(f"t -  {t}")                
                index = index + 1

                next_job_el = driver.find_elements(By.XPATH, f"//*[contains(@class, 'scaffold-layout__list-detail-container') ]//div[contains(@class, 'scaffold-layout__list ') ]//ul/li[{index}]/following-sibling::*") 
                if next_job_el:
                    logger.info(f"Next job is available loop will continue")
                else:
                    logger.info(f"Next job is not available loop will break")
                    print(f"Next job is not available loop will break")

                    time.sleep(100)
                    break
                

            except StaleElementReferenceException:
                index = index + 1
                logger.warning(f"stale el")
                job_li_el = wait.until( EC.presence_of_element_located( (By.XPATH, f"//*[contains(@class, 'scaffold-layout__list-detail-container') ]//div[contains(@class, 'scaffold-layout__list ') ]//ul/li[{index+1}]//*[contains(@class, 'full-width artdeco-entity-lockup__title')]") ) )
                t = job_li_el.text
                logger.info(t)
                driver.execute_script("arguments[0].scrollIntoView()",job_li_el)
                job_li_el.click()
                time.sleep(2)
                logger.info(f"Scrolled into view -s")                
            except Exception as e:
                index = index + 1
                logger.error(f"Error - {e}")
        # time.sleep(100)

# cliec


    except Exception as e:
        logger.error(f"Failed in - 'run_job_apply_for_linkedin()' -{e}")
        body = f"Failed to execute job apply automation with error - {e}"
        subject =  f"{str(job_search_platform.capitalize())} Job apply status report - {datetime.now().strftime('%d-%m-%Y')} - FAILED"
        # send_email( sender_email, sender_pwd, receiver_email, smtp_server_name, smtp_server_port, subject, body)        
# 
if __name__ == "__main__":
    # logger =None
    sender_email=None 
    receiver_email=None
    sender_pwd=None
    smtp_server_name=None 
    smtp_server_port=None
    

    date = datetime.now().strftime("%d-%m-%y")
    logging.basicConfig(filename=f'app_{date}.log', filemode="w", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    config = configparser.ConfigParser()
    config.read('./job_apply.conf')

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
    driver.implicitly_wait(10)
    logging.info("Driver set")
    driver.maximize_window()

    load_dotenv()

    job_search_platforms = config["job_apply_config"]["job_search_platforms"].split(",")
    logger.info(f"Job search platforms - {job_search_platforms}")

    try:


        sender_email, receiver_email, sender_pwd, smtp_server_name, smtp_server_port = get_mail_config( config ) 

        if job_search_platforms == [] or job_search_platforms == None:
            logger.warning(f"No platform is present to check jobs, check config")

        for job_search_platform in job_search_platforms:
            logger.info(f"Job search started for platform - '{job_search_platform}'")
            run_job_apply_automation( platform = job_search_platform)

    except Exception as e:
        if logger is not None:
            logger.info(f"Exception - {e}")
        if sender_email and receiver_email and sender_pwd and smtp_server_name and smtp_server_port:
            body = f"Failed to execute job apply automation with error - {e}"
            subject =  f"Job apply status report - {datetime.now().strftime('%d-%m-%Y')} - FAILED"
            send_email( sender_email, sender_pwd, receiver_email, smtp_server_name, smtp_server_port, subject, body)

    finally:
        driver.quit()
