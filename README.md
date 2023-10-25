# gve devnet dnac command runner temperature collection
This is a prototype that collects temperature information from the devices managed by DNA Center and compiles the output into a log and summary


## Contacts
* Kevin Chen (kevchen3@cisco.com)

## Solution Components
* Catalyst Center (formerly DNA Center)



## Prerequisites
**DNA Center Credentials**: In order to use the DNA Center APIs, you need to make note of the IP address, username, and password of your instance of DNA Center. Note these values to add to the credentials file during the installation phase.

## Installation/Configuration
1. Clone this repository with `git clone [repository name]`
2. add the credentials to a .env file in the following format 

```
USERNAME=[insert your username here]
PASSWORD=[insert your password here]
URL=[insert IP address of Catalyst Center or DNAC here]
```
3. Set up a Python virtual environment. Make sure Python 3 is installed in your environment, and if not, you may download Python [here](https://www.python.org/downloads/). Once Python 3 is installed in your environment, you can activate the virtual environment with the instructions found [here](https://docs.python.org/3/tutorial/venv.html).
4. Install the requirements with `pip3 install -r requirements.txt`
5. Select devices for which you wish to monitor the temperature, via the DNA Center Inventory page. 

![/IMAGES/Inventory.png](/IMAGES/Inventory.png)

Once you have selected the devices, click on the Export button. This will save a csv file called "ExportDevice.csv" that contains the information for the devices you have selected. Alternatively, you can create the file manually by creating a file of the same name, then putting in 1 column with the header "ip_address" proceeded by the list of IP addresses of the devices you wish to monitor. 

ip_address  | 
------------- | 
192.168.1.1  | 
10.10.10.10  | 


6. Save the "ExportDevice.csv" file into the root folder of this repository. 


## Usage
There are two functionalities included in this repository, 
1. Collect temperature information

To run the code, use the command:
```
$ python3 complete/main.py
```
This will generate a csv file in a folder named with the current date in the output/ folder

![/IMAGES/output1.png](/IMAGES/output1.png)


2. Run a summary of a particular day's information
```
$ python3 complete/daily_summary.py
```

In the terminal, enter the relative path of the csv file generated from running main.py, something like this
```
Enter temperature csv: output/19_10_2023/19_10_2023.csv
```

This will generate the summary reports in the same folder, see example:

![/IMAGES/output2.png](/IMAGES/output2.png)

# Screenshots

![/IMAGES/0image.png](/IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.