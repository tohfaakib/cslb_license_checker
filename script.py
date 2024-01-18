import re

import requests
from bs4 import BeautifulSoup
import json


def get_soup(lic_num):
    headers = {
        'Referer': 'https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/CheckLicense.aspx',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    params = {
        'LicNum': lic_num,
    }

    response = requests.get(
        'https://www2.cslb.ca.gov/OnlineServices/CheckLicenseII/LicenseDetail.aspx',
        params=params,
        headers=headers,
    )

    soup = BeautifulSoup(response.text, 'html.parser')

    return soup


def get_regex_text(pattern: str, text: str) -> str:
    text = str(text)
    try:
        pattern = re.compile(r'{}'.format(pattern))
        matches = re.search(pattern, text)
        return matches.group(1)
    except Exception as e:
        return ''


def get_license(lic_num):
    soup = get_soup(lic_num)

    license_data = {}

    status_block = soup.find('td', {'id': 'MainContent_Status'}).find('span', {"class": "text-success"})
    status_text = ""
    if status_block:
        status_text = status_block.text.strip()

    if "This license is current and active." in status_text:
        status = "Active"
    else:
        status = "Inactive"

    business_info_block = soup.find('td', {'id': 'MainContent_BusInfo'})

    if "Business Phone Number:" in str(business_info_block):
        business_phone = str(business_info_block).split("Business Phone Number:")[1].split("<br/>")[0].strip()
    else:
        business_phone = ""

    business_block = str(business_info_block).split("Business Phone Number:")[0].split('"MainContent_BusInfo">')[
        1].strip()
    business_block_split = business_block.split("<br/>")
    business_name = business_block_split[0].strip()

    license_data["status"] = status
    license_data["business_name"] = business_name

    j = 0
    for i, block in enumerate(business_block_split):
        if i != 0:
            address = block.replace("&amp;", "").strip().split()
            address = " ".join(address)
            if address:
                j += 1
                license_data[f"business_address_{j}"] = address

    entity = soup.find('td', {'id': 'MainContent_Entity'}).text.strip()
    issue_date = soup.find('td', {'id': 'MainContent_IssDt'}).text.strip()
    expire_date = soup.find('td', {'id': 'MainContent_ExpDt'}).text.strip()

    classification = soup.find('td', {'id': 'MainContent_ClassCellTable'}).text.strip()

    license_data["business_phone"] = business_phone
    license_data["entity"] = entity
    license_data["issue_date"] = issue_date
    license_data["expire_date"] = expire_date
    license_data["classification"] = classification

    bond_block = soup.find('td', {'id': 'MainContent_BondingCellTable'})
    bond_ps = bond_block.find_all('p')
    for p in bond_ps:
        if "Bond with" in p.text:
            bond_with = p.find("a").text.strip()
            license_data["bond_with"] = bond_with
        if "Bond Number:" in p.text:
            bond_number = p.text.strip().split("Bond Number: ")[1].strip().replace('"', '')
            license_data["bond_number"] = bond_number
        if "Bond Amount:" in p.text:
            bond_amount = p.text.strip().split("Bond Amount: ")[1].strip().replace('"', '')
            license_data["bond_amount"] = bond_amount
        if "Effective Date:" in p.text:
            bond_effective_date = p.text.strip().split("Effective Date: ")[1].strip().replace('"', '')
            license_data["bond_effective_date"] = bond_effective_date

    workers_compenstation_block = str(soup.find('td', {'id': 'MainContent_WCStatus'}))

    workers_compenstation_insurance_with = get_regex_text("the\s<a\s[^>]+>([^<]+)", workers_compenstation_block).strip()
    workers_compenstation_policy_number = get_regex_text("Policy\sNumber:[^>]+>([^<]+)",
                                                         workers_compenstation_block).strip()
    workers_compenstation_effective_date = get_regex_text("Effective\sDate:[^>]+>([^<]+)",
                                                          workers_compenstation_block).strip()
    workers_compenstation_expire_date = get_regex_text("Expire\sDate:[^>]+>([^<]+)",
                                                       workers_compenstation_block).strip()

    license_data["workers_compenstation_insurance_with"] = workers_compenstation_insurance_with
    license_data["workers_compenstation_policy_number"] = workers_compenstation_policy_number
    license_data["workers_compenstation_effective_date"] = workers_compenstation_effective_date
    license_data["workers_compenstation_expire_date"] = workers_compenstation_expire_date

    return json.dumps(license_data, indent=4)


if __name__ == '__main__':
    licence_data = get_license('988872')
    # licence_data = get_license('988875')
    # licence_data = get_license('978375')
    print(licence_data)
