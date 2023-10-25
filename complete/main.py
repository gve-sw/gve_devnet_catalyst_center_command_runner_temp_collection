import DNACenter
from prettyprinter import pprint
import getpass
from decouple import config
import schedule
import time


def collect_info():
    session = DNACenter.DNACenter(
        username=username, password=password, base_url=url)
    # session.save_temp_to_db()
    session.save_temp_to_one_csv()


if __name__ == "__main__":

    # uncomment the 3 lines below to enable interactive credential entry

    # username = input("Enter username: ")
    # password = getpass.getpass("Enter password: ")
    # url = input("Enter DNAC URL: ")

    # credentials to Catalyst Center (DNAC) is stored in .env file
    # format the .env file to below
    # USERNAME=[your username here]
    # PASSWORD=[your password here]
    # URL=[your Catalyst Center (DNAC) URL here e.g. https://10.10.141.35]

    username = config('USERNAME')
    password = config("PASSWORD")
    url = config("URL")

    # data collection paramters
    # time in seconds (3600s in 1 hour, 86400s in 1 day)
    # if collection period is too short, command runner might not be finished in time
    collection_period = 60

    schedule.every(collection_period).seconds.do(collect_info)

    while True:
        schedule.run_pending()
        time.sleep(1)
