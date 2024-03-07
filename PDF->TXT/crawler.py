import requests
from bs4 import BeautifulSoup
import time
import csv

def crawl(query_list, csvName):
    # stores employees for csv
    employees = []
    
    # get requests website
    for query in query_list:
        first = query[0]
        last = query[1]
        print("Crawling " + first + " " + last)
        response = requests.get(f"https://www.uoregon.edu/findpeople/person/subsetsearch/{first}%20{last}/200")

        # parses information
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Initialize the employee dictionary for each query
        employee = {}

        if not soup.find(string="No matches found."): #no results
            if not soup.find('div', class_='directory-result-count'): #if not more than one result
                employee = assignDict(soup)
                employees.append(employee)
            else: # more than one result
                name_span = soup.find('span', class_='name')
                if name_span:
                    name_a = name_span.find('a')
                    if name_a:
                        url = "https://www.uoregon.edu" + name_a['href']
                        response = requests.get(url)
                        soup = BeautifulSoup(response.content, "html.parser")
                        employee = assignDict(soup)
                        employees.append(employee)
        else:
            employee["url"] = "Not Found"
            employee["Name"] = first + " " + last
            employees.append(employee)
            print("Not Found")

        time.sleep(3)

    with open(csvName, "w", newline='') as csv_file:
        writer = csv.writer(csv_file)

        # Write header
        if csv_file.tell() == 0:
            writer.writerow(employee.keys())

        for employee in employees:
            writer.writerow(employee.values())

def assignDict(soup):
    employee = {}
    #<link href="https://www.uoregon.edu/findpeople/person/personid/104109" rel="canonical"/>
    employee["url"] = soup.select_one("link[href]")["href"]
    employee["Name"] = soup.select_one('td.table__cell[data-th="Name"]').text.strip()
    employee["Title"] = soup.select_one('td.table__cell[data-th="Title"]').text.strip()
    employee["Department"] = soup.select_one('td.table__cell[data-th="Department"]').text.strip()
    employee["Email Address"] = soup.select_one('td.table__cell[data-th="Email Address"]').find('a').text.strip()

    employee_address = soup.select_one('td.table__cell[data-th="Office Address"]')
    if employee_address is not None:
        employee["Office Address"] = employee_address.text.strip()
    else:
        employee["Office Address"] = "Not Available"
    employee_phone = soup.select_one('td.table__cell[data-th="Office Phone"]')
    if employee_phone is not None:
        employee["Office Phone"] = employee_phone.text.strip()
    else:
        employee["Office Phone"] = "Not Available"
    
    print("Found Data")
    return employee

if __name__ == "__main__":
    query_list = [('Kai', 'Adams'), ('Jyllian', 'Martini'), ('Corey', 'Swift')]
    crawl(query_list)
