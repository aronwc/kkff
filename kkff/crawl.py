'Crawl PDFs list on water.issuelab.org.'
from bs4 import BeautifulSoup
import os
import re
import requests


for pagenum in range(0, 120)[0:120:10]:
    soup = BeautifulSoup(requests.get('http://water.issuelab.org/home/' +
                                      'limit/' + str(pagenum) +
                                      '/view/all').text)
    for div in soup.find_all('div', class_='txt'):
        url = div.h3.a['href']
        name = re.match(r'.*resource\/(.+)', url).group(1)
        fname = '../data/' + name + '.pdf'
        if os.path.exists(fname):  # already have this one
            print 'already have', fname
            next
        report_html = 'http://water.issuelab.org/' + url
        print 'fetching', report_html
        report_soup = BeautifulSoup(requests.get(report_html).text)
        pdf = report_soup.h2.a['href']
        if 'download2' in pdf:
            print '\tfollowing redirect'
            redirect_text = requests.get(pdf).text
            match = re.match(r'.*url=([^\"]+)\"', redirect_text)
            if match:
                pdf = match.group(1)
            else:
                print 'no report found for', report_html
                next
        print '\tfetching pdf', pdf
        r = requests.get(pdf)
        with open(fname, "wb") as outf:
            outf.write(r.content)
