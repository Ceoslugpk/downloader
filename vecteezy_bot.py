import os
import time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
VECTEEZY_EMAIL = os.getenv("VECTEEZY_EMAIL")
VECTEEZY_PASSWORD = os.getenv("VECTEEZY_PASSWORD")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR")

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Bot is running. Send me a Vecteezy link to download.")

async def handle_message(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    if "vecteezy.com" in message:
        await update.message.reply_text("Processing your request...")
        try:
            await download_file(update, message)
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")
    else:
        await update.message.reply_text("Please send a valid Vecteezy link.")

async def download_file(update: Update, url: str) -> None:
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
    })

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    try:
        # Login
        driver.get("https://www.vecteezy.com/sign-in")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(VECTEEZY_EMAIL)
        driver.find_element(By.NAME, "password").send_keys(VECTEEZY_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)

        # Download
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.download-button"))).click()
        time.sleep(10)

        # Send file
        files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(('.zip', '.eps', '.svg'))]
        if files:
            latest = max(files, key=lambda f: os.path.getctime(os.path.join(DOWNLOAD_DIR, f)))
            await update.message.reply_document(open(os.path.join(DOWNLOAD_DIR, latest), 'rb'))
        else:
            await update.message.reply_text("Downloaded file not found")

    except Exception as e:
        await update.message.reply_text(f"Error during download: {str(e)}")
    finally:
        driver.quit()

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
