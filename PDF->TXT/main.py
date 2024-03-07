from PyPDF2 import PdfReader
import re
import json
import csv
import crawler

class Reader:
    def __init__(self, PDFfile) -> None:
        self.PDFfile = PDFfile #file location PDFS/CLASSIFIED.pdf 
        self.reader = PdfReader(self.PDFfile) #stream for pyPDF
        self.pageNumber = 106 #current page number count
        self.numPages = len(self.reader.pages) #total number of pages
        self.employees = {}
        self.activeEmployees = []
    
    def pageInterator(self):
        while self.pageNumber < self.numPages-1:
            text = self.pagePull() 
            print(self.pageNumber)
            self.decipher(text) #decipher and place items in dict
            self.pageNumber += 1
        
        text = self.pagePull() 
        self.decipher(text) #decipher and place items in dict
        self.pageNumber += 1
    
    def pagePull(self):
        page = self.reader.pages[self.pageNumber]
        text = page.extract_text()
        return text
    
    def decipher(self, text):
        #Split at new lines
        lines = text.splitlines() #makes a list with lines

        #throw out first 3 lines
        del lines[:3]

        #throw out last 2 lines
        del lines[-2:]

        #each employee takes 6 lines, 7 per page
        i = 0
        quantity = 6
        numEmployees = int(len(lines)/quantity)
        lineBuff = 0
        while i < numEmployees:
            #1 - Name: last, first middle
            names = lines[(i*quantity)+lineBuff] #pull name
            names = names.split(',') #split into last, first + middle
            last = names[0]
            result = ''
            y = 0
            
            while y < len(last):
                if y < len(last) - 1 and last[y] == ' ' and last[y+1].islower():
                    y += 1
                else:
                    result += last[y]
                y += 1

            last = result
            if len(names) > 1:
                names = names[1].split() #split first and middle into two
            else:
                print(names)

            if len(names) > 1:
                if len(names[1]) > 1: #if middle initial is more than 1
                    first = (names[0] + names[1])
                    middle = " "
                elif names[1].islower():
                    first = (names[0] + names[1])
                    middle = " "
                else:
                    first = names[0]
                    middle = names[1]
            else:
                first = names[0]
                middle = " "

            key = first + " " + last #make key with first and last ex: "Amy Gregg"
            
            if key not in self.employees:
                tempDict = {'FIRST': first, 'MIDDLE': middle, 'LAST': last}
                
                #2 - HOME DEPARTMENT
                homeDept = lines[(i*quantity)+1+lineBuff].split('HOME DEPARTMENT ')
                tempDict['HOME DEPARTMENT'] = homeDept[1]

                #3 - JOB TITLE
                jobTitle = lines[(i*quantity)+2+lineBuff].split('JOB TITLE ')
                tempDict['JOB TITLE'] = jobTitle[1]

                #4 - POSITION CLASS, TERM OF SVC, PAY DEPARTMENT, TOTAL PAY, JOB TYPE
                lineFour = lines[(i*quantity)+3+lineBuff]

                # Define the patterns for splitting
                patterns = ['POSITION CLASS', 'TERM OF SVC', 'PAY DEPARTMENT', 'TOTAL PAY', 'JOB TYPE']

                # Create a regular expression pattern by joining the patterns with '|'
                split_pattern = '|'.join(map(re.escape, patterns))

                # Split the text using the pattern
                values = re.split(split_pattern, lineFour)

                # Filter out empty strings from the result
                values = list(filter(None, values))

                for y in values:
                    y = y[:-1]
                    y = y[1:]
                
                if len(values) == 5:
                    #result = {patterns[i]: values[i] for i in range(len(patterns))}
                    tempDict['POSITION CLASS'] = values[0][1:-1]
                    tempDict['TERM OF SVC'] = values[1]
                    tempDict['PAY DEPARTMENT'] = values[2][1:-1]

                    total_pay_string = values[3]
                    # Use regular expression to extract numeric part
                    numeric_part = int(re.sub(r'\D', '', total_pay_string))
                    # Append to the dictionary
                    tempDict['TOTAL PAY'] = numeric_part
                    tempDict['JOB TYPE'] = values[4][1:]
                    
                else:
                    lineBuff += 1

                #5 - JOB START DATE, JOB STATUS
                lineFive = lines[(i*quantity)+4+lineBuff]
                # Define the patterns for splitting
                patterns = ['JOB START DATE', 'JOB STATUS']

                # Create a regular expression pattern by joining the patterns with '|'
                split_pattern = '|'.join(map(re.escape, patterns))

                # Split the text using the pattern
                values = re.split(split_pattern, lineFive)

                # Filter out empty strings from the result
                values = list(filter(None, values))

                for y in values:
                    y = y[:-1]
                    y = y[1:]
                
                if len(values) == 2:
                    #result = {patterns[i]: values[i] for i in range(len(patterns))}
                    tempDict['JOB START DATE'] = values[0][1:]
                    tempDict['JOB STATUS'] = values[1][1:]
                    #tempDict.update(result)
                
                if tempDict['JOB STATUS'] == "Active" and (first, last) not in self.activeEmployees:
                    self.activeEmployees.append((first, last, jobTitle[1]))

                #6 - JOB END DATE (can be NULL)
                endDate = lines[(i*quantity)+5+lineBuff].split('JOB END DATE ')
                if len(endDate) == 2:
                    tempDict['JOB END DATE'] = endDate[1]
                else:
                    tempDict['JOB END DATE'] = ""
                
                self.addToDict(key, tempDict)
            else:
                lineFour = lines[(i*quantity)+3+lineBuff]

                # Define the patterns for splitting
                patterns = ['POSITION CLASS', 'TERM OF SVC', 'PAY DEPARTMENT', 'TOTAL PAY', 'JOB TYPE']

                # Create a regular expression pattern by joining the patterns with '|'
                split_pattern = '|'.join(map(re.escape, patterns))

                # Split the text using the pattern
                values = re.split(split_pattern, lineFour)

                # Filter out empty strings from the result
                values = list(filter(None, values))

                if len(values) == 5:
                    total_pay_string = values[3]
                    # Use regular expression to extract numeric part
                    numeric_part = int(re.sub(r'\D', '', total_pay_string))
                

                    self.employees[key]['TOTAL PAY'] += numeric_part
                
                badkeys = ['Briana Duncan', 'Rita Gillihan','Victoria Sanchez', 'Satoko Ura Dhillon']
                if key in badkeys and lineBuff == 0:
                    lineBuff += 1
            i += 1

    def addToDict(self, employeeName, employeeInfo):
        self.employees[employeeName] = employeeInfo

