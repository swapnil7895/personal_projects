


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

# logging.debug("This is a debug message")
# logging.info("This is an info message")
# logging.warning("This is a warning message")
# logging.error("This is an error message")
# logging.critical("This is a critical message")



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
print("after service set")
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.implicitly_wait(10)
print("after driver set")

try:
    # Launch the URL
    url = r'https://www.naukri.com/mnjuser/homepage?utm_source=google&utm_medium=cpc&utm_campaign=Brand'  # Replace with your target URL
    driver.get(url)
    print(f"after get url")
    
    # time.sleep(10)
    # print(f"after 10 sec delay")
    # driver.execute_script("window.stop();")\\\

    driver.find_element(By.XPATH, r"//div[text() = 'Jobs']").click()
    driver.find_element(By.XPATH, r'//*[text() = "Search jobs here"]').click()        
    driver.find_element(By.XPATH, r'//*[@placeholder = "Enter keyword / designation / companies" ]').send_keys("Python selenium")
    driver.find_element(By.XPATH, r'//*[@placeholder = "Enter keyword / designation / companies" ]').send_keys(Keys.ENTER)

# sort by date\\\\
    driver.find_element(By.XPATH, r'//*[@id = "filter-sort"]').click()        
    driver.find_element(By.XPATH, r'//li/a/span[ text() = "Date" ]').click()            
    

    all_jobs_on_page_el = driver.find_elements(By.XPATH, r'//div[ @class = "srp-jobtuple-wrapper"]')
    print( "All jobs on this page" + str(len( all_jobs_on_page_el)))


    for i in range( len( all_jobs_on_page_el) ):
        try:
            if i == 0:
                continue

            print(i)
            time.sleep(2)
            # all_jobs_on_page_el2 = driver.find_elements(By.XPATH, r'//div[ @class = "srp-jobtuple-wrapper"]')
            # title = all_jobs_on_page_el2[i].find_element(By.XPATH, r"//*[ @class = ' row1']/a").get_attribute("title")

            title = driver.find_element(By.XPATH, r'(//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row1"]/a)['+str(i)+']').get_attribute("title")  
            print("title - " + title)

            

            # '//div[ @class = "srp-jobtuple-wrapper"]//*[ @class = " row1"]/a'
        except Exception as e:
            print("in exp block")
            time.sleep(1000)




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
