from PyPDF2 import PdfReader
import re
import json

class Reader:
    def __init__(self, PDFfile) -> None:
        self.PDFfile = PDFfile #file location PDFS/CLASSIFIED.pdf 
        self.reader = PdfReader(self.PDFfile) #stream for pyPDF
        self.pageNumber = 1 #current page number count
        self.numPages = len(self.reader.pages) #total number of pages
        self.employees = {}
    
    def pageInterator(self):
        while self.pageNumber < self.numPages-1:
            print("page number ", self.pageNumber)
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
            names = names.split() #split into last, first, middle
            names[0] = names[0][:-1] #remove comma
            key = names[1] + " " + names[0] #make key with first and last ex: "Amy Gregg"
            if len(names) >= 3:
                tempDict = {'FIRST': names[1], 'MIDDLE': names[2], 'LAST': names[0]}
            else:
                tempDict = {'FIRST': names[1], 'MIDDLE': ' ', 'LAST': names[0]}
            
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
                result = {patterns[i]: values[i] for i in range(len(patterns))}
                tempDict.update(result)
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
                result = {patterns[i]: values[i] for i in range(len(patterns))}
                tempDict.update(result)

            #6 - JOB END DATE (can be NULL)
            endDate = lines[(i*quantity)+5+lineBuff].split('JOB END DATE ')
            if len(endDate) == 2:
                tempDict['JOB END DATE'] = endDate[1]
            else:
                tempDict['JOB END DATE'] = ""
            
            self.addToDict(key, tempDict)
            #check if the self.employees alerady has an entry for that employee
            #if yes: rearrange employee value to include new information (maybe as a list?)
            #if not: add

            i += 1

    def addToDict(self, employeeName, employeeInfo):
        self.employees[employeeName] = employeeInfo

if __name__ == "__main__":
    CLASSIFIED = Reader("PDFS/CLASSIFIED.pdf")
    CLASSIFIED.pageInterator()
    with open('classified.txt', 'w') as convert_file: 
        convert_file.write(json.dumps(CLASSIFIED.employees))