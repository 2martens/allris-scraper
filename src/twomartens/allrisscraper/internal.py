# -*- coding: utf-8 -*-

#   Copyright 2020 Jim Martens
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import configparser
import os
from datetime import date
from datetime import time
from typing import List
from typing import Tuple
from urllib import request

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement

from twomartens.allrisscraper import config as config_module
from twomartens.allrisscraper import definitions
from twomartens.allrisscraper import meeting
from twomartens.allrisscraper.definitions import ALLRIS_LOGIN


def main(_) -> None:
    config_file = f"{os.getcwd()}/tm-allris-scraper-config.ini"
    if not config_module.initialize_config(config_file):
        return
        
    config = configparser.ConfigParser()
    config.read(config_file)
    district = config["Default"]["district"]
    username = config["Default"]["username"]
    password = config["Default"]["password"]
    pdf_location = config["Default"]["pdflocation"]
    firefox_binary = config["Default"]["firefoxBinary"]
    geckodriver = config["Default"]["geckodriver"]
    base_url = definitions.BASE_LINKS[district]
    
    options = Options()
    options.headless = True
    binary = FirefoxBinary(firefox_binary)
    driver = webdriver.Firefox(firefox_binary=binary, options=options, executable_path=geckodriver)
    driver.set_window_size(1920, 1080)
    driver.delete_all_cookies()
    driver.implicitly_wait(5)
    driver.get(ALLRIS_LOGIN)
    login(driver, username=username, password=password)
    driver.get("https://serviceportal.hamburg.de/HamburgGateway/Service/StartService/ALLMAnd")
    driver.get(f"{base_url}/si012.asp")
    meetings = get_meetings(driver)
    download_documents(driver, meetings, pdf_location, base_url, district)
    driver.close()
    

def login(driver: webdriver.Firefox, username: str, password: str) -> None:
    login_field = driver.find_element_by_id("Username")
    login_field.send_keys(username)
    password_field = driver.find_element_by_id("Password")
    password_field.send_keys(password)
    button = driver.find_element_by_class_name("btn-primary")
    button.click()
    

def get_meetings(driver: webdriver.Firefox) -> List[meeting.Meeting]:
    elements = driver.find_elements_by_class_name("zl12")
    elements.extend(driver.find_elements_by_class_name("zl11"))
    meetings = list()
    for element in elements:
        tds = element.find_elements_by_tag_name("td")
        date_obj = get_day(tds[0].text)
        time_obj = time.fromisoformat(str(tds[1].text).rstrip())
        agenda_link = tds[4].find_element_by_tag_name("a").get_property("href")
        name = tds[4].find_element_by_tag_name("a").text
        location = tds[5].text
        meetings.append(meeting.Meeting(name=name, date=date_obj,
                                        time=time_obj, end_time=None,
                                        link=agenda_link, location=location,
                                        agenda=None, address=None))
    
    return meetings


def download_documents(driver: webdriver.Firefox, meetings: List[meeting.Meeting],
                       pdf_location: str, base_url: str, district: str) -> None:
    base_link = f"{base_url}/do027.asp"
    for _meeting in meetings:
        driver.get(_meeting.link)
        td = driver.find_element_by_xpath("//table[@class='tk1']//td[@class='me1']")
        form_elements = td.find_elements_by_tag_name("form")
        agenda_link, total_link, invitation_link = get_links(form_elements, base_link)
        if len(agenda_link) > 0:
            driver.get(agenda_link)
            save_pdf(driver.current_url, f"{get_formatted_filename(pdf_location, _meeting, district)}/Tagesordnung.pdf")
        if len(total_link) > 0:
            driver.get(total_link)
            save_pdf(driver.current_url, f"{get_formatted_filename(pdf_location, _meeting, district)}/Mappe.pdf")
        if len(invitation_link) > 0:
            driver.get(invitation_link)
            save_pdf(driver.current_url, f"{get_formatted_filename(pdf_location, _meeting, district)}/Einladung.pdf")
        save_file(_meeting.location, f"{get_formatted_filename(pdf_location, _meeting, district)}/ort.txt")


