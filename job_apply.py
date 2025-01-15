


import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import logging

# Set up basic configuration
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("This log will be saved to a file.")


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


try:
    # Launch the URL
    url = r'https://www.naukri.com/mnjuser/homepage?utm_source=google&utm_medium=cpc&utm_campaign=Brand'  # Replace with your target URL
    driver.get(url)
    logging.info("URL Launched")

    # time.sleep(10)
    # print(f"after 10 sec delay")
    # driver.execute_script("window.stop();")\\\

    driver.find_element(By.XPATH, r"//div[text() = 'Jobs']").click()
    logging.info("Clicked on 'jobs' button")

    driver.find_element(By.XPATH, r'//*[text() = "Search jobs here"]').click()       
    logging.info("Clicked on 'Search jobs here' button") 
    keywords_to_search = "Python selenium"
    driver.find_element(By.XPATH, r'//*[@placeholder = "Enter keyword / designation / companies" ]').send_keys(f"{keywords_to_search}")
    logging.info(f"Entered text '{keywords_to_search}'") 
    driver.find_element(By.XPATH, r'//*[@placeholder = "Enter keyword / designation / companies" ]').send_keys(Keys.ENTER)
    logging.info(f"Pressed ENTER") 

    logging.info(f"Sorting jobs by date")   
    driver.find_element(By.XPATH, r'//*[@id = "filter-sort"]').click()        
    logging.info(f"Clicked on sort FILTER")       
    driver.find_element(By.XPATH, r'//li/a/span[ text() = "Date" ]').click()            
    logging.info(f"Clicked on DATE item from DROPDOWN")       
    

    all_jobs_on_page_el = driver.find_elements(By.XPATH, r'//div[ @class = "srp-jobtuple-wrapper"]')
    logging.info(f"All jobs count from this page - {str(len( all_jobs_on_page_el))}")       

    logging.info(f"Looping over all jobs of this page")       

    for i in range( 1, len( all_jobs_on_page_el), 1 ):
        try:
            logging.info(f"")       

            logging.info(f"************")       
            logging.info(f"************")                   
            logging.info(f"Iteration - {i}")       
            time.sleep(2)
            # all_jobs_on_page_el2 = driver.find_elements(By.XPATH, r'//div[ @class = "srp-jobtuple-wrapper"]')
            # title = all_jobs_on_page_el2[i].find_element(By.XPATH, r"//*[ @class = ' row1']/a").get_attribute("title")

            title = driver.find_element(By.XPATH, r'(//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row1"]/a)['+str(i)+']').get_attribute("title")  
            logging.info("title - " + str(title))            
            job_days_old = driver.find_element(By.XPATH, r'(//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row6"]/span[@class = "job-post-day " ])['+str(i)+']').text        
            job_days_old = job_days_old.lower()
            # job_old_str_list = [ "just now", "few hours ago", "days ago", "day ago"]
            if "30+" in job_days_old:           
                logging.warning(f"Job '{title}' is posted 30 days back so ignoring") 
            
            if "just now" in job_days_old or "few hours ago" in job_days_old or "days ago" in job_days_old or "day ago"  in job_days_old:
                logging.info(f"Job '{title}' is posted - {job_days_old}") 
                driver.find_element(By.XPATH, r'(//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row1"]/a)['+str(i)+']').click()
                logging.info(f"Clicked on job - '{title}'")
                window_handles = driver.window_handles
                logging.info(window_handles)
                driver.switch_to.window( window_handles[1] )
                try:
                    apply_button = driver.find_element(By.ID, "apply-button")
                    apply_button.click()
                    logging.info(f"Clicked on apply button")
                    try:
                        apply_message = driver.find_element(By.XPATH, '//*[@class = "apply-message"]').text
                        if "You have successfully applied" in apply_message:
                            logging.info(f"Successfully applied to job - {title}")
                    except Exception as e:
                        logging.info(f"Apply success message is not there, checking chatbot popup")


                    # //*[@class = "apply-message"]
                    logging.info(f"Checking if chatbot popup present")
                    try:
                        chatbot_popup_el = driver.find_element(By.ID, "_17go0qzspDrawer")
                    except Exception as e:
                        logging.info(f"Chatbot popup not present")

# 

                    logging.info(f"Applied to job - '{title}'")
                    time.sleep(10)
                    driver.close()
                    logging.info(f"Closed window - '{window_handles[1]}'") 
                    driver.switch_to.window(window_handles[0])               
                    logging.info(f"Switched back to main window") 

                except Exception as e:
                    logging.warning(f"Apply button not found for this job")
                    driver.close()
                    logging.info(f"Closed window - '{window_handles[1]}'") 
                    driver.switch_to.window(window_handles[0])               
                    logging.info(f"Switched back to main window")









            # '//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row1"]/a'
            # '//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row1"]/span[@class = "job-post-day " ]'            
            # //div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row6"]/span[@class = "job-post-day " ]
        except Exception as e:            
            logging.error(f"in exp block - {e}")




# 

    # placeholder="Enter keyword / designation / companies"

    print(f"after click on jobs")
    raise

    try:
        while True:
            time.sleep(3)
            # Find the button with class name 'bvtn' and click it
            button = driver.find_element(By.XPATH, r'//*[@id="main"]/div/div[1]/main/div[2]/div/div/span/div[2]/div/div[2]/div/div[3]/div/div[1]/span')
            button.click()
    except Exception as e:
        print(f"In exp {e}")
        driver.save_screenshot("screenshot.png")




    # Optionally, add some delay or further actions if needed
finally:
    # Close the browser
    driver.quit()
