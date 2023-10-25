import requests
import csv
import json
from collections import defaultdict
from requests.auth import HTTPBasicAuth
from prettyprinter import pprint
import time
import datetime
import os

from get_db import *


class Device (object):
    def __init__(self, device_id, hostname, ip, location, os, serial):
        self.__device_id = device_id
        self.__hostname = hostname
        self.__ip = ip
        self.__location = location
        if self.__location is None:
            self.__location = 'N/A'

        self.__os_version = os
        self.__serial = serial
        self.__temp = list()

        self.__flagged = False

    def get_device_id(self):
        return self.__device_id

    def get_hostname(self):
        return self.__hostname

    def get_ip(self):
        return self.__ip

    def get_location(self):
        return self.__location

    def get_os_version(self):
        return self.__os_version

    def get_serial(self):
        return self.__serial

    def get_temp(self):
        return self.__temp[0]

    def is_flagged(self):
        return self.__flagged

    def set_flag(self):
        self.__flagged = True

    def record_temps(self, temps):
        self.__temp.append(temps)


class DNACenter (object):

    def __init__(self, username, password, base_url):
        # PUBLIC Properties
        self.username = username
        self.password = password
        self.base_url = base_url
        # PRIVATE Properies
        self.__auth_token = self.__get_auth_token()
        self.__devices = {}
        # DISABLE REQUESTS WARNINGS
        requests.packages.urllib3.disable_warnings()
        # COLLECT DEVICES DATA
        self.__collect_devices_data()
        # FLAG BUGS

    def __get_auth_token(self):
        r = requests.request("POST", '%s/dna/system/api/v1/auth/token' % self.base_url,
                             auth=HTTPBasicAuth(self.username, self.password), verify=False)
        if r.status_code == 200:
            response = r.json()

            return response['Token']

        else:
            return "Error! HTTP %s Response" % (r.status_code)

    """

	PRIVATE CLASS METHODS

	"""

    def __dna_headers(self):
        return {'Content-Type': 'application/json', 'x-auth-token': self.__auth_token}

    def __devices_by_csv(self, csv_file):
        columns = defaultdict(list)
        with open(csv_file) as f:
            reader = csv.DictReader(f)  # read rows into a dictionary format
            # read a row as {column1: value1, column2: value2,...}
            for row in reader:
                for (k, v) in row.items():  # go over each column name and value
                    # append the value into the appropriate list
                    columns[k].append(v)
                    # based on column name k

        return columns

    def __get_command_runner_task(self, task_id):
        while True:
            r = requests.get("%s/dna/intent/api/v1/task/%s" % (self.base_url,
                             task_id), headers=self.__dna_headers(), verify=False)
            response = r.json()

            if r.status_code == 200 or r.status_code == 202:
                progress = r.json()['response']['progress']

            else:
                break

            if "fileId" in progress:  # keep checking for task completion
                break

        file_id = json.loads(progress)
        file_id = file_id['fileId']
        # print("FILE_ID:", file_id)

        return self.__get_cmd_output(file_id)

    def __get_cmd_output(self, file_id):
        while True:
            print(
                "PAUSING PROGRAM FOR 10 SECONDS TO WAIT FOR COMMANDS TO PUSH OUT OF PIPELINE")
            time.sleep(10)
            r = requests.get("%s/dna/intent/api/v1/file/%s" % (self.base_url,
                             file_id), headers=self.__dna_headers(), verify=False)
            try:
                if r.status_code == 200 or r.status_code == 202:
                    response = r.json()
                    print("RESPONSE LEN: ", len(response))
                    print("DEVICES LEN: ", len(self.__devices))
                    if len(response) < len(self.__devices):
                        continue
                    else:
                        break
                else:
                    print("EXITED WITH STATUS CODE: ", r.status_code)
                    break
            except:
                continue
        if r.status_code == 200 or r.status_code == 202:
            response = r.json()

            for device in response:
                device_details = self.__devices[device['deviceUuid']]
                temp_info = {}
                if 'show env temp' in device['commandResponses']['SUCCESS']:
                    for test in device['commandResponses']['SUCCESS']['show env temp'].split('\n'):

                        # note: show env temp output has yellow and red thresholds, this code will NOT record those thresholds correctly
                        temp_info[test.partition(":")[0].strip()] = test.partition(":")[
                            2].strip()
                    device_details.record_temps(temp_info)

            return True

    def __run_show_command_on_devices(self, device_ids):
        """
        Uses the Cisco Catalyst Center (DNAC) Command Runner API to run the following commands:
                *NOTE: Command Runner API allows up to 5 commands at once.*

                Command:
                        1. show env temp

                                'System Temperature', 'Inlet Temperature Value',
                             'Outlet Temperature Value',
                             'Hotspot Temperature Value'


        Retrives the following output from 'show env temp':
                1. device's system temperature
                2. device inlet temperature
                3. device outlet temperature
                4. device hotspot temperature value

        Return Value:
                dictionary

        """
        # print(device_ids)
        payload = {
            "name": "show temps",
            "commands": ["show env temp"],
            "deviceUuids": device_ids}

        r = requests.request("POST", '%s/dna/intent/api/v1/network-device-poller/cli/read-request' %
                             self.base_url, headers=self.__dna_headers(), data=json.dumps(payload), verify=False)
        response = r.json()

        if r.status_code == 200 or r.status_code == 202:
            yield self.__get_command_runner_task(response['response']['taskId'])

        else:
            yield "Error! HTTP %s Response: %s" % (r.status_code, response['response']['message'])

    def __get_devices_by_ip(self, csv_file):
        devices_info = self.__devices_by_csv(csv_file)
        devices_ip = devices_info['ip_address']

        all_devices_id = list()
        for ip in devices_ip:

            print(ip)
            r = requests.request("GET", '%s/dna/intent/api/v1/network-device?managementIpAddress=%s' %
                                 (self.base_url, ip), headers=self.__dna_headers(), verify=False)
            print(r.status_code)
            if r.status_code == 200:
                for device in r.json()['response']:
                    all_devices_id.append(device['id'])
                    self.__devices[device['id']] = Device(
                        device['id'], device['hostname'], device['managementIpAddress'], device['locationName'], device['softwareVersion'], device['serialNumber'])

        return all_devices_id

    def __collect_devices_data(self):
        for data in self.__run_show_command_on_devices(self.__get_devices_by_ip("ExportDevice.csv")):
            if (data == True):
                continue

    """

	PUBLIC CLASS METHODS

	"""

    def save_temp_to_one_csv(self):
        time_now = time.strftime('%H_%M_%d_%m_%Y', time.localtime())
        date_now = time.strftime('%d_%m_%Y', time.localtime())
        try:
            os.mkdir("output/"+date_now)
            # print("creating output folder")
        except:
            print("output folder exists")

        if os.path.exists('output/'+date_now+'/'+date_now+'.csv') == False:
            create_new_header = True
        else:
            create_new_header = False

        with open('output/'+date_now+'/'+date_now+'.csv', 'a') as output:
            writer = csv.writer(output, delimiter=',')

            if create_new_header:

                writer.writerow(['Time', 'Hostname', 'IP Address', 'Location',
                                 'System Temperature', 'Inlet Temperature Value',
                                 'Outlet Temperature Value',
                                 'Hotspot Temperature Value'])
                create_new_header = False

            for device_id, device in self.get_devices().items():
                build_row = list()

                try:

                    build_row.extend(
                        (time_now, device.get_hostname(), device.get_ip(), device.get_location()))

                    build_row.extend((device.get_temp()['Switch 1'],
                                      device.get_temp()['Inlet Temperature Value'].partition(" ")[
                        0].strip(),
                        device.get_temp()['Outlet Temperature Value'].partition(" ")[
                        0].strip(),
                        device.get_temp()['Hotspot Temperature Value'].partition(" ")[0].strip()))
                except:
                    print("reading row error")
                    build_row.extend(
                        (time_now, device.get_hostname(), device.get_ip(), device.get_location(), "", "", "", ""))

                writer.writerow(build_row)

    def save_temp_to_db(self):
        time_now = datetime.datetime.now()
        dbname = get_db_client()
        collection_name = get_or_generate_collection("switch_temp")
        for device_id, device in self.get_devices().items():

            metadata = {
                "hostname": device.get_hostname(),
                "device_ip": device.get_ip(),
                "device_location": device.get_location()
            }
            result = collection_name.insert_one({
                "metadata": metadata,
                "timestamp": time_now,
                "inlet_temperature_value": int(device.get_temp()['Inlet Temperature Value'].partition(" ")[0].strip()),
                "outlet_temperature_value": int(device.get_temp()['Outlet Temperature Value'].partition(" ")[0].strip()),
                "hotspot_temperature_value": int(device.get_temp()['Hotspot Temperature Value'].partition(" ")[0].strip())

            })
            if result.acknowledged:
                print("data saved")

    def get_devices(self):
        return self.__devices
