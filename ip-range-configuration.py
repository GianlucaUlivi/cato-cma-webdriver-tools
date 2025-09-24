import os
from os import getenv
from selenium import webdriver
import time
import urllib3
import argparse
from tkinter.filedialog import askopenfile
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
import absl.logging
from progressbar import progressbar


global subnet_list
global driver


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


parser = argparse.ArgumentParser(description="Insert CSV list of IP Subnet in Resources > IP Ranges")
parser.add_argument("--wait", dest="wait_time", type=float, default=0.2,
                    help="How many seconds the WebDriver will between each operation [DEFAULT: 0.2]")
parser.add_argument("--verbose", dest="verbose", default=False, action="store_true",
                    help="Enable verbosity on stdout logging [DEFAULT: FALSE]")
args = parser.parse_args()
# How many seconds the WebDriver will wait between one IP/Subnet and the next
webdriver_time_per_operation = args.wait_time



def load_list_from_file():
    # Load data from source file
    data = []
    file = askopenfile(mode="r", filetypes=[('All Files', '*.*')], title="Open CSV File")
    for line in file.readlines():
        subnet_name, subnet_ip = line.strip().split(",")
        subnet = {
            "name": subnet_name.strip(),
            "ip": subnet_ip.strip()
        }
        data.append(subnet)
    global subnet_list
    subnet_list = data


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

    print(f"Please login and go to the Resource/IP Ranges page on the WebDriver.")
    url = getenv("CATO_CMA_URL", default="https://cc.catonetworks.com")
    driver.get(url)
    input("Press Enter to continue after you are logged in and on the ip range page...\n")

    global subnet_list
    subnet_list = []

    load_list_from_file()

    for subnet in progressbar(subnet_list, redirect_stdout=True):
        # Click on the "new" button
        driver.find_element(by="xpath", value="//button[@data-testid='catobutton-new']").click()
        time.sleep(webdriver_time_per_operation)

        # Insert loaded data into web field with ID "name" and "subnet" and click on Apply to confirm
        driver.find_element(by="id", value="name").send_keys(subnet['name'])
        driver.find_element(by="id", value="subnet").send_keys(subnet['ip'])
        time.sleep(webdriver_time_per_operation)

        # Click on the "apply" button
        driver.find_element(by="xpath", value="//button[@data-testid='catobutton-apply']").click()
        time.sleep(webdriver_time_per_operation)

    input("Please verify the inserted data and save, then press Enter to close...")
    driver.close()
    print("Bye :)")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
