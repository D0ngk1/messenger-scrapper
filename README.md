# Messenger Image Scraper 📸

A Python Selenium automation tool that scrolls through Meta Messenger conversations and automatically downloads all images to your local machine.

## 🌟 Features

- **Automatic Scrolling**: Intelligently scrolls through conversations to load older messages
- **Smart Image Detection**: Finds and downloads all images from the conversation
- **Duplicate Prevention**: Uses MD5 hashing to avoid downloading the same image twice
- **Stale Element Handling**: Robust handling of dynamic DOM updates
- **Size Filtering**: Automatically filters out small icons and emojis
- **Progress Tracking**: Real-time console output showing scroll and download progress
- **Persistent History**: Maintains a hash file to prevent re-downloading across sessions

## 🛠️ Prerequisites

### Required Software
- Python 3.7+
- Chrome/Brave Browser
- ChromeDriver (matching your browser version)

### Python Dependencies
```bash
pip install selenium requests
```

## 📦 Installation

1. **Clone or download this repository**

2. **Install dependencies**

3. **Download ChromeDriver**
   - Visit [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
   - Download the version matching your Chrome/Brave browser
   - Place `chromedriver` in the project directory

4. **Configure your browser profile**
   - Update `PROFILE_PATH` and `PROFILE_DIR` in the script
   - Or log in manually when the browser opens

## ⚙️ Configuration

Edit the following variables in the script:

```python
# Browser Configuration
CHROMEDRIVER_PATH = "./chromedriver"  # Path to chromedriver
BROWSER_PATH = "/usr/bin/brave-browser"  # Path to your browser
PROFILE_PATH = "/home/user/.config/BraveSelenium"  # Browser profile directory
PROFILE_DIR = "Profile1"  # Profile name

# Scroll Configuration
max_scrolls = 100  # Maximum number of scroll attempts
scroll_pause_time = 2  # Seconds to wait between scrolls

# Download Configuration
download_images = True  # Enable/disable automatic downloading
save_folder = "messenger_images"  # Folder to save images
```

## 🚀 Usage

1. **Run the script**
```bash
python main.py
```

2. **Navigate to your conversation**
   - The browser will open to Messenger
   - Log in if needed (or use saved profile)
   - Open the conversation you want to scrape

3. **Wait for completion**
   - The script will automatically scroll and download images
   - Progress is shown in the console
   - Images are saved to the `messenger_images/` folder

## 📁 Output Structure

```
messenger_images/
├── img_1234567890_0.jpg
├── img_1234567891_1.png
├── img_1234567892_2.jpg
├── ...
└── downloaded_hashes.txt  # Tracks downloaded images
```

## 🔍 How It Works

### 1. Container Detection
The script locates the scrollable message container using XPath:
```python
//div[@role='none' and contains(@class, 'x78zum5') 
    and contains(@class, 'xdt5ytf') 
    and contains(@class, 'x1iyjqo2')]
```

### 2. Scroll Mechanism
- Scrolls to the top of the container: `scrollTo(0, 0)`
- Waits for new messages to load
- Detects new content by monitoring `scrollHeight` changes
- Stops when no new messages load after 3 attempts

### 3. Stale Element Handling
Re-finds the container before and after each scroll to avoid `StaleElementReferenceException`:
```python
message_container = get_message_container(driver)  # Re-find
driver.execute_script("arguments[0].scrollTo(0, 0)", message_container)
time.sleep(2)
message_container = get_message_container(driver)  # Re-find again
```

### 4. Image Download Process
- Finds all `<img>` tags with valid HTTP URLs
- Filters images by size (skips < 50px)
- Creates MD5 hash of URL for duplicate detection
- Downloads image using `requests` library
- Saves hash to prevent re-downloading

### 5. Duplicate Prevention
Uses MD5 hashing for efficient duplicate detection:
```python
img_hash = hashlib.md5(url.encode()).hexdigest()
if img_hash in downloaded_hashes:
    continue  # Skip already downloaded
```

## ⚠️ Important Notes

### Stale Element Exception
Modern web apps like Messenger dynamically update the DOM as you scroll. This causes element references to become "stale" (invalid). 

**Solution**: Re-find elements after each scroll operation.

### Rate Limiting
- Script includes 0.1s delay between downloads
- Adjust if you encounter rate limiting issues

### Privacy & Legal
- ⚠️ This tool is for **personal backup purposes only**
- Always respect Meta's Terms of Service
- Don't use for unauthorized data collection
- Respect others' privacy - only scrape your own conversations

## 🐛 Troubleshooting

### "Could not find message container"
- Ensure you've opened a conversation before the script runs
- Update the XPath selector if Messenger's structure changed
- Increase the initial wait time

### "StaleElementReferenceException"
- This should be handled automatically
- If it persists, increase `scroll_pause_time`

### ChromeDriver version mismatch
```bash
# Check Chrome version
chrome --version

# Download matching ChromeDriver
# Visit: https://chromedriver.chromium.org/downloads
```

### Images not downloading
- Check console for error messages
- Verify image URLs are accessible
- Check internet connection
- Increase timeout in `download_image()` function

## 🔧 Advanced Usage

### Run in Headless Mode
Uncomment this line to run without opening a visible browser:
```python
options.add_argument("--headless")
```

### Adjust Scroll Speed
```python
scroll_pause_time = 3  # Slower, more reliable
scroll_pause_time = 1  # Faster, may miss content
```

### Change Download Folder
```python
save_folder = "my_custom_folder"
```

## 📊 Performance

- **Speed**: ~2 seconds per scroll + download time
- **Memory**: Minimal (only stores hashes, not images in memory)
- **Disk Space**: Depends on number of images in conversation


## 📝 License

MIT License - feel free to use and modify for personal projects.

## 🙏 Acknowledgments

- Selenium WebDriver team
- Stack Overflow community for debugging tips
- Meta Messenger (for not making this too difficult!)

## 📧 Contact

Have questions or suggestions? Feel free to reach out!

---

**Disclaimer**: This tool is provided as-is for educational and personal backup purposes. Users are responsible for complying with all applicable laws and terms of service.
