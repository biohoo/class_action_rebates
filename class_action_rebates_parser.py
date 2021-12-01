from dateutil import parser
import datetime
from urllib.parse import urlparse
import pandas as pd
import selenium
from selenium.webdriver.firefox.options import Options
from jonathan_utilities import pandas_better_formatting

pandas_better_formatting.set_pandas_options()

options = Options()
options.add_argument("--headless")

print('starting firefox...')
driver = selenium.webdriver.Firefox(options=options)

SITE = 'http://www.classactionrebates.com'

selenium_site = driver.get(SITE)

products = driver.find_elements_by_xpath('//*[@id="settlements"]/tbody/tr/td[2]/p')
urls = driver.find_elements_by_xpath('//*[@id="settlements"]/tbody/tr/td[2]/p/a')
proofs = driver.find_elements_by_xpath('//*[@id="settlements"]/tbody/tr/td[4]/p')
deadlines = driver.find_elements_by_xpath('//*[@id="settlements"]/tbody/tr/td[5]/p')

def get_deadline_status(deadline_datetime):
    if deadline_datetime < datetime.datetime.today():
        return 'Expired'
    else:
        return 'Still Good!'


def get_deadlines_return_status(deadlines):

    single_or_multiple = []
    date_as_datetime = []
    deadline_status = []

    for deadline in deadlines:
        deadline = deadline.text.strip('\n')
        if 'Pending' in deadline:
            deadline = '1/1/1900'
        if 'Estimated' in deadline:
            deadline = deadline.split(' ')[0]

        try:
            as_datetime = parser.parse(deadline)
            single_or_multiple.append('Single Date')
            date_as_datetime.append(as_datetime)
            deadline_status.append(get_deadline_status(as_datetime))

        except ValueError as e:
            dates = deadline.split(',')
            as_datetime = parser.parse(dates[-1])

            single_or_multiple.append('Multiple Dates')
            date_as_datetime.append(as_datetime)
            deadline_status.append(get_deadline_status(as_datetime))

    return single_or_multiple, date_as_datetime, deadline_status

single_or_multiple_list, date_as_datetime_list, deadline_status_list = get_deadlines_return_status(deadlines)

urls_list = []
number_of_records = 0

for url in urls:
    if url.text.find('File Claim') == -1:

        url_text = url.get_attribute('href')
        domain = urlparse(url_text).netloc

        if domain == 'www.classactionrebates.com':

            urls_list.append(url.get_attribute('href'))
            number_of_records += 1

print('number of records: ', number_of_records)

proofs_list = [pr.text for pr in proofs]
products_list = [pr.text.replace('\n',' ') for pr in products]


rebates_dict = {
    'Proof':proofs_list,
    'Products':products_list,
    'Deadline_Status': deadline_status_list,
    'Single_Multiple': single_or_multiple_list,
    'Deadline_Date': date_as_datetime_list,
    'URL': urls_list
}


df = pd.DataFrame.from_dict(rebates_dict)
print(df)

df1 = df[(df.Proof != 'Yes') & (df.Deadline_Status != 'Expired')]

proofless_unexpired = len(df1)

print('''\n\n>>>>>> Filtered for unexpired and no proof of purchase <<<<<<''')
print(df1[['URL','Products']])
print('Number of proofless, unexpired records: ', proofless_unexpired)
print('Percent of total: ', round((proofless_unexpired / number_of_records) * 100, 0))

df1.to_csv('class_action_filtered.csv')
df.to_csv('class_action.csv')
