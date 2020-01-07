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
from urllib import request
from datetime import date
from datetime import time
import os

from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox import webdriver
from selenium.webdriver.firefox.options import Options

from twomartens.allrisscraper import meeting


ALLRIS_LOGIN: str = "https://2martens.de/allris-eimsbüttel"
ALLRIS_OPEN: str = "https://2martens.de/bezirk-eimsbüttel"
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3112.50 Safari/537.36'


def main() -> None:
    config = configparser.ConfigParser()
    config.read("config.ini")
    username = config["Default"]["username"]
    password = config["Default"]["password"]
    pdf_location = config["Default"]["pdflocation"]
    
    options = Options()
    options.headless = False
    options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.WebDriver(options=options)
    driver.implicitly_wait(2)
    driver.get(ALLRIS_LOGIN)
    login(driver, username=username, password=password)
    driver.get("https://gateway.hamburg.de/HamburgGateway/Service/StartService/113")
    driver.get("https://sitzungsdienst-eimsbuettel.hamburg.de/ri/si012.asp")
    meetings = get_meetings(driver)
    download_documents(driver, meetings, pdf_location)
    

def login(driver: webdriver.WebDriver, username: str, password: str) -> None:
    login_field = driver.find_element_by_id("LoginName")
    login_field.send_keys(username)
    password_field = driver.find_element_by_id("Password")
    password_field.send_keys(password)
    button = driver.find_element_by_id("buttonLogin")
    button.click()
    

def get_meetings(driver: webdriver.WebDriver) -> List[meeting.Meeting]:
    elements = driver.find_elements_by_class_name("zl12")
    meetings = list()
    for element in elements:
        tds = element.find_elements_by_tag_name("td")
        date_obj = get_day(tds[0].text)
        time_obj = time.fromisoformat(str(tds[1].text).rstrip())
        agenda_link = tds[4].find_element_by_tag_name("a").get_property("href")
        name = tds[4].find_element_by_tag_name("a").text
        location = tds[5].text
        meetings.append(meeting.Meeting(name, date_obj, time_obj, agenda_link, location))
    
    return meetings
    

def download_documents(driver: webdriver.WebDriver, meetings: List[meeting.Meeting], pdf_location: str) -> None:
    base_link = "https://sitzungsdienst-eimsbuettel.hamburg.de/ri/do027.asp"
    for meeting in meetings:
        driver.get(meeting.link)
        td = driver.find_element(By.XPATH, "//table[@class='tk1']//td[@class='me1']")
        form_elements = td.find_elements_by_tag_name("form")
        agenda_item = form_elements[0]
        agenda_link = f"{base_link}?DOLFDNR={agenda_item.find_element_by_name('DOLFDNR').get_property('value')}&options=64"
        total_item = form_elements[1]
        total_link = f"{base_link}?DOLFDNR={total_item.find_element_by_name('DOLFDNR').get_property('value')}&options=64"
        invitation_item = form_elements[2]
        invitation_link = f"{base_link}?DOLFDNR={invitation_item.find_element_by_name('DOLFDNR').get_property('value')}&options=64"
        driver.get(agenda_link)
        save_pdf(driver.current_url, f"{pdf_location}{meeting.date.isoformat()}-{meeting.name}-Tagesordnung.pdf")
        driver.get(total_link)
        save_pdf(driver.current_url, f"{pdf_location}{meeting.date.isoformat()}-{meeting.name}-Mappe.pdf")
        driver.get(invitation_link)
        save_pdf(driver.current_url, f"{pdf_location}{meeting.date.isoformat()}-{meeting.name}-Einladung.pdf")


def save_pdf(url: str, dest: str) -> None:
    file_data: request = request.urlopen(url)
    data_to_write = file_data.read()
    with open(dest, "wb") as file:
        file.write(data_to_write)


def get_day(date_str: str) -> date:
    date_elements = date_str[date_str.find(",") + 1:].split(".")
    return date(int(date_elements[-1]), int(date_elements[-2]), int(date_elements[-3]))
    

if __name__ == "__main__":
    main()