if __name__ == "__main__":
    CLASSIFIED = Reader("PDFS/CLASSIFIED.pdf")
    CLASSIFIED.pageInterator()

    print(len(CLASSIFIED.activeEmployees))

    # Extracting employee information
    employees_data = CLASSIFIED.employees.values()

    # Writing employee information to CSV file
    with open("classifiedEmployees.csv", 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # Write header row
        header = ['FIRST', 'MIDDLE', 'LAST', 'HOME DEPARTMENT', 'JOB TITLE', 'POSITION CLASS',
                  'TERM OF SVC', 'PAY DEPARTMENT', 'TOTAL PAY', 'JOB TYPE', 'JOB START DATE',
                  'JOB STATUS', 'JOB END DATE']
        writer.writerow(header)

        # Write each employee's information as a row in the CSV file
        for employee_info in employees_data:
            writer.writerow([
                employee_info.get('FIRST', ''),
                employee_info.get('MIDDLE', ''),
                employee_info.get('LAST', ''),
                employee_info.get('HOME DEPARTMENT', ''),
                employee_info.get('JOB TITLE', ''),
                employee_info.get('POSITION CLASS', ''),
                employee_info.get('TERM OF SVC', ''),
                employee_info.get('PAY DEPARTMENT', ''),
                employee_info.get('TOTAL PAY', ''),
                employee_info.get('JOB TYPE', ''),
                employee_info.get('JOB START DATE', ''),
                employee_info.get('JOB STATUS', ''),
                employee_info.get('JOB END DATE', '')
            ])

    #print("crawlingggg")
    #crawler.crawl(CLASSIFIED.activeEmployees[40:60])