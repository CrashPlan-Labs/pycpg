#testing pyCPG... Does it actually work?!!!

import pycpg.sdk

import logging
import os
from datetime import datetime, timedelta
import argparse
import getpass
import pandas as pd

#define logging levels for py42 and for the script. We want the logs to putput to both standard out, and a file. 
#Definging handlers as done below does that.
pycpg.settings.debug.level = logging.ERROR
pycpg.settings.items_per_page = 1000

logging.basicConfig(
                    format='%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S',
                    level=logging.DEBUG,
                    handlers=[
                        logging.FileHandler(os.path.basename(__file__)+".log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)
#Global variables so they don't need to be passed to functions
global sdk
global execute
def parse_args():
    """Parses command line arguments"""
    parser = argparse.ArgumentParser(                    
                    prog='Testing Pycpg',
                    description='This tool will test pycpg',
                    epilog='')
    parser.add_argument('-u', '--username', type=str, help='Full username of a Customer Cloud Admin user')
    parser.add_argument('-c', '--cloud',  type=str, choices=['us1', 'us2', 'eu5'], help='Auto-enters url for the appropriate cloud')

    args = parser.parse_args()
    return args

def process_args(args):
    global execute
    """ Processes command line arguments into a dictionary of settings"""
    if args.username:
        username = args.username
    else:
        username = input("Please enter the username: ")

    if args.cloud:
        consoleUrl = selectCloudInfo(args.cloud)
    else: # Uses us1 cloud as a default
        cloudSelectorInput = input("Please enter the 3-letter code for your cloud (us1, us2, eu5) or press enter to use us1 as a default")
        if cloudSelectorInput == "":
            cloudSelectorInput = "us1"
        consoleUrl = consoleUrl(cloudSelectorInput)
    password = getpass.getpass()

    scriptSettings = {
        'username': username,
        'password': password,
        'consoleUrl': consoleUrl,
    }
    return scriptSettings

def selectCloudInfo(cloudSelectorString):
    """Returns console Url based on selector string entered"""
    cloudSelector = cloudSelectorString.lower()
    if cloudSelector == "us1":
        consoleUrl = "https://console.us1.crashplan.com"
    elif cloudSelector == 'us2':
        consoleUrl = "https://console.us2.crashplan.com"
    elif cloudSelector == 'eu5':
        consoleUrl = "https://console.eu5.cpg.crashplan.com"

    return consoleUrl

def df_from_py42_generator(generator,pageName):
    dataframe = pd.DataFrame()
    for page in generator:
        tmpFrame = pd.DataFrame(page[pageName])
        dataframe = pd.concat([dataframe,tmpFrame],ignore_index=True)
    return dataframe

def get_all_devices():
    response = sdk.devices.get_all(active=True,include_backup_usage=True)
    allDevicesDf = df_from_py42_generator(response,'computers')
    allDevicesDf = allDevicesDf.sort_values(by=['userUid', 'name'])
    return allDevicesDf

# Main program
logging.info("Starting run of the script")
scriptSettings = process_args(parse_args())
logging.info(f"consoleUrl: {scriptSettings['consoleUrl']}")
logging.info(f"username: {scriptSettings['username']}")

##Connect to console and py42 SDK so we can use that connection to get devices, remove and re-add legal hold state, as well as deactivate devices in a stable session.
totpNeeded = input("Please enter 'y' or 'Y' if you need to use a totp code:")
if (totpNeeded.lower() == "y"):
    totp = input("Please enter your totp code:")
    sdk = pycpg.sdk.from_local_account(scriptSettings['consoleUrl'], scriptSettings['username'],scriptSettings['password'],totp)
else:
    sdk = pycpg.sdk.from_local_account(scriptSettings['consoleUrl'], scriptSettings['username'],scriptSettings['password'])

allDevicesDf = get_all_devices() 

#print(allDevicesDf.to_string())

pages = sdk.devices.get_all(active=True,include_backup_usage=True)  # pages has 'generator' type
for page in pages:  # page has 'PycpgResponse' type
    devices = page["computers"]
    for device in devices:
        userUid = device["userUid"]
        name = device["name"]
        print(f"{userUid}: {name}")

response = sdk.devices.get_user("orrisontest@crashplan.com")
print(response)  # JSON as Dictionary - same as print(response.text)
print(response.raw_text)  # Raw API response
print(response.status_code)  # 200


password = input("Please input your password: ")

sdk = pycpg.sdk.from_local_account("https://console.us2.crashPlan.com", "andrew.orrison+us5@crashplan.com", (password))