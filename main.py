import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, Label, Entry, Button, font, Toplevel, Menu
import requests
from xml.etree import ElementTree as ET
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
import os
import subprocess  # For opening the folder
import platform

# UI setup for the main window
root = tk.Tk()
root.title("l00f00's Crawl and Capture")

# Initialize custom font right after the root window
custom_font = font.Font(family="Roboto", size=10)

# Set the application icon
##logo_path = './ico/app_logo.ico' if platform.system() == 'Windows' else './ico/app_logo.png'
##root.iconbitmap(logo_path) if platform.system() == 'Windows' else root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=logo_path))

# Initialize configuration
config = {
    'webdriver_path': r'.\chromeDriver\chromedriver.exe'
}

# Update and configuration functions remain the same
def update_config():
    global config
    config['webdriver_path'] = webdriver_entry.get()
    with open('config.txt', 'w') as config_file:
        config_file.write(config['webdriver_path'])
    messagebox.showinfo("Configuration", "Configuration updated successfully", parent=configuration_window)
    configuration_window.destroy()

def show_configuration_window():
    global configuration_window, webdriver_entry
    configuration_window = Toplevel(root)
    configuration_window.title("Configuration")
    configuration_window.config(bg="black")
    Label(configuration_window, text="ChromeDriver Path:", bg="black", fg="white", font=custom_font).pack(side=tk.TOP, fill=tk.X)
    webdriver_entry = Entry(configuration_window, bg="black", fg="white", insertbackground="white", font=custom_font)
    webdriver_entry.pack(side=tk.TOP, fill=tk.X, pady=(0,10))
    webdriver_entry.insert(0, config['webdriver_path'])
    save_button = Button(configuration_window, text="Save Configuration", command=update_config, bg="black", fg="white", font=custom_font)
    save_button.pack(side=tk.TOP, fill=tk.X)

# Setup menu
menu_bar = tk.Menu(root)
root.config(menu=menu_bar, bg="black")
config_menu = tk.Menu(menu_bar, tearoff=0, bg="black", fg="white", font=custom_font)
menu_bar.add_cascade(label="Configuration", menu=config_menu)
config_menu.add_command(label="Set Path", command=show_configuration_window)

def take_screenshots():
    urls = text_area.get('1.0', tk.END).strip().split('\n')
    save_path = save_path_entry.get()
    cookie_banner_selector = cookie_banner_entry.get()
    num_screenshots = 0
    
    if not save_path:
        messagebox.showerror("Error", "Please select a path to save screenshots.", parent=root)
        return
    if not urls or urls == ['']:
        messagebox.showerror("Error", "Please enter at least one URL.", parent=root)
        return
    
    service = Service(executable_path=config['webdriver_path'])
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')  # Uncomment to start the browser maximized
    options.add_argument('--ignore-certificate-errors')  # Ignore SSL errors
    options.add_argument('--ignore-ssl-errors')  # Ignore SSL errors
    options.add_argument('--no-sandbox')  # Bypass OS security
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    options.add_argument('--disable-gpu')  # Applicable to Windows OS only
    options.add_argument('--disable-software-rasterizer')  # Applicable to Windows OS only
    options.add_argument('--disable-extensions')  # Disables extensions
    options.add_argument('--disable-infobars')  # Disables the info bar
    options.add_argument('--disable-popup-blocking')  # Disables popup blocking
    options.add_argument('--disable-extensions')  # Disables extensions
    options.add_argument('--disable-notifications')  # Disables notifications
    options.add_argument('--disable-default-apps')  # Disables default apps
    driver = webdriver.Chrome(service=service, options=options)
    
    for idx, url in enumerate(urls):
        if url:
            driver.get(url)
            sleep(2)
            if cookie_banner_selector:
                try:
                    elements = driver.find_elements(By.CLASS_NAME, cookie_banner_selector)
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            sleep(1)
                            break
                except Exception as e:
                    print(f"Cookie banner not found or not clickable for class try ID: {url}, error: {str(e)}")
                    elements = driver.find_elements(By.ID, cookie_banner_selector)
                    for element in elements:
                        if element.is_displayed():
                            element.click()
                            sleep(1)
                            print(f"Cookie banner clicked for ID: {url}")
                            break
                    print(f"Cookie banner not found or not clickable for ID: {url}, error: {str(e)}")
                
            screenshot_path = os.path.join(save_path, f'screenshot_{idx}.png')
            driver.save_screenshot(screenshot_path)
            num_screenshots += 1
            
    driver.quit()
    messagebox.showinfo("Success", f"Screenshots taken successfully. Total {num_screenshots} images captured.", parent=root)
    subprocess.run(['explorer', save_path], check=True)

def select_path():
    directory = filedialog.askdirectory()
    if directory:
        save_path_entry.delete(0, tk.END)
        save_path_entry.insert(0, directory)

def fetch_sitemap():
    sitemap_url = sitemap_url_entry.get()
    if sitemap_url:
        try:
            response = requests.get(sitemap_url)
            response.raise_for_status()
            root = ET.fromstring(response.content)
            urls = [url.text for url in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
            text_area.delete('1.0', tk.END)
            text_area.insert(tk.END, '\n'.join(urls))
            if save_path_entry.get():
                with open(os.path.join(save_path_entry.get(), 'sitemap_urls.txt'), 'w') as f:
                    f.write('\n'.join(urls))
            messagebox.showinfo("Success", f"Added {len(urls)} URLs from the sitemap.", parent=root)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=root)



# UI container setup
container = tk.Frame(root, bg="black")
container.pack(padx=10, pady=10)

# UI elements setup
Label(container, text="Sitemap URL:", bg="black", fg="white", font=custom_font).pack(side=tk.TOP, fill=tk.X)
sitemap_url_entry = Entry(container, bg="black", fg="white", insertbackground="white", font=custom_font)
sitemap_url_entry.pack(side=tk.TOP, fill=tk.X, pady=(0,10))
##fetch_sitemap_button = Button(container, text="Fetch Sitemap", command=fetch_sitemap, bg="black", fg="white", font=custom_font)
##fetch_sitemap_button.pack(side=tk.TOP, fill=tk.X)

Label(container, text="Save Path:", bg="black", fg="white", font=custom_font).pack(side=tk.TOP, fill=tk.X)
save_path_entry = Entry(container, bg="black", fg="white", insertbackground="white", font=custom_font)
save_path_entry.pack(side=tk.TOP, fill=tk.X, pady=(0,10))
select_path_button = Button(container, text="Browse", command=select_path, bg="black", fg="white", font=custom_font)
select_path_button.pack(side=tk.TOP, fill=tk.X)
fetch_sitemap_button = Button(container, text="Fetch Sitemap", command=fetch_sitemap, bg="black", fg="white", font=custom_font)
fetch_sitemap_button.pack(side=tk.TOP, fill=tk.X)

text_area = scrolledtext.ScrolledText(container, height=10, bg="black", fg="white", insertbackground="white", font=custom_font)
text_area.pack(side=tk.TOP, fill=tk.BOTH, pady=(10,10))

Label(container, text="Cookie Banner Selector (ID or Class):", bg="black", fg="white", font=custom_font).pack(side=tk.TOP, fill=tk.X)
cookie_banner_entry = Entry(container, bg="black", fg="white", insertbackground="white", font=custom_font)
cookie_banner_entry.pack(side=tk.TOP, fill=tk.X, pady=(0,10))

start_button = Button(container, text="Take Screenshots", command=take_screenshots, bg="black", fg="white", font=custom_font)
start_button.pack(side=tk.TOP, fill=tk.X)

# Start the main loop
root.mainloop()