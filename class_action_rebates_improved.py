import bs4 as bs
import pandas as pd
import requests
import itertools

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

for c in columns:
    print(df[c])