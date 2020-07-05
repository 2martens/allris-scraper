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
import datetime
from dataclasses import dataclass
from datetime import date
from datetime import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webelement import FirefoxWebElement

from twomartens.allrisscraper import data_types
from twomartens.allrisscraper.definitions import MONTHS


@dataclass
class Meeting:
    name: str
    date: datetime.date
    time: datetime.time
    end_time: Optional[datetime.time]
    link: str
    location: str
    address: Optional[str]
    agenda: Optional[data_types.Agenda]


def get_meetings(driver: webdriver, base_url: str):
    driver.get(f"{base_url}/si010_e.asp?MM=6&YY=2020")
    year_month: str = str(driver.find_element_by_xpath("//table[@class='risdeco']//table[1]//tr").text).strip()
    month, year = year_month.split(" ")
    calendar_lines = driver.find_elements(
            By.XPATH,
            "//table[@class='tl1']//tr[not(descendant::td[contains(@colspan, '8')])]"
    )
    meetings = list()
    calendar_lines.remove(calendar_lines[0])
    for line in calendar_lines:
        last_date = None
        if len(meetings):
            last_meeting = meetings[-1]
            last_date = last_meeting.date
        meetings.append(get_meeting(line, month, year, last_date))
    return meetings


def get_meeting(line: FirefoxWebElement, month: str, year: str, last_date: date) -> Meeting:
    tds = line.find_elements_by_xpath("td")
    date_str: str = str(tds[1].text).strip()
    if date_str:
        date_obj = date(int(year), MONTHS.get(month), int(date_str))
    else:
        date_obj = last_date
    start_time, end_time = str(tds[2].text).strip().split(" - ")
    start_time_obj = time.fromisoformat(start_time)
    end_time_obj = time.fromisoformat(end_time)
    name = str(tds[5].find_element_by_tag_name("a").text)
    agenda_link = str(tds[5].find_element_by_tag_name("a").get_property("href"))
    location = str(tds[8].text)
    
    return Meeting(name=name, date=date_obj,
                   time=start_time_obj, end_time=end_time_obj,
                   link=agenda_link, location=location,
                   agenda=None, address=None)
