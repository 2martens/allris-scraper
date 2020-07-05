import argparse
import configparser
import json
import os

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options

from twomartens.allrisscraper import agenda
from twomartens.allrisscraper import config as config_module
from twomartens.allrisscraper import custom_json
from twomartens.allrisscraper import definitions
from twomartens.allrisscraper import meeting
from twomartens.allrisscraper import organization
from twomartens.allrisscraper import person


def main(args: argparse.Namespace):
    config_file = f"{os.getcwd()}/tm-allris-scraper-config.ini"
    if not config_module.initialize_config(config_file):
        return
    
    config = configparser.ConfigParser()
    config.read(config_file)
    district = config["Default"]["district"]
    json_path = config["Default"]["jsonLocation"]
    firefox_binary = config["Default"]["firefoxBinary"]
    base_url = definitions.PUBLIC_BASE_LINKS[district]
    
    options = Options()
    options.headless = False
    binary = FirefoxBinary(firefox_binary)
    driver = webdriver.Firefox(firefox_binary=binary, options=options)
    driver.implicitly_wait(2)
    os.makedirs(json_path, exist_ok=True)
    if args.include_meetings:
        meetings = meeting.get_meetings(driver, base_url)
        agenda.process_agendas(driver, meetings)
        motions = agenda.get_motions(driver, meetings)
        with open(json_path + "meetings.json", "w") as file:
            json.dump(meetings, file,
                      cls=custom_json.EnhancedJSONEncoder)
        with open(json_path + "motions.json", "w") as file:
            json.dump(motions, file,
                      cls=custom_json.EnhancedJSONEncoder)
    
    if args.include_organizations:
        organizations = organization.get_organizations(driver, base_url)
        persons = person.get_persons(driver, organizations)
        with open(json_path + "organizations.json", "w") as file:
            json.dump(organizations, file,
                      cls=custom_json.EnhancedJSONEncoder)
        with open(json_path + "persons.json", "w") as file:
            json.dump(persons, file,
                      cls=custom_json.EnhancedJSONEncoder)
    
    driver.close()
