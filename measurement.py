'''

This script will take readings of your current location and store the answers to the following questions:
  - How many access points can you see at any given location?
  - When multiple access points are available, how many users are connected to each one?
  - Which access point does your machine connect to? Is this the best one? Strongest signal? Fastest rates? Is it chosen randomly?

The scripts use the following two tools to determine this information:
  - Airport: Command Line wireless utility for Mac OSX.
  - Netifaces: Python Library for working with interfaces

Because of the use of the airport command the program only supports being run
on Mac OSX systems.


Installation Instructions:
  - Run the script installation.sh. The installation does the following:
    - Creates a symbolic linking to your airport tool on Mac OSX

'''
from subprocess import check_output, CalledProcessError, STDOUT
import csv
import datetime
import sys
import json
import time
import netifaces
import re

# Number of times you attempt using airport tool
number_attempts = 5

def _get_access_points(dateandtime,location):
    '''
    This method will use the airport command line tool to retrieve the number of access points that are
    visible on the McGill Network. Since most students connect using WPA, we will only check the access
    points that begin with WPA. The script will save this data into a csv file and will prompt the user to
    specify the location that the reading was taken.

    The information stored in the csv file includes (links to explanations):
        - SSID: Service Set IDentifier: http://www.pcmag.com/encyclopedia/term/51942/ssid
        - BSID: https://www.quora.com/Whats-the-difference-between-a-BSSID-and-an-ESSID
        - Wireless RSSI Level:  http://www.speedguide.net/faq/what-is-wireless-rssi-level-418
        - Channel
        - HT
        - CC
        - Security (WPA2 generally)

    '''
    try:
        result = check_output(["airport","-s"],shell=False)
    except CalledProcessError as e:
        return False

    access_points = result.strip().split('\n')
    access_points = access_points[1:] # remove the first entry since that's just the header
    results = [access_point.strip().split() for access_point in access_points]
    wpa_mcgill_results = []
    try:
        wpa_mcgill_results = [result for result in results if result[0]=='wpa.mcgill.ca'] # remove results that aren't wpa.mcgill.ca
    except IndexError as e:
        pass

    if not wpa_mcgill_results:
        return False

    name = "Access Points: " + str(dateandtime) + ' - ' + str(location) + ".csv"
    with open(name, "wb") as f:
        writer = csv.writer(f)
        writer.writerows(wpa_mcgill_results)

    return True

def get_access_points(dateandtime,location):
    '''

    The airport tool fails if used multiple times in a short period of time. One way around this is
    to try using multiple times. An attempt is made once every second. If the attempt doesn't work after
    number of attempts time, the user will be prompted to try again.

    '''
    success = False
    for i in range(number_attempts):
        success = _get_access_points(dateandtime,location)
        if success:
            break
        time.sleep(1)
    return success

def get_users_connected():
    '''

    This method will determine the number of devices that are currently connected to a network using ping and arp.
    First the program will automatically detect all of your interfaces and check for interfaces on MAC osx for WIFI (en0 and en1).
    Then it will attempt to get the network address and then send a broadcast ping to all devices. This should update the local ARP
    table which we then query to get all of the devices on the network.

    '''
    broadcast_addresses = []
    for interface in netifaces.interfaces():
        if interface.startswith('en') and netifaces.AF_INET in netifaces.ifaddresses(interface):
            links = netifaces.ifaddresses(interface)[netifaces.AF_INET]
            try:
                for item in links:
                    broadcast_addresses.append(item['broadcast'])
            except IndexError as e:
                print("No broadcast found on this interface")

    users_connected = []
    for address in broadcast_addresses:
        print("Pinging: %s"%(address))
        res = check_output(['ping', '-c', '5', address])
        objects_in_network = check_output(['arp','-a'])
        answer = [user for user in objects_in_network.strip().split('\n') if re.match(r'\web[0-9]+.wireless.mcgill.ca[\w\W]',user.strip())]
        users_connected.append({address:len(answer)})

    return users_connected



def get_current_connection_info(dateandtime, location):
    '''

    Will use the airport commandline tool to get info about the user's current connection. See examples for information recorded.

    '''
    try:
        result = check_output(["airport","-I"],stderr=STDOUT)
    except CalledProcessError as e:
        return False

    result = dict((elem.strip().split(":",1) for elem in result.strip().split('\n')))
    result['users_connected'] = get_users_connected()
    name = "Connection Info: " + str(dateandtime) + ' - ' + str(location) + ".json"
    with open(name, 'w') as outfile:
        json.dump(result, outfile,indent=4, sort_keys=True)


if __name__ == '__main__':
    print("Hello! Please make sure to Airport installed before starting.")
    print("You may run installation.sh in order to install them.")

    # Step 0: Get Date and Location
    dateandtime = datetime.datetime.now()
    prompt = "Please input your location:"
    location = raw_input(prompt)

    # Step 1: Getting Access points. Attempt to use airport tool multiple times. If it doesn't work then
    # we prompt the user to restart
    print("Getting Access Point Data")
    step_1_completed = False
    counter = 1
    while not step_1_completed:
        print("Attempt %d"%(counter))
        step_1_completed = get_access_points(dateandtime,location)
        if not step_1_completed:
            result = raw_input("Was not able to successfully get information about access points. Try again? (Yes or No)")
            if result == 'Yes':
                counter +=1
                continue
            else:
                sys.exit(-1)

    # Step 2: Getting Information about current connection and storing in JSON File
    print("Getting Current Connection Info")
    get_current_connection_info(dateandtime,location)


    print("Done")
