import os
import sys
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import csv
import io
import re
import ast
import tkinter as tk
import configparser
from tkinter import messagebox
from send_email import send_email
import parsers

def safe_del(self):
    try:
        if hasattr(self, "service") and self.service:
            self.quit()
    except Exception:
        pass

uc.Chrome.__del__ = safe_del

os.makedirs("results", exist_ok=True)

# Disable interpolation to allow '%' in URLs so some URLs don't break
config = configparser.ConfigParser(interpolation=None)
config.read("settings.ini")

enable_error = config["prompts"].getboolean("enable_error_prompts")
enable_info = config["prompts"].getboolean("enable_info_prompts")
email_direction = config["email"].get("direction", "ltr")

raw_sites = config["sites"].get("disabled_sites", "[]")
try:
    disabled_sites = ast.literal_eval(raw_sites)
    if not isinstance(disabled_sites, list):
        disabled_sites = []
except Exception:
    disabled_sites = []

def show_error_prompt(title, message):
    try:
        if enable_error:
            root = tk.Tk()
            root.withdraw()
            root.lift()
            root.attributes('-topmost', True)
            root.update()
            messagebox.showerror(title, message)
            root.destroy()
            sys.exit(1)
        else:
            print(f"\n[ERROR] {title}\n{'-' * 60}\n{message}\n{'-' * 60}\n")
            sys.exit(1)
    except tk.TclError:
        print(f"\n[ERROR] {title}\n{'-' * 60}\n{message}\n{'-' * 60}\n")
        if not enable_error:
            sys.exit(1)

def show_info_prompt(title, message):
    try:
        if enable_info:
            root = tk.Tk()
            root.withdraw()
            root.lift()
            root.attributes('-topmost', True)
            root.update()
            messagebox.showinfo(title, message)
            root.destroy()
        else:
            print(f"\n[INFO] {title}\n{'-' * 60}\n{message}\n{'-' * 60}\n")
    except tk.TclError:
        print(f"\n[INFO] {title}\n{'-' * 60}\n{message}\n{'-' * 60}\n")

def create_driver(headless=True):
    try:
        options = uc.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("window-size=1920,1080")
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(30)
        return driver
    except WebDriverException as e:
        msg = (
            f"Error initializing Chrome driver:\n{e}\n\n"
            "How to fix:\n"
            "- Make sure Google Chrome is installed and updated to the latest version.\n"
            "- Check that no antivirus or firewall is blocking Chrome.\n"
            "- Close other Chrome instances that might interfere.\n"
            "- Run the script with proper permissions."
        )
        show_error_prompt("Driver Initialization Failed", msg)

def get_html(driver, url, wait_selector):
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
        )
        return driver.page_source
    except TimeoutException:
        msg = (
            f"Timeout waiting for {wait_selector} on {url}\n\n"
            "How to fix:\n"
            "- Check your internet connection.\n"
            "- Make sure the URL is correct and accessible.\n"
            "- If the page is slow, increase wait times or adjust the selector.\n"
            "- Ensure Google Chrome is installed and updated."
        )
        show_error_prompt("Page Fetch Failed", msg)
    except WebDriverException as e:
        msg = (
            f"Error fetching {url}:\n{e}\n\n"
            "How to fix:\n"
            "- Check your internet connection.\n"
            "- Ensure the website isn’t blocking automated browsers.\n"
            "- Make sure Chrome is installed and updated."
        )
        show_error_prompt("Page Fetch Failed", msg)

def list_of_dicts_to_csv_str(data):
    if not data:
        return ""
    all_fields = set()
    for row in data:
        all_fields.update(row.keys())
    all_fields = list(all_fields)
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=all_fields)
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()

def compare_and_write_csv(filename, data_list):
    new_data = data_list
    try:
        with open(filename, "r", encoding="utf-8-sig") as f:
            existing_csv = f.read()
        existing_data = list(csv.DictReader(io.StringIO(existing_csv)))
    except FileNotFoundError:
        existing_data = []
    except OSError as e:
        msg = (
            f"Cannot read {filename}:\n{e}\n\n"
            "How to fix:\n"
            "- Make sure the file is not open in another program.\n"
            "- Check that you have read permissions for this folder.\n"
            "- Ensure there is enough disk space."
        )
        show_error_prompt("CSV Read Error", msg)

    added = [item for item in new_data if item not in existing_data]
    removed = [item for item in existing_data if item not in new_data]

    if not added and not removed:
        return False

    csv_str = list_of_dicts_to_csv_str(new_data)
    try:
        with open(filename, "w", encoding="utf-8-sig", newline="") as f:
            f.write(csv_str)
    except OSError as e:
        msg = (
            f"Cannot write {filename}:\n{e}\n\n"
            "How to fix:\n"
            "- Make sure the file is not open in another program.\n"
            "- Check that you have write permissions for this folder.\n"
            "- Ensure there is enough disk space."
        )
        show_error_prompt("CSV Write Error", msg)

    return {"added": added, "removed": removed}

