import os
from selenium import webdriver
import selenium
import time
import urllib3
import argparse
from tkinter.filedialog import askopenfile
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
import absl.logging
import sys
from progressbar import progressbar
from os import getenv


global ip_list
global driver

if sys.platform in ('linux', 'darwin'):
    CLEAR = 'clear'
elif sys.platform == 'win32':
    CLEAR = 'cls'


# Disable SSL Warnings (for verify=False)
urllib3.disable_warnings()
# Disable WebDriver logging
LOGGER.setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('selenium').setLevel(logging.CRITICAL)
# Suppress Abseil logs
absl.logging.get_absl_handler().python_handler.stream = open(os.devnull, 'w')
absl.logging.set_verbosity(absl.logging.FATAL)
absl.logging.set_stderrthreshold(absl.logging.FATAL)


parser = argparse.ArgumentParser(description="Insert txt list of IP Address or Subnet as Destination Bypass on Cato Socket")
parser.add_argument("--wait", dest="wait_time", type=float, default=0.2,
                    help="How many seconds the WebDriver will between one IP/Subnet and the next [DEFAULT: 0.2]")
parser.add_argument("--verbose", dest="verbose", default=False, action="store_true",
                    help="Enable verbosity on stdout logging [DEFAULT: FALSE]")
args = parser.parse_args()
# How many seconds the WebDriver will wait between one IP/Subnet and the next
webdriver_time_per_ip = args.wait_time


def clear_term():
    os.system(CLEAR)


def load_list_from_file():
    # Load data from source file
    data = []
    file = askopenfile(mode="r", filetypes=[('All Files', '*.*')], title="Open File")
    for line in file.readlines():
        data.append(line.strip())
    global ip_list
    ip_list = data


def insert_data():
    # Insert loaded data into web field with ID "value" and press Enter confirm
    global ip_list
    for ip in progressbar(ip_list, redirect_stdout=True):
        driver.find_element(by="id", value="value").send_keys(ip)
        driver.find_element(by="id", value="value").send_keys(selenium.webdriver.Keys.ENTER)
        time.sleep(webdriver_time_per_ip)

    input("Please verify the inserted data and save, then press Enter to load a new menu...")


def main():
    # Define and open WebDriver
    options = webdriver.ChromeOptions()
    if args.verbose:
        options.add_argument('--log-level=0')
    else:
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
    global driver
    driver = webdriver.Chrome(options=options)

    print(f"Please login and go to the site Bypass page on the WebDriver.")
    url = getenv("CATO_CMA_URL", default="https://cc.catonetworks.com")
    driver.get(url)
    input("Press Enter to continue after you are logged in...\n\n")

    global ip_list
    ip_list = []

    while True:
        clear_term()
        if not ip_list:
            print("1) Load ip list form file (txt)")

        else:
            print("1) Load NEW ip list form file (txt)")
            print(f"2) Insert loaded data into value field (loaded: {len(ip_list)})")

        print("0) Exit")

        user_selection = input("> ")
        match user_selection:
            case "1":
                load_list_from_file()
            case "2":
                insert_data()
            case "0":
                print("Bye :)")
                driver.close()
                raise SystemExit(0)
            case _:
                print("Invalid selection")


if __name__ == "__main__":
    main()
