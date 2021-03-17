from bs4 import BeautifulSoup
import pandas as pd
import requests
import pprint
import unicodedata
import datetime

junk = ['Βορείου Τομέα Αθηνών', 'Δυτικού Τομέα Αθηνών', 'Κεντρικού Τομέα Αθηνών',
        'Νοτίου Τομέα Αθηνών', 'Πειραιώς', 'Νήσων', 'Ανατολικής Αττικής','Δυτικής Αττικής',]

GREEK_PE = ['Δράμας', 'Έβρου', 'Καβάλας', 'Θάσου', 'Ξάνθης', 'Ροδόπης', 'Ημαθίας', 'Θεσσαλονίκης', 'Κιλκίς', 'Πέλλας',
            'Πιερίας', 'Σερρών', 'Χαλκιδικής', 'Γρεβενών', 'Καστοριάς', 'Κοζάνης', 'Φλώρινας', 'Άρτας', 'Θεσπρωτίας',
            'Ιωαννίνων', 'Πρέβεζας', 'Καρδίτσας', 'Λάρισας', 'Μαγνησίας', 'Σποράδων', 'Τρικάλων', 'Ζακύνθου',
            'Κέρκυρας', 'Κεφαλληνίας', 'Ιθάκης', 'Λευκάδας', 'Αιτωλοακαρνανίας', 'Αχαΐας', 'Ηλείας', 'Βοιωτίας',
            'Εύβοιας', 'Ευρυτανίας', 'Φθιώτιδας', 'Φωκίδας', 'Αργολίδας', 'Αρκαδίας', 'Κορινθίας', 'Λακωνίας', 'Μεσσηνίας', 'Λέσβου', 'Ικαρίας',
            'Λήμνου', 'Σάμου', 'Χίου', 'Άνδρου', 'Μήλου', 'Θήρας', 'Κέας-Κύθνου', 'Μυκόνου', 'Νάξου', 'Σύρου', 'Τήνου',
            'Πάρου', 'Καλύμνου', 'Καρπάθου', 'Κω', 'Ρόδου', 'Ηρακλείου', 'Λασιθίου', 'Ρεθύμνης', 'Χανίων', 'Αττικής']


# function that returns a list of dates starting from the last it reads from the txt
def list_with_dates(year=2020, month=9, day=14):

    # starting date
    d1 = datetime.date(year, month, day)

    # stopping date
    # d2 = datetime.date(2021, 3, 7)

    d2 = datetime.date.today()
    diff = d2 - d1
    dates_until_today = []

    # get a list with dates from starting to stopping date
    for i in range(diff.days + 1):
        dates_until_today.append(d1 + datetime.timedelta(i))
        dates_until_today[-1] = dates_until_today[-1].strftime("%d-%m-%Y")

    # get rid of the starting date since you already parsed that
    del dates_until_today[0]

    return dates_until_today


# script to remove greek accents from strings
def remove_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')


def parser(dateInUse):
    link = f'http://www.odigostoupoliti.eu/koronoios-krousmata-simera-{dateInUse}-stin-ellada/'

    # get html data
    page = requests.get(link)

    # check if status code is good ( 200 )
    if page.status_code != 200:
        link = f'http://www.odigostoupoliti.eu/koronoios-krousmata-simera-stin-ellada-{dateInUse}/'
        page = requests.get(link)

        if page.status_code != 200:
            exit(f'Error {page.status_code}! Page not found')

    # get page parsed into <class 'bs4.BeautifulSoup'>
    soup = BeautifulSoup(page.content, 'html.parser')

    # find all elements under the <p> html tag
    p = soup.find_all('p')  # result is of type <class 'bs4.element.ResultSet'>

    # get only text from ul
    paragraphText = []

    # job_elem is of type <class 'bs4.element.Tag'>
    for job_elem in p:
        paragraphText.append(job_elem.text)

    # specify the stop index of usefull date
    stopIndex = 0
    for i in range(len(paragraphText)):
        if 'Σχετικά' in paragraphText[i]:
            stopIndex = i

    # from paragraphText get only the usefull data using start - stop indexes
    caseList = paragraphText[paragraphText.index('Σε ποιες περιοχές εντοπίζονται τα νέα κρούσματα'):stopIndex]

    # do this to avoid having \xa0 in your data
    caseList = [unicodedata.normalize("NFKD", x) for x in caseList]

    # START filtering data on caseList

    # some times we need to split the data in caseList
    flag = False
    for string in caseList:
        if string.count('\n'):
            flag = True
    if flag:
        caseList = ['$'.join(x.split('\n')) for x in caseList]
        caseList = '$'.join(caseList)
        caseList = caseList.split('$')
        print('This was used')

    # from every string get a corresponding number if a name from GREEK_PE is in that string
    for string in caseList:
        for name in GREEK_PE:
            flag = False
            # remove the accents from the greek words and make all lower case
            filtered_name = remove_accents(name).lower()
            string = remove_accents(string).lower()

            # if name ends with 'ς' then remove the ς
            if filtered_name[-1] == 'ς':
                # slicing the string is faster than string.replace()
                filtered_name = filtered_name[:-1]

            # if name ends with 'ου' then remove the υ
            if filtered_name[-1] == 'υ':
                filtered_name = filtered_name[:-1]

            # if name in string == True then this string has useful info and we need to filter it properly
            if filtered_name in string:
                flag = True
            # cover special cases of some names
            elif name == 'Ιωαννίνων':
                if 'ιωαννινα' in string:
                    flag = True
            elif name == 'Σερρών':
                if 'σερρε' in string:
                    flag = True
            elif name == 'Χανίων':
                if 'χανια' in string:
                    flag = True
            elif name == 'Τρικάλων':
                if 'τρικαλα' in string:
                    flag = True
            elif name == 'Σποράδων':
                if 'σποραδες' in string:
                    flag = True
            elif name == 'Ρεθύμνης':
                if 'ρεθυμνο' in string:
                    flag = True

            # if one of the previous checks is true then get all numbers from current string
            if flag:

                ''' sometimes it can pick up a string that passed all the requirments but doesn't 
                contain a number so it raises ValueError '''
                try:
                    cases = int(''.join([x for x in string if x.isnumeric()]))
                except ValueError:
                    continue
                if name == 'Αττικής' and 'Αττικής' in catalog.keys():

                    if dateInUse in catalog['Αττικής'].keys():

                        continue

                # create catalog
                # if district exists
                if name in catalog.keys():
                    catalog[name].update({dateInUse: cases})

                # if district has first time  cases
                else:
                    catalog[name] = {dateInUse: cases}


if __name__ == '__main__':
    catalog = {}

    # set the date range for parsing
    try:
        # read the excel file to get last date parsed
        old_df = pd.read_excel(r"C:\Users\ARIS\Desktop\official.xlsx", index_col=0)

        # get the last date index from excel in str format and gives it as start reference to datetime
        last_date = old_df.index[-1].split('-')
        year, month, day = int(last_date[-1]), int(last_date[-2]), int(last_date[-3])

        dateRange = list_with_dates(year, month, day)
    except FileNotFoundError:
        dateRange = list_with_dates()

    # parser('02-03-2021')
    for date in dateRange:
        try:
            parser(date)
            print(date)
        except:
            pass
    # pprint.pprint(catalog)

    df = pd.DataFrame(dict(catalog))
    result = pd.concat([old_df, df])
    print(df)

    result.to_excel(r"C:\Users\ARIS\Desktop\test.xlsx")