def changes_to_html(changes, direction):
    if not changes:
        return ""
    if direction not in ("ltr", "rtl"):
        raise ValueError("direction must be 'ltr' or 'rtl'")
    text_align = "right" if direction == "rtl" else "left"
    html = f'''
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <style>
      a {{ color: #0645ad; }}
      hr {{ border: 1px solid #000; margin: 20px 0; }}
      p.added {{ font-size: 32px; font-weight: bold; color: green; }}
      p.removed {{ font-size: 32px; font-weight: bold; color: red; }}
      ul {{ margin-bottom: 10px; }}
      li strong {{ color: #000; }}
    </style>
  </head>
  <body style="direction: {direction}; text-align: {text_align}; background-color: #ffffff; color: #000000; font-family: Arial, sans-serif;">
'''
    first = True
    for url, change_dict in changes.items():
        if not first:
            html += "<hr>"
        html += f'<p><a href="{url}" style="font-size:22px;font-weight:bold;">URL: {url}</a></p>'
        if change_dict.get("added"):
            html += '<p class="added">+</p>'
            for change in change_dict["added"]:
                html += "<ul>"
                for k, v in change.items():
                    if v:
                        html += f"<li><strong>{k}:</strong> {v}</li>"
                html += "</ul>"
        if change_dict.get("removed"):
            html += '<p class="removed">-</p>'
            for change in change_dict["removed"]:
                html += "<ul>"
                for k, v in change.items():
                    if v:
                        html += f"<li><strong>{k}:</strong> {v}</li>"
                html += "</ul>"
        first = False
    html += "</body></html>"
    return html

def safe_name(url):
    name = re.sub(r"[^\w\d]+", "_", url)
    return name.strip("_")

if __name__ == '__main__':
    all_changes = {}
    driver = None
    try:
        driver = create_driver(headless=True)  # * You might need to set headless to False for some websites to work
        if not driver:
            sys.exit(1)
        for url, parser, wait_selector in parsers.urls_and_parsers:
            if any(site in url for site in disabled_sites):
                print(f"Skipping disabled site: {url}")
                continue
            print(f"Fetching {url} ...")
            content = get_html(driver, url, wait_selector)
            try:
                parsed_data = parser(content)
            except Exception as e:
                msg = (
                    f"Parser failed for {url}:\n{e}\n\n"
                    "How to fix:\n"
                    "- Check that the parser logic matches the page structure.\n"
                    "- Make sure the page loaded correctly.\n"
                    "- Update parser if the website changed its HTML."
                )
                show_error_prompt("Parser Error", msg)
            print(f"Parsed {len(parsed_data)} items from {url}")
            if parsed_data:
                name = safe_name(url)
                csv_path = os.path.join("results", f"results_{name}.csv")
                changes = compare_and_write_csv(csv_path, parsed_data)
                if changes:
                    all_changes[url] = changes

        if all_changes:
            html_content = changes_to_html(all_changes, direction=email_direction)
            try:
                send_email("Important Changes Detected", html_content)
                show_info_prompt("Info", "Important Changes Detected")
            except Exception as e:
                msg = (
                    f"Failed to send email:\n{e}\n\n"
                    "How to fix:\n"
                    "- Check your internet connection.\n"
                    "- Verify email server settings and credentials.\n"
                    "- Ensure firewall or antivirus is not blocking SMTP."
                )
                show_error_prompt("Email Sending Failed", msg)
        else:
            show_info_prompt("Info", "No changes detected.")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
            try:
                service = getattr(driver, "service", None)
                if service:
                    stop = getattr(service, "stop", None)
                    if callable(stop):
                        try:
                            stop()
                        except Exception:
                            pass
                    proc = getattr(service, "process", None)
                    if proc:
                        try:
                            proc.kill()
                        except Exception:
                            pass
            except Exception:
                pass
