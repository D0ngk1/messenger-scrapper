"""
Semi-automatic Messenger photo scraper using Selenium.
Workflow:
  1. Script opens Brave/Chromium and navigates to messenger.com
  2. You manually log in and pass the CAPTCHA
  3. Open the conversation you want to scrape in that browser tab
  4. Press Enter in the terminal to let the script continue
  5. Script scrolls up to load older messages, gathers image URLs, and downloads them
Notes:
  - Designed for personal backups only (your own account).
  - Be conservative with speed to avoid triggering security checks.
"""

import os
import requests
import hashlib
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
import time
import shutil

# -------------- Config ----------------
CHROMEDRIVER_PATH = "./chromedriver"
BROWSER_PATH = "/usr/bin/brave-browser"
PROFILE_PATH = "/home/igadu/.config/BraveSelenium"
PROFILE_DIR = "Profile1"

# Chrome options (Brave)
def setup_driver():    
    options = Options()
    options.binary_location = "/usr/bin/brave-browser"
    # options.add_argument("--headless") # Uncomment to run without opening window
    options.add_argument(f"--user-data-dir={PROFILE_PATH}")
    options.add_argument(f"--profile-directory={PROFILE_DIR}")
    options.add_argument("--start-maximized")
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def get_message_container(driver):
    """Find the scrollable message container"""
    # Find the div with role="none" and the specific classes
    containers = driver.find_elements(
        By.XPATH, 
        "//div[@role='none' and contains(@class, 'x78zum5') and contains(@class, 'xdt5ytf') and contains(@class, 'x1iyjqo2') and contains(@class, 'x6ikm8r') and contains(@class, 'x1odjw0f')]"
    )
    
    # Find the one that's actually scrollable
    for container in containers:
        try:
            scroll_height = driver.execute_script("return arguments[0].scrollHeight", container)
            client_height = driver.execute_script("return arguments[0].clientHeight", container)
            
            if scroll_height > client_height:
                return container
        except:
            continue
    
    # Return first one if found
    if containers:
        return containers[0]
    
    return None

