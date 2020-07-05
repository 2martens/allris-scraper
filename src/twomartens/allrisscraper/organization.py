from typing import List

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

from twomartens.allrisscraper import data_types as types


def get_organizations(driver: webdriver.Firefox, base_url: str) -> List[types.Organization]:
    organizations = [get_organization(driver=driver,
                                      link=f"{base_url}/pa021.asp",
                                      classification="Bezirksversammlung",
                                      organization_type="Gremium")]
    organizations.extend(get_committees(driver=driver,
                                        link=f"{base_url}/au010.asp"))
    organizations.extend(get_factions(driver=driver,
                                      link=f"{base_url}/fr010.asp"))
    
    return organizations


def get_committees(driver: webdriver.Firefox, link: str) -> List[types.Organization]:
    driver.get(link)
    committee_trs = driver.find_elements_by_xpath("//div[@id='rismain']//table//tr[not(contains(@class, 'zw1'))]")[2:-1]
    organizations = []
    links = []
    for committee_tr in committee_trs:
        tds = committee_tr.find_elements_by_xpath("td")
        next_session = str(tds[6].text).strip()
        if next_session == "":
            continue
        links.append(str(tds[1].find_element_by_xpath("a").get_property("href")).strip())
    for link in links:
        organizations.append(get_organization(driver=driver, link=link,
                                              classification="Ausschuss", organization_type="Gremium"))
    
    return organizations


def get_factions(driver: webdriver.Firefox, link: str) -> List[types.Organization]:
    driver.get(link)
    driver.get(link)
    faction_trs = driver.find_elements_by_xpath("//div[@id='rismain']//table//tr")[2:-1]
    organizations = []
    links = []
    for faction_tr in faction_trs:
        tds = faction_tr.find_elements_by_xpath("td")
        is_outdated = "(bis" in str(tds[2].text).strip()
        if is_outdated:
            continue
        links.append(str(tds[1].find_element_by_xpath("a").get_property("href")).strip())
    for link in links:
        organizations.append(get_organization(driver=driver, link=link,
                                              classification="Fraktion", organization_type="Fraktion"))
    
    return organizations


def get_organization(driver: webdriver.Firefox, link: str, classification: str,
                     organization_type: str) -> types.Organization:
    driver.get(link)
    name = str(driver.find_element_by_xpath("//div[@id='risname']").text).strip()
    memberships = []
    member_trs = driver.find_elements_by_xpath("//div[@id='rismain']//table[2]//tr")[2:-1]
    for member_tr in member_trs:
        memberships.append(get_membership(member_tr, name))
    
    return types.Organization(name=name, classification=classification,
                              organization_type=organization_type, membership=memberships)


def get_membership(member_tr: WebElement, organization: str) -> types.Membership:
    tds = member_tr.find_elements_by_xpath("td")
    if len(tds[2].find_elements_by_xpath("a")) == 0:
        person_link = ""
    else:
        person_link = str(tds[2].find_element_by_xpath("a").get_property("href")).strip()
    role = str(tds[3].text).strip()
    on_behalf_of = str(tds[4].text).strip()
    
    return types.Membership(person=person_link, organization=organization, role=role, on_behalf_of=on_behalf_of)
