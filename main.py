from PyPDF2 import PdfReader
import re
import csv
import crawler

class ClassifiedReader:
    def __init__(self, PDFfile) -> None:
        self.PDFfile = PDFfile #file location PDFS/CLASSIFIED.pdf 
        self.reader = PdfReader(self.PDFfile) #stream for pyPDF
        self.pageNumber = 1 #current page number count
        self.numPages = len(self.reader.pages) #total number of pages
        self.employees = {}
        self.activeEmployees = []
    
    def pageInterator(self):
        while self.pageNumber < self.numPages-1:
            print(self.pageNumber)
            text = self.pagePull() 
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
                    self.activeEmployees.append((first, last))

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

class UnclassifiedReader:
    def __init__(self, PDFfile) -> None:
        self.PDFfile = PDFfile #file location PDFS/CLASSIFIED.pdf 
        self.reader = PdfReader(self.PDFfile) #stream for pyPDF
        self.pageNumber = 1 #current page number count
        self.numPages = len(self.reader.pages) #total number of pages
        self.employees = {}
        self.activeEmployees = []
    
    def pageInterator(self):
        while self.pageNumber < self.numPages-1:
            print(self.pageNumber)
            text = self.pagePull() 
            self.decipher(text) #decipher and place items in dict
            self.pageNumber += 1
        
        text = self.pagePull() 
        #self.decipher(text) #decipher and place items in dict
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

        #each employee takes 8 lines, 6 per page
        i = 0
        quantity = 8
        numEmployees = int(len(lines)/quantity)
        lineBuff = 0
        while i < numEmployees:
            #1 - Name: last, first middle
            names = lines[(i*quantity)+lineBuff] #pull name
            names = names[15:]
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
                homeDept = lines[(i*quantity)+1+lineBuff]
                tempDict['HOME DEPARTMENT'] = homeDept

                #3 - ACADEMIC TITLE
                academicTitle = lines[(i*quantity)+2+lineBuff].split('ACADEMIC TITLE ')
                tempDict["ACADEMIC TITLE"] = academicTitle[1]

                #4 - TERM OF SVC, PAY DEPARTMENT
                lineFour = lines[(i*quantity)+3+lineBuff]
                patterns = ['TERM OF SVC', 'PAY DEPARTMENT']

                # Create a regular expression pattern by joining the patterns with '|'
                split_pattern = '|'.join(map(re.escape, patterns))

                # Split the text using the pattern
                values = re.split(split_pattern, lineFour)

                # Filter out empty strings from the result
                values = list(filter(None, values))

                if len(values) == 2:
                    tempDict['TERM OF SVC'] = values[0]
                    tempDict['PAY DEPARTMENT'] = values[1][1:]
                else:
                    lineBuff += 1
                

                #5 - TOTAL PAY, JOB TYPE
                lineFive = lines[(i*quantity)+4+lineBuff]

                # Define the patterns for splitting
                patterns = ['TOTAL PAY', 'JOB TYPE']

                # Create a regular expression pattern by joining the patterns with '|'
                split_pattern = '|'.join(map(re.escape, patterns))

                # Split the text using the pattern
                values = re.split(split_pattern, lineFive)

                # Filter out empty strings from the result
                values = list(filter(None, values))
                
                if len(values) == 2:
                    total_pay_string = values[0]
                    # Use regular expression to extract numeric part
                    numeric_part = int(re.sub(r'\D', '', total_pay_string))
                    # Append to the dictionary
                    tempDict['TOTAL PAY'] = numeric_part
                    tempDict['JOB TYPE'] = values[1]
                    
                else:
                    lineBuff += 1

                #6 - JOB START DATE, JOB STATUS
                lineSix = lines[(i*quantity)+5+lineBuff]
                # Define the patterns for splitting
                patterns = ['JOB START DATE', 'as of 6/30/2023']

                # Create a regular expression pattern by joining the patterns with '|'
                split_pattern = '|'.join(map(re.escape, patterns))

                # Split the text using the pattern
                values = re.split(split_pattern, lineSix)

                # Filter out empty strings from the result
                values = list(filter(None, values))
                
                if len(values) == 2:
                    tempDict['JOB START DATE'] = values[0][1:]
                    tempDict['JOB STATUS'] = values[1][1:]
                
                if tempDict['JOB STATUS'] == "Active" and (first, last) not in self.activeEmployees:
                    self.activeEmployees.append((first, last))

                #7 - JOB END DATE (can be NULL)
                endDate = lines[(i*quantity)+6+lineBuff].split('JOB END DATE ')
                if len(endDate) == 2:
                    tempDict['JOB END DATE'] = endDate[1]
                else:
                    tempDict['JOB END DATE'] = ""
                
                #8 - OA SALARY GRADE, POSITION CLASS
                lineEight = lines[(i*quantity)+7+lineBuff]
                # Define the patterns for splitting
                patterns = ['OA SALARY GRADE', 'POSITION CLASS', 'JOB STATUS']

                # Create a regular expression pattern by joining the patterns with '|'
                split_pattern = '|'.join(map(re.escape, patterns))

                # Split the text using the pattern
                values = re.split(split_pattern, lineEight)

                # Filter out empty strings from the result
                values = list(filter(None, values))
                
                if len(values) == 2:
                    tempDict['OA SALARY GRADE'] = values[0][1:]
                    tempDict['POSITION CLASS'] = values[1][1:]
                
                self.addToDict(key, tempDict)
            else:
                lineFive = lines[(i*quantity)+4+lineBuff]

                # Define the patterns for splitting
                patterns = ['TOTAL PAY', 'JOB TYPE']

                # Create a regular expression pattern by joining the patterns with '|'
                split_pattern = '|'.join(map(re.escape, patterns))

                # Split the text using the pattern
                values = re.split(split_pattern, lineFive)

                # Filter out empty strings from the result
                values = list(filter(None, values))
                
                if len(values) == 2:
                    total_pay_string = values[0]
                    # Use regular expression to extract numeric part
                    numeric_part = int(re.sub(r'\D', '', total_pay_string))
                    self.employees[key]['TOTAL PAY'] += numeric_part
                    
                else:
                    lineBuff += 1
                
                badkeys = []
                if key in badkeys and lineBuff == 0:
                    lineBuff += 1
            i += 1

    def addToDict(self, employeeName, employeeInfo):
        self.employees[employeeName] = employeeInfo

