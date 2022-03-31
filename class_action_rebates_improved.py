import bs4 as bs
import pandas as pd
import requests
from dateutil import parser
from datetime import datetime

TODAY = datetime.now()

SITE = 'http://www.classactionrebates.com'
f = requests.get(SITE).text

soup = bs.BeautifulSoup(f, 'lxml')
parsed_table = soup.find_all('table')[0]

data = []

for row in parsed_table.find_all('tr'):
    row_result = []
    for td in row.find_all('td'):
        if td.find('a'):
            row_result.append(td.a['href'])
            row_result.append(''.join(td.stripped_strings))
        else:
            row_result.append(''.join(td.stripped_strings))
    data.append(row_result)

print('data: ', data)
columns = ['icon', 'URL','description','Estimate','Proof','Deadline']
df = pd.DataFrame(data[1:], columns=columns)

def is_expired(dateString):

    if 'Pending' in dateString:
        return False

    if 'Estimated' in dateString:
        deadline = dateString.split(' ')[0]
        as_datetime = parser.parse(deadline)
        return TODAY > as_datetime

    if ',' in dateString:
        # Multiple dates in deadline.  Taking latest.
        dates = dateString.split(',')
        as_datetime = parser.parse(dates[-1])
        return TODAY > as_datetime

    as_datetime = parser.parse(dateString)
    return TODAY > as_datetime


df['is_expired'] = df['Deadline'].apply(lambda x: is_expired(x))

for c in df.columns:
    print(df[c])
