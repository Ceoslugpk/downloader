import os
import time
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
VECTEEZY_EMAIL = os.getenv("VECTEEZY_EMAIL")
VECTEEZY_PASSWORD = os.getenv("VECTEEZY_PASSWORD")
DOWNLOAD_DIR = "/path/to/download/dir"  # Update this path on your VPS

# Initialize Telegram Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the bot is started."""
    update.message.reply_text("Bot is running. Send me a Vecteezy link to download.")

def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle incoming messages (Vecteezy links)."""
    message = update.message.text
    if "vecteezy.com" in message:
        update.message.reply_text("Processing your request...")
        download_file(update, message)
    else:
        update.message.reply_text("Please send a valid Vecteezy link.")

def download_file(update: Update, url: str) -> None:
    """Download the file from Vecteezy and send it back via Telegram."""
    # Configure Selenium for headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
    })

    driver = webdriver.Chrome(options=chrome_options)
    try:
        # Log in to Vecteezy
        driver.get("https://www.vecteezy.com/sign-in")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(VECTEEZY_EMAIL)
        driver.find_element(By.NAME, "password").send_keys(VECTEEZY_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Navigate to the provided link and download
        driver.get(url)
        download_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.download-button")))
        download_button.click()

        # Wait for download to complete (adjust sleep time based on file size)
        time.sleep(10)

        # Find the latest downloaded file
        files = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))]
        if not files:
            raise Exception("No files were downloaded.")
        latest_file = max(files, key=os.path.getctime)

        # Send the file back via Telegram
        with open(latest_file, 'rb') as file:
            bot.send_document(chat_id=update.message.chat_id, document=file)

    except Exception as e:
        bot.send_message(chat_id=update.message.chat_id, text=f"Error: {str(e)}")
    finally:
        driver.quit()

def main() -> None:
    """Start the Telegram bot."""
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