def download_image(url, save_folder, filename):
    """Download a single image from URL"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            filepath = os.path.join(save_folder, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"  ✓ Downloaded: {filename}")
            return True
    except Exception as e:
        print(f"  ✗ Failed to download {filename}: {e}")
    return False

def get_image_hash(url):
    """Create a unique hash for an image URL to avoid duplicates"""
    return hashlib.md5(url.encode()).hexdigest()

def download_loaded_images(driver, save_folder="messenger_images"):
    """Download all images currently loaded in the conversation"""
    # Create save folder if it doesn't exist
    os.makedirs(save_folder, exist_ok=True)
    
    # Find all image elements in the conversation
    # Messenger uses img tags and background images
    images = driver.find_elements(By.XPATH, "//img[contains(@src, 'http')]")
    
    downloaded_hashes = set()
    download_count = 0
    
    # Try to load existing hashes to avoid re-downloading
    hash_file = os.path.join(save_folder, "downloaded_hashes.txt")
    if os.path.exists(hash_file):
        with open(hash_file, 'r') as f:
            downloaded_hashes = set(f.read().splitlines())
    
    print(f"\nFound {len(images)} images on page")
    
    for idx, img in enumerate(images):
        try:
            src = img.get_attribute('src')
            
            # Skip if not a valid image URL
            if not src or 'blob:' in src or 'data:' in src:
                continue
            
            # Skip small images (likely icons/emojis)
            try:
                width = img.get_attribute('width')
                height = img.get_attribute('height')
                if width and height and (int(width) < 50 or int(height) < 50):
                    continue
            except:
                pass
            
            # Create hash to check for duplicates
            img_hash = get_image_hash(src)
            
            if img_hash in downloaded_hashes:
                continue
            
            # Generate filename
            timestamp = int(time.time() * 1000)
            ext = 'jpg'
            if '.png' in src.lower():
                ext = 'png'
            elif '.gif' in src.lower():
                ext = 'gif'
            
            filename = f"img_{timestamp}_{idx}.{ext}"
            
            # Download the image
            if download_image(src, save_folder, filename):
                downloaded_hashes.add(img_hash)
                download_count += 1
                
                # Save hash to file
                with open(hash_file, 'a') as f:
                    f.write(f"{img_hash}\n")
            
            time.sleep(0.1)  # Small delay to avoid overwhelming the server
            
        except Exception as e:
            print(f"  Error processing image {idx}: {e}")
            continue
    
    print(f"Downloaded {download_count} new images")
    return download_count

def scroll_until_date(driver, target_date=None, max_scrolls=100, download_images=False, save_folder="messenger_images"):
    """
    Scrolls Messenger chat upwards to load older messages.
    """
    print("Looking for message container...")
    time.sleep(2)  # Wait for page to load
    
    message_container = get_message_container(driver)
    
    if not message_container:
        print("Could not find message container!")
        return False
    
    print("Found message container!")
    
    # Get initial scroll properties
    scroll_height = driver.execute_script("return arguments[0].scrollHeight", message_container)
    client_height = driver.execute_script("return arguments[0].clientHeight", message_container)
    scroll_top = driver.execute_script("return arguments[0].scrollTop", message_container)
    
    print(f"Initial - ScrollHeight: {scroll_height}, ClientHeight: {client_height}, ScrollTop: {scroll_top}")
    
    # Scroll parameters
    scroll_pause_time = 2
    no_change_count = 0
    
    print("Starting to scroll through messages...")
    
    for i in range(max_scrolls):
        try:
            # Re-find container to avoid stale element
            message_container = get_message_container(driver)
            
            if not message_container:
                print("Lost message container!")
                break
            
            # Get current scroll position
            current_scroll_top = driver.execute_script("return arguments[0].scrollTop", message_container)
            current_scroll_height = driver.execute_script("return arguments[0].scrollHeight", message_container)
            
            # Scroll to the very top (load older messages)
            driver.execute_script("arguments[0].scrollTo(0, 0)", message_container)
            
            print(f"Scroll {i + 1}/{max_scrolls} - ScrollTop: {current_scroll_top}, ScrollHeight: {current_scroll_height}")
            
            # Wait for new messages to load
            time.sleep(scroll_pause_time)
            
            # Re-find container after waiting
            message_container = get_message_container(driver)
            
            # Get new scroll position
            new_scroll_top = driver.execute_script("return arguments[0].scrollTop", message_container)
            new_scroll_height = driver.execute_script("return arguments[0].scrollHeight", message_container)
            
            print(f"  After - ScrollTop: {new_scroll_top}, ScrollHeight: {new_scroll_height}")
            
            # Check if scroll height increased (new messages loaded)
            if new_scroll_height > current_scroll_height:
                print(f"  ✓ Loaded new messages! Height increased by {new_scroll_height - current_scroll_height}")
                no_change_count = 0
                
                # Download images if enabled
                if download_images:
                    download_loaded_images(driver, save_folder)
                    
            # Check if we're at the top and nothing changed
            elif new_scroll_top == 0 and new_scroll_height == current_scroll_height:
                no_change_count += 1
                print(f"  No change detected ({no_change_count}/3)")
                
                if no_change_count >= 3:
                    print("Reached the top of the conversation!")
                    return True
            else:
                no_change_count = 0
                
        except StaleElementReferenceException:
            print("  Element became stale, re-finding container...")
            continue
        except Exception as e:
            print(f"  Error during scroll: {e}")
            continue
    
    print("Max scrolls reached")
    return False

def main():
    print("Starting Selenium on Brave")
    driver = setup_driver()
    
    try:
        driver.get("https://www.messenger.com/t/100047858612752/")
        
        # Wait a bit for page to fully load and user to navigate to conversation if needed
        print("Waiting for conversation to load...")
        time.sleep(5)
        
        target_date = "Sep 24 at 7:16 PM"
        found = scroll_until_date(driver, target_date, max_scrolls=100, download_images=True, save_folder="messenger_images")
        
        if found:
            print("\nScrolling complete! Now you can scrape images from this point.")
            # Do a final download of all images
            print("\nDoing final image download...")
            download_loaded_images(driver, save_folder="messenger_images")
        else:
            print("\nScrolling stopped. Date not reached.")
        
        print("Keeping browser open for 30 seconds...")
        time.sleep(30)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(30)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
