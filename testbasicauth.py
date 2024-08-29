from selenium import webdriver
import time

driver = webdriver.Chrome()
driver.maximize_window()
driver.get(f"https://admin:admin@the-internet.herokuapp.com/basic_auth")
time.sleep(10)