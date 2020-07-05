import configparser
import json
import os
from datetime import date
from datetime import time
from typing import Dict
from typing import List
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium.webdriver.remote.webelement import WebElement

from twomartens.allrisscraper import agenda
from twomartens.allrisscraper import config as config_module
from twomartens.allrisscraper import custom_json
from twomartens.allrisscraper import definitions
from twomartens.allrisscraper import meeting
from twomartens.allrisscraper.definitions import MONTHS
from twomartens.allrisscraper.meeting import Meeting


def main():
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
    driver.get(f"{base_url}/si010_e.asp?MM=6&YY=2020")
    meetings = get_meetings(driver)
    process_agendas(driver, meetings)
    motions = get_motions(driver, meetings)
    driver.close()
    
    os.makedirs(json_path, exist_ok=True)
    with open(json_path + "meetings.json", "w") as file:
        json.dump(meetings, file,
                  cls=custom_json.EnhancedJSONEncoder)
    with open(json_path + "motions.json", "w") as file:
        json.dump(motions, file,
                  cls=custom_json.EnhancedJSONEncoder)


def get_meetings(driver: webdriver):
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
    
    return meeting.Meeting(name=name, date=date_obj,
                           time=start_time_obj, end_time=end_time_obj,
                           link=agenda_link, location=location,
                           agenda=None, address=None)


def process_agendas(driver: webdriver.Firefox, meetings: List[meeting.Meeting]) -> None:
    for meeting_obj in meetings:
        process_agenda(driver, meeting_obj)


def process_agenda(driver: webdriver.Firefox, meeting_obj: meeting.Meeting) -> None:
    driver.get(meeting_obj.link)
    td = driver.find_element_by_xpath("//table[@class='risdeco']//tr[2]//td[2]")
    tables = td.find_elements_by_xpath("table")
    meta_table = tables[0]
    agenda_table = tables[1]
    meta_trs = meta_table.find_elements_by_xpath("./tbody//tr//td[1]//tr")
    meeting_obj.address = str(meta_trs[5].find_element_by_xpath("td[2]").text)
    
    agenda_item_trs = agenda_table.find_elements(
            By.XPATH,
            ".//tr[not(descendant::th) and not(descendant::td[contains(@colspan, '7')])]")
    agenda_item_trs = agenda_item_trs[:-1]
    
    agenda_items = list()
    for index, agenda_item_tr in enumerate(agenda_item_trs):
        agenda_items.append(process_agenda_item(index, agenda_item_tr))
    meeting_obj.agenda = agenda.Agenda(agenda_items)


def process_agenda_item(index: int, item: WebElement) -> agenda.AgendaItem:
    tds = item.find_elements_by_xpath("td")
    item_link = str(tds[0].find_element_by_tag_name("a").get_property("href")).strip()
    number = str(tds[0].find_element_by_tag_name("a").text).strip()
    name = str(tds[3].text).strip()
    public = "Ö" in number
    motion_td = str(tds[5].text).strip()
    has_motion = len(motion_td) != 0
    motion_link = None
    motion_reference = None
    if has_motion:
        motion_link = str(tds[5].find_element_by_tag_name("a").get_property("href")).strip()
        motion_reference = str(tds[5].find_element_by_tag_name("a").text).strip()
    
    return agenda.AgendaItem(number=number, order=index, name=name,
                             public=public, link=item_link,
                             motion_link=motion_link, motion_reference=motion_reference)


def get_motions(driver: webdriver.Firefox, meetings: List[meeting.Meeting]) -> Dict[str, agenda.Motion]:
    motions: Dict[str, agenda.Motion] = dict()
    for _meeting in meetings:
        agenda_items = _meeting.agenda.agenda_items
        for agenda_item in agenda_items:
            if agenda_item.motion_link is None:
                continue
            motions[agenda_item.motion_reference] = get_motion(driver, agenda_item.motion_link,
                                                               agenda_item.motion_reference)
    return motions


def get_motion(driver: webdriver.Firefox, link: str, reference: str) -> agenda.Motion:
    driver.get(link)
    meta_table = driver.find_element_by_xpath("//table[@class='risdeco']//tr[2]//td[2]//table//tr//td[1]//table")
    meta_trs = meta_table.find_elements_by_xpath("./tbody//tr")
    name = str(meta_trs[0].find_element_by_xpath("td[2]").text).strip()
    motion_type = str(meta_trs[1].find_element_by_xpath("td[4]").text).strip()
    under_direction_of = str(meta_trs[2].find_element_by_xpath("td[2]").text).strip()
    consultation_trs = meta_trs[4].find_elements_by_xpath(".//table//tr")[1:]
    current_organization: Optional[str] = None
    current_role: Optional[str] = None
    consultations = []
    for consultation_tr in consultation_trs:
        tds = consultation_tr.find_elements_by_xpath("td")
        is_organization_header = tds[1].get_attribute("class") == "text1"
        if is_organization_header:
            current_organization = str(tds[1].text).strip()
            current_role = str(tds[2].text).strip()
        else:
            authoritative = str(tds[0].get_property("title")).strip() == "Erledigt"
            meeting_link = str(tds[3].find_element_by_xpath("a").get_property("href")).strip()
            consultations.append(agenda.Consultation(
                    authoritative, meeting_link,
                    [current_organization], current_role))
    
    text_divs = driver.find_elements_by_xpath("//table[@class='risdeco']//tr[2]//td[2]//div")
    context_div = text_divs[0]
    context_ps = context_div.find_elements_by_xpath("p")[1:-1]
    context = ""
    for p in context_ps:
        if len(context) > 0:
            context += "\n"
        context += str(p.text).strip()
    
    petition_div = text_divs[1]
    petition_ps = petition_div.find_elements_by_xpath("p")[1:-1]
    petition = ""
    for p in petition_ps:
        if len(petition) > 0:
            petition += "\n"
        petition += str(p.text).strip()
    petition.rstrip()
    
    return agenda.Motion(name=name, reference=reference,
                         type=motion_type, under_direction_of=under_direction_of,
                         context=context, petition=petition, consultations=consultations)


if __name__ == "__main__":
    main()
