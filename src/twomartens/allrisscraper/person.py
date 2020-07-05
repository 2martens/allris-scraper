from dataclasses import dataclass
from typing import Dict
from typing import List

from selenium import webdriver

from twomartens.allrisscraper.organization import Organization


@dataclass
class Person:
    name: str
    form_of_address: str
    phone: List[str]
    email: List[str]


def get_persons(driver: webdriver.Firefox, organizations: List[Organization]) -> List[Person]:
    persons: Dict[str, Person] = {}
    for org in organizations:
        memberships = org.membership
        for membership in memberships:
            person_link = membership.person
            if person_link in persons:
                continue
            persons[person_link] = get_person(driver=driver, link=person_link)
        
    return list(persons.values())


def get_person(driver: webdriver.Firefox, link: str) -> Person:
    driver.get(link)
    meta_trs = driver.find_elements_by_xpath("//div[@id='rismain']//table//tr//td//table//tr")
    form_of_address = str(meta_trs[0].find_element_by_xpath("td[3]").text).strip()
    name = str(meta_trs[1].find_element_by_xpath("td").text).strip()
    phone_tds = meta_trs[5].find_elements_by_xpath("td")
    phone = ""
    if len(phone_tds) > 1:
        phone = str(meta_trs[5].find_element_by_xpath("td[2]//span").text).strip()
    email_tds = meta_trs[6].find_elements_by_xpath("td")
    email = ""
    if len(email_tds) > 1:
        email = str(meta_trs[6].find_element_by_xpath("td[2]//a").text).strip()
    
    return Person(name=name, form_of_address=form_of_address, phone=[phone], email=[email])
