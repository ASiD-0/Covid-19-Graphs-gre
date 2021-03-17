from bs4 import BeautifulSoup
import pandas as pd
import requests
import pprint
import unicodedata
import datetime


# function that returns a list of dates starting from the last it reads from the txt
def list_with_dates():

    # if no other date is present use this as the default
    year, month, day = 2020, 11, 16
    try:
        # checks excel file for days already parsed
        x = pd.read_excel(r"C:\Users\ARIS\Desktop\a.xlsx", index_col=0)

        # get the last date index from excel in str format and gives it as start reference to datetime
        last_date = x.index[-1].split('-')
        year, month, day = int(last_date[-1]), int(last_date[-2]), int(last_date[-3])
    except FileNotFoundError:
        pass
    # starting date
    d1 = datetime.date(year, month, day)

    # stopping date
    d2 = datetime.date(2020, 11, 27)

    # d2 = datetime.date.today()
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


GREEK_PE = ['Δράμας', 'Έβρου', 'Καβάλας', 'Θάσου', 'Ξάνθης', 'Ροδόπης', 'Ημαθίας', 'Θεσσαλονίκης', 'Κιλκίς', 'Πέλλας',
            'Πιερίας', 'Σερρών', 'Χαλκιδικής', 'Γρεβενών', 'Καστοριάς', 'Κοζάνης', 'Φλώρινας', 'Άρτας', 'Θεσπρωτίας',
            'Ιωαννίνων', 'Πρέβεζας', 'Καρδίτσας', 'Λάρισας', 'Μαγνησίας', 'Σποράδων', 'Τρικάλων', 'Ζακύνθου',
            'Κέρκυρας', 'Κεφαλληνίας', 'Ιθάκης', 'Λευκάδας', 'Αιτωλοακαρνανίας', 'Αχαΐας', 'Ηλείας', 'Βοιωτίας',
            'Εύβοιας', 'Ευρυτανίας', 'Φθιώτιδας', 'Φωκίδας', 'Βορείου Τομέα Αθηνών', 'Δυτικού Τομέα Αθηνών',
            'Κεντρικού Τομέα Αθηνών', 'Νοτίου Τομέα Αθηνών', 'Πειραιώς', 'Νήσων', 'Ανατολικής Αττικής',
            'Δυτικής Αττικής', 'Αργολίδας', 'Αρκαδίας', 'Κορινθίας', 'Λακωνίας', 'Μεσσηνίας', 'Λέσβου', 'Ικαρίας',
            'Λήμνου', 'Σάμου', 'Χίου', 'Άνδρου', 'Μήλου', 'Θήρας', 'Κέας-Κύθνου', 'Μυκόνου', 'Νάξου', 'Σύρου', 'Τήνου',
            'Πάρου', 'Καλύμνου', 'Καρπάθου', 'Κω', 'Ρόδου', 'Ηρακλείου', 'Λασιθίου', 'Ρεθύμνης', 'Χανίων', 'Αττικής']


def parser(dateInUse):
    link = f'http://www.odigostoupoliti.eu/koronoios-krousmata-simera-{dateInUse}-stin-ellada/'

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

    for string in caseList:
        for name in GREEK_PE:
            # if name in string == True then this string has useful info and we need to filter it properly
            if remove_accents(name).lower().replace('ς', '') in remove_accents(string).lower():
                # sometimes it can pick up a string that passed all the requirments but doesn't contain a number so it raises ValueError
                try:
                    cases = int(''.join([x for x in string.split() if x.isnumeric()]))
                except ValueError:
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
    dateRange = list_with_dates()
    for date in dateRange:
        try:
            parser(date)
            print(date)
        except:
            pass

    # pprint.pprint(catalog)

    df = pd.DataFrame(dict(catalog))
    print(df)
    df.to_excel(r"C:\Users\ARIS\Desktop\test.xlsx")
