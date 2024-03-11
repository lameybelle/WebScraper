import requests
from bs4 import BeautifulSoup
import time
import csv

def crawl(query_list, csvName):
    # stores employees for csv
    i = 1

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

        if not soup.find(string="No matches found."):  # no results
            if not soup.find('div', class_='directory-result-count'):  # if not more than one result
                employee = assignDict(soup)

                # Write to CSV in each loop iteration
                with open(csvName, "a", newline='') as csv_file:
                    writer = csv.writer(csv_file)

                    # Write header
                    if csv_file.tell() == 0:
                        writer.writerow(employee.keys())

                    # Write the current employee's data to CSV
                    writer.writerow(employee.values())
            else:  # more than one result
                name_span = soup.find('span', class_='name')
                if name_span:
                    name_a = name_span.find('a')
                    if name_a:
                        url = "https://www.uoregon.edu" + name_a['href']
                        response = requests.get(url)
                        soup = BeautifulSoup(response.content, "html.parser")
                        employee = assignDict(soup)

                        # Write to CSV in each loop iteration
                        with open(csvName, "a", newline='') as csv_file:
                            writer = csv.writer(csv_file)

                            # Write header
                            if csv_file.tell() == 0:
                                writer.writerow(employee.keys())

                            # Write the current employee's data to CSV
                            writer.writerow(employee.values())
        else:
            employee["url"] = "Not Found"
            employee["Name"] = first + " " + last

            # Write to CSV in each loop iteration
            with open(csvName, "a", newline='') as csv_file:
                writer = csv.writer(csv_file)

                # Write header
                if csv_file.tell() == 0:
                    writer.writerow(employee.keys())

                # Write the current employee's data to CSV
                writer.writerow(employee.values())

        print(i)
        time.sleep(3)
        i += 1


def assignDict(soup):
    employee = {}
    # <link href="https://www.uoregon.edu/findpeople/person/personid/104109" rel="canonical"/>
    employee["url"] = soup.select_one("link[href]")["href"]

    employeeName = soup.select_one('td.table__cell[data-th="Name"]')
    if employeeName is not None:
        employee["Name"] = employeeName.text.strip()
    else:
        employee["Name"] = "Not Available"

    employeeTitle = soup.select_one('td.table__cell[data-th="Title"]')
    if employeeTitle is not None:
        employee["Title"] = employeeTitle.text.strip()
    else:
        employee["Title"] = "Not Available"

    employeeDept = soup.select_one('td.table__cell[data-th="Department"]')
    if employeeDept is not None:
        employee["Department"] = employeeDept.text.strip()
    else:
        employee["Department"] = "Not Available"

    employeeEmail = soup.select_one('td.table__cell[data-th="Email Address"]')
    if employeeEmail is not None:
        employee["Email Address"] = soup.select_one('td.table__cell[data-th="Email Address"]').text.strip()
    else:
        employee["Email Address"] = "Not Available"

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

    return employee


if __name__ == "__main__":
    query_list = [('Kai', 'Adams'), ('Jyllian', 'Martini'), ('Corey', 'Swift')]
    crawl(query_list, "employees.csv")
