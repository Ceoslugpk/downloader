from selenium import webdriver
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)
driver.get("https://www.google.com")
print("Page title:", driver.title)
driver.quit()
