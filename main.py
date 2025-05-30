from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import argparse

parser = argparse.ArgumentParser(description="Automate PopMart login and interaction.")

parser.add_argument("--email", required=True, help="Email for PopMart login")
parser.add_argument("--password", required=True, help="Password for PopMart login")
parser.add_argument("--user-data-dir", required=True, help="Chrome user data directory path")
parser.add_argument("--set-id", required=True, help="Pop Mart Set ID (check URL)")

args = parser.parse_args()

# Setup driver
# Set up Chrome options

options = Options()
user_data_dir=args.user_data_dir
options.add_argument(f"--user-data-dir={user_data_dir}")
options.add_argument(r"--profile-directory=Default")
options.add_argument("--start-maximized")

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
# Start Chrome with the set options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
set_id = args.set_id
url = f"https://www.popmart.com/us/pop-now/set/{set_id}"
driver.get(url)
wait = WebDriverWait(driver, 15)

# Accept the privacy policy
try:
    accept_button = wait.until(
        EC.element_to_be_clickable((By.CLASS_NAME, "policy_acceptBtn__ZNU71"))
    )
    accept_button.click()
except:
    pass

# Main loop to check each box
while True:
    print("🔍 Checking current box...")

    # Wait for containers to load
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class^='index_showBoxItem__']")))
    containers = driver.find_elements(By.CSS_SELECTOR, "[class^='index_showBoxItem__']")

    unlocked_found = False

    for img in containers:
        src = img.get_attribute("src")
        if "box_pic_with_shadow" in src:
            print("✅ Found unlocked container!")

            # Scroll + JavaScript click
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", img)
            driver.execute_script("arguments[0].click();", img)

            # Wait for the login modal to appear
            wait = WebDriverWait(driver, 10)
            login_modal = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "index_loginContainer__u_1sM")))

            # Enter email
            email_input = login_modal.find_element(By.ID, "email")
            email = args.email
            email_input.send_keys(email)

            # Click the 'CONTINUE' button
            continue_button = login_modal.find_element(By.CLASS_NAME, "index_loginButton__nvmup")
            continue_button.click()

            # Wait for login modal to appear
            try:
                login_modal = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "index_loginContainer__u_1sM")))

                # Optional: wait until email appears as confirmation that you're on the second step
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "index_disabledEmail__Dj16h")))

                # Enter password
                password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
                password_input.clear()
                password = args.password
                password_input.send_keys(password)

                # Click "SIGN IN" button
                sign_in_button = login_modal.find_element(By.XPATH, "//button[contains(text(), 'SIGN IN')]")
                driver.execute_script("arguments[0].click();", sign_in_button)

                print("🔐 Submitted login form.")

            except Exception as e:
                print(f"❌ Failed to complete login: {e}")

            # Wait for redirect to complete (URL change)
            wait.until(EC.url_changes("https://www.popmart.com/us/pop-now/set/81"))

            # Optionally wait for some known element to confirm the new page has loaded
            try:
                # Wait for the "ADD TO BAG" button to be clickable
                add_to_bag_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ADD TO BAG')]"))
                )
                # Click the button
                driver.execute_script("arguments[0].click();", add_to_bag_button)
                print("🛒 Clicked 'ADD TO BAG'")
            except Exception as e:
                print(f"❌ Failed to click 'ADD TO BAG': {e}")

            unlocked_found = True
            break

    # If we clicked one, we're done
    if unlocked_found:
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
        else:
            print("❌ No visible next arrow found. Stopping.")
            break
    except:
        print("❌ Failed to click next arrow.")
        break

# All done
print("🎯 Finished.")
input("Press Enter to close...")
driver.quit()
