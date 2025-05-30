from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import argparse
import time

parser = argparse.ArgumentParser(description="Automate PopMart login and interaction.")

parser.add_argument("--email", required=True, help="Email for PopMart login")
parser.add_argument("--password", required=True, help="Password for PopMart login")
parser.add_argument("--user-data-dir", required=True, help="Chrome user data directory path")
parser.add_argument("--set-id", required=True, help="Pop Mart Set ID (check URL)")

args = parser.parse_args()

# Setup driver
options = Options()
user_data_dir = args.user_data_dir
options.add_argument(f"--user-data-dir={user_data_dir}")
options.add_argument(r"--profile-directory=Default")
options.add_argument("--start-maximized")

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

set_id = args.set_id
url = f"https://www.popmart.com/us/pop-now/set/{set_id}"
driver.get(url)
quick_wait = WebDriverWait(driver, 2, poll_frequency=0.1)

# Accept the privacy policy if prompted
try:
    accept_button = quick_wait.until(
        EC.element_to_be_clickable((By.CLASS_NAME, "policy_acceptBtn__ZNU71"))
    )
    accept_button.click()
except:
    pass

while True:
    print("🔍 Checking current box...")

    # Wait for containers to load
    quick_wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class^='index_showBoxItem__']")))
    containers = driver.find_elements(By.CSS_SELECTOR, "[class^='index_showBoxItem__']")

    unlocked_found = False

    for img in containers:
        src = img.get_attribute("src")
        # Modified condition to always be False for testing cycling through boxes
         if "box_pic_with_shadow" in src:
            print("✅ Found unlocked container!")

            # Scroll + JavaScript click
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", img)
            driver.execute_script("arguments[0].click();", img)

            # Wait for redirect URL change after clicking unlocked container
            quick_wait.until(EC.url_changes(url))

            try:
                add_to_bag_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ADD TO BAG')]"))
                )
                driver.execute_script("arguments[0].click();", add_to_bag_button)
                print("🛒 Clicked 'ADD TO BAG'")
            except Exception as e:
                print(f"❌ Failed to click 'ADD TO BAG': {e}")

            unlocked_found = True
            break

    if unlocked_found:
        print("🎯 Finished - unlocked container found and processed.")
        break

    # Print the current box number (before moving to next)
    try:
        box_number_elem = driver.find_element(By.CLASS_NAME, "index_boxNumber__7k_Uf")
        print(f"📦 Current Box Number: {box_number_elem.text}")
    except:
        print("⚠️ Box number not found.")

    # Click the "Next Box" button (visible arrow)
    try:
        next_buttons = driver.find_elements(By.CLASS_NAME, "index_nextImg__PTfZF")
        visible_next = None
        for btn in next_buttons:
            if "display: block" in btn.get_attribute("style"):
                visible_next = btn
                break

        if visible_next:
            visible_next.click()
            print("🔄 No unlocked containers. Moved to next box.")
            time.sleep(1)  # Allow next box to load

            # Wait for the next box number element to confirm loading
            try:
                quick_wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "index_boxNumber__7k_Uf"))
                )
            except:
                print("⚠️ Timeout waiting for next box to load.")
        else:
            print("❌ No visible next arrow found. Stopping.")
            break
    except Exception as e:
        print(f"❌ Failed to click next arrow: {e}")
        break

print("🚪 Exiting script.")
input("Press Enter to close...")
driver.quit()
