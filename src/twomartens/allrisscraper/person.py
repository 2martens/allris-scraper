from typing import Dict
from typing import List

from selenium import webdriver

from twomartens.allrisscraper import data_types as types


def get_persons(driver: webdriver.Firefox, organizations: List[types.Organization]) -> List[types.Person]:
    persons: Dict[str, types.Person] = {}
    for org in organizations:
        memberships = org.membership
        for membership in memberships:
            person_link = membership.person
            if person_link in persons:
                continue
            if person_link == "":
                continue
            persons[person_link] = get_person(driver=driver, link=person_link)
    
    return list(persons.values())


def get_person(driver: webdriver.Firefox, link: str) -> types.Person:
    driver.get(link)
    meta_trs = driver.find_elements_by_xpath("//div[@id='rismain']//table[1]//tr//td//table//tr")
    form_of_address = str(meta_trs[0].find_element_by_xpath("td[3]").text).strip()
    name = str(meta_trs[1].find_element_by_xpath("td").text).strip()
    phone = []
    email = []
    additional_trs = meta_trs[2:]
    for tr in additional_trs:
        tds = tr.find_elements_by_tag_name("td")
        if len(tds) == 1 and str(tds[0].text).strip() == "":
            continue
        images = tr.find_elements_by_xpath("td[1]//img")
        if len(images) == 0:
            continue
        alt = images[0].get_property("alt")
        if is_email_row(alt):
            email.append(str(tr.find_element_by_xpath("td[2]//a").text).strip())
        if is_phone_row(alt):
            phone.append(str(tr.find_element_by_xpath("td[2]//span").text).strip())
    
    return types.Person(name=name, form_of_address=form_of_address, phone=phone, email=email)


def is_email_row(alt: str) -> bool:
    return "eMail" in alt


def is_phone_row(alt: str) -> bool:
    return "Tel" in alt
