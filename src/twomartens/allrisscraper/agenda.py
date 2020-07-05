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

from typing import Dict
from typing import List
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from twomartens.allrisscraper import meeting
from twomartens.allrisscraper import data_types as types

XPATH_2ND_TD = "td[2]"


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
    meeting_obj.address = str(meta_trs[5].find_element_by_xpath(XPATH_2ND_TD).text)
    
    agenda_item_trs = agenda_table.find_elements(
            By.XPATH,
            ".//tr[not(descendant::th) and not(descendant::td[contains(@colspan, '7')])]")
    agenda_item_trs = agenda_item_trs[:-1]
    
    agenda_items = list()
    for index, agenda_item_tr in enumerate(agenda_item_trs):
        agenda_items.append(process_agenda_item(index, agenda_item_tr))
    meeting_obj.agenda = types.Agenda(agenda_items)


def process_agenda_item(index: int, item: WebElement) -> types.AgendaItem:
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
    
    return types.AgendaItem(number=number, order=index, name=name,
                            public=public, link=item_link,
                            motion_link=motion_link, motion_reference=motion_reference,
                            resolution_text="")


def get_motions(driver: webdriver.Firefox, meetings: List[meeting.Meeting]) -> Dict[str, types.Motion]:
    motions: Dict[str, types.Motion] = dict()
    for _meeting in meetings:
        agenda_items = _meeting.agenda.agenda_items
        for agenda_item in agenda_items:
            if agenda_item.motion_link is None:
                continue
            motions[agenda_item.motion_reference] = get_motion(driver=driver, agenda_item_link=agenda_item.link,
                                                               link=agenda_item.motion_link,
                                                               reference=agenda_item.motion_reference)
    return motions


def get_motion(driver: webdriver.Firefox, agenda_item_link: str, link: str, reference: str) -> types.Motion:
    driver.get(link)
    meta_table = driver.find_element_by_xpath("//table[@class='risdeco']//tr[2]//td[2]//table//tr//td[1]//table")
    meta_trs = meta_table.find_elements_by_xpath("./tbody//tr")
    name = str(meta_trs[0].find_element_by_xpath(XPATH_2ND_TD).text).strip()
    motion_type = str(meta_trs[1].find_element_by_xpath("td[4]").text).strip()
    under_direction_of = str(meta_trs[2].find_element_by_xpath(XPATH_2ND_TD).text).strip()
    consultation_trs = meta_trs[4].find_elements_by_xpath(".//table//tr")[1:]
    current_organization: Optional[str] = None
    current_role: Optional[str] = None
    consultations = []
    for consultation_tr in consultation_trs:
        tds = consultation_tr.find_elements_by_xpath("td")
        is_organization_header = tds[1].get_attribute("class") == "text1"
        if is_organization_header:
            current_organization = str(tds[1].text).strip()
            if len(tds) >= 3:
                current_role = str(tds[2].text).strip()
            else:
                current_role = None
        else:
            authoritative = str(tds[0].get_property("title")).strip() == "Erledigt" \
                            and str(tds[4].text).strip() in ["beschlossen", "zur Kenntnis genommen", "abgelehnt"]
            link_exists = len(tds[3].find_elements_by_xpath("a")) > 0
            if not link_exists:
                continue
            meeting_link = str(tds[3].find_element_by_xpath("a").get_property("href")).strip()
            consultations.append(types.Consultation(
                    authoritative=authoritative, meeting=meeting_link,
                    organization=[current_organization], role=current_role,
                    agenda_item=agenda_item_link, result=str(tds[2].text).strip()
            ))
    
    file_table = driver.find_element_by_xpath("//table[@class='risdeco']//tr[2]//td[2]//table//tr//td[3]//table")
    motion_file_form = file_table.find_element_by_xpath(".//tr[2]//td//form[1]")
    hidden_inputs = motion_file_form.find_elements_by_xpath(".//input[contains(@type, 'hidden')]")
    file_link = ""
    for hidden_input in hidden_inputs:
        if file_link == "":
            file_link += "?"
        else:
            file_link += "&"
        file_link += f"{hidden_input.get_property('name')}={hidden_input.get_property('value')}"
    file_link = f"{motion_file_form.get_property('action')}{file_link}"
    
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
    
    return types.Motion(name=name, reference=reference,
                        type=motion_type, under_direction_of=under_direction_of,
                        context=context, petition=petition, consultations=consultations,
                        file=file_link)