def get_links(form_elements: List[WebElement], base_link: str) -> Tuple[str, str, str]:
    agenda_name = "Tagesordnung"
    updated_agenda_name = "Aktuelle TO"
    total_name = "Alle Dokumente zur Sitzung im Paket"
    total_short_name = "Mappe"
    invitation_name = "Einladung"
    
    links = {}
    for element in form_elements:
        name = element.find_element_by_class_name("il2_p").get_property("value")
        link = f"{base_link}?DOLFDNR={element.find_element_by_name('DOLFDNR').get_property('value')}&options=64"
        if name == agenda_name:
            links[agenda_name] = link
        if name == updated_agenda_name:
            links[agenda_name] = link
        if name == total_name:
            links[total_short_name] = link
        if name == invitation_name:
            links[invitation_name] = link
    
    if agenda_name not in links:
        links[agenda_name] = ""
    if invitation_name not in links:
        links[invitation_name] = ""
    if total_short_name not in links:
        links[total_short_name] = ""
    
    return links[agenda_name], links[total_short_name], links[invitation_name]


def get_formatted_filename(pdf_location: str, meeting_obj: meeting.Meeting, district: str) -> str:
    return f"{pdf_location}{meeting_obj.date.isoformat()}_{get_abbreviated_committee_name(meeting_obj.name, district)}"


def save_pdf(url: str, dest: str) -> None:
    file_data: request = request.urlopen(url)
    data_to_write = file_data.read()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as file:
        file.write(data_to_write)


def save_file(content: str, dest: str) -> None:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as file:
        file.write(content)


def get_day(date_str: str) -> date:
    date_elements = date_str[date_str.find(",") + 1:].split(".")
    return date(int(date_elements[-1]), int(date_elements[-2]), int(date_elements[-3]))


def get_abbreviated_committee_name(name: str, district: str) -> str:
    start_committee = "Sitzung des Ausschusses"
    start_regional_committee = "Sitzung des Regionalausschusses"
    start_plenary = "Sitzung der Bezirksversammlung"
    start_youth_help_committee = "Sitzung des Jugendhilfeausschusses"
    start_other_committee = "Sitzung des"
    end_other_committee = "ausschusses"
    abbreviated_name = ""
    if name.startswith(start_plenary):
        abbreviated_name = "BV"
    elif name.startswith(start_committee):
        second_part = name[len(start_committee):]
        second_split = second_part.split(sep=",")
        abbreviated_name = get_abbreviation(second_split)
        if len(abbreviated_name) == 1:
            abbreviated_name = f"A{abbreviated_name}"
    elif name.startswith(start_regional_committee):
        second_part = name[len(start_regional_committee):]
        second_split = second_part.split(sep="/")
        abbreviated_name = f"Ra{get_abbreviation(second_split)}"
    elif name.startswith(start_youth_help_committee):
        abbreviated_name = "JHA"
    elif name.startswith(start_other_committee) and name.endswith(end_other_committee):
        core_name = name[len(start_other_committee):-len(end_other_committee)]
        abbreviated_name = core_name
    
    if abbreviated_name in definitions.ABBREVIATIONS[district]:
        abbreviated_name = definitions.ABBREVIATIONS[district][abbreviated_name]
    
    return abbreviated_name


def get_abbreviation(name):
    abbreviated_name = ""
    for part in name:
        part = part.lstrip()
        if "und" in part:
            part_split = part.split("und")
            first_part = part_split[0].lstrip()
            second_part = part_split[1].lstrip()
            abbreviated_name = f"{abbreviated_name}{first_part[:1].capitalize()}{second_part[:1].capitalize()}"
        else:
            abbreviated_name = f"{abbreviated_name}{part[:1].capitalize()}"
    return abbreviated_name