if __name__ == "__main__":
    #CLASSIFIED = ClassifiedReader("PDFS/CLASSIFIED.pdf")
    #CLASSIFIED.pageInterator()
    #print("done with classified")
    UNCLASSIFIED = UnclassifiedReader("PDFS/UNCLASSIFIED.pdf")
    UNCLASSIFIED.pageInterator()
    print("done with unclassified")
    
    # Writing unclassified employee information to CSV file
    with open("unclassifiedEmployees.csv", 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # Write header row
        header = ['FIRST', 'MIDDLE', 'LAST', 'HOME DEPARTMENT', 'ACADEMIC TITLE',
                'TERM OF SVC', 'PAY DEPARTMENT', 'TOTAL PAY', 'JOB TYPE',
                'JOB START DATE', 'JOB STATUS', 'JOB END DATE', 'OA SALARY GRADE', 'POSITION CLASS']
        writer.writerow(header)

        # Write each unclassified employee's information as a row in the CSV file
        for employee_info in UNCLASSIFIED.employees.values():
            writer.writerow([
                employee_info.get('FIRST', ''),
                employee_info.get('MIDDLE', ''),
                employee_info.get('LAST', ''),
                employee_info.get('HOME DEPARTMENT', ''),
                employee_info.get('ACADEMIC TITLE', ''),
                employee_info.get('TERM OF SVC', ''),
                employee_info.get('PAY DEPARTMENT', ''),
                employee_info.get('TOTAL PAY', ''),
                employee_info.get('JOB TYPE', ''),
                employee_info.get('JOB START DATE', ''),
                employee_info.get('JOB STATUS', ''),
                employee_info.get('JOB END DATE', ''),
                employee_info.get('OA SALARY GRADE', ''),
                employee_info.get('POSITION CLASS', '')
            ])


    print(len(UNCLASSIFIED.activeEmployees))

    # Extracting employee information
    #employees_data = CLASSIFIED.employees.values()
    
    ''' 
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
            ])'''
    print("crawlingggg")

    #start back up on 1726
    #crawler.crawl(CLASSIFIED.activeEmployees[1726:], "classifiedFindPeople.csv")
    crawler.crawl(UNCLASSIFIED.activeEmployees[351:], "unclassifiedFindPeople.csv")