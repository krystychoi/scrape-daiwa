'''
Created on Nov 4, 2016

@author: U0080217
'''
import os
import requests
import re 
import urllib
from lxml import html
from datetime import datetime

#build directories
cwd = os.getcwd()
mdirectory = cwd + '/monthly'
if not os.path.exists(mdirectory):
    os.mkdir(mdirectory)
adirectory = cwd + '/annual'
if not os.path.exists(adirectory):
    os.mkdir(adirectory)

#create logs
mlog_path = mdirectory + '/mlog.txt'
alog_path = adirectory + '/alog.txt'

#create totals
mpdf_total = 0
apdf_total = 0

#start logs
with open(mlog_path,'a') as text_file:
    text_file.write('[INFO] ' + str(datetime.now()) + ' start pdf download...' +'\n')

with open(alog_path,'a') as text_file:
    text_file.write('[INFO] ' + str(datetime.now()) + ' start pdf download...' +'\n')
    
#get page links
url = 'http://www.daiwa-am.co.jp/funds/search/results/quick_result.html?act=1&srch_funds_name=&srch_invest%5B%5D=0&srch_etf_focus=1&srch_index_focus=1&srch_every_focus=1&srch_bullbear_focus=1&srch_distrib%5B%5D=0&srch_corp_bond=&srch_corp_bank=&srch_corp_post=1&act=1&ch=%EF%BF%BD'
search_page = requests.get(url)
search_html = html.fromstring(search_page.content)

end_num  = []

last_page = search_html.xpath('//div[@class="pageBute"][1]//a[2]/@href')
for page in last_page:
    end_num = page[-2:]

pages = []

end_range = int(end_num) + 1
for i in range(0,end_range):
    page = url + '&page=' + str(i)
    pages.append(page)

#start scraping
for page in pages:
    search_page = requests.get(page)
    search_html = html.fromstring(search_page.content)
    
    detail_links = search_html.xpath('//td[@class="detailLink"]//a[1]/@href')
    for link in detail_links:
        if link.startswith('http://etf'):            
            detail_page_etf = requests.get(link)
            detail_html_etf = html.fromstring(detail_page_etf.content)
            
            report_link_etf = detail_html_etf.xpath('//li[@class="report"]//a/@href')
            for link in report_link_etf:
                report_url_etf = 'http://etf.daiwa-am.co.jp' + link 
                report_page_etf = requests.get(report_url_etf)
                report_html_etf = html.fromstring(report_page_etf.content)
                
                names_etf = []
                mlinks_etf = []
                
                fund_names_etf = report_html_etf.xpath('//div[@class="main"]//h1/text()')
                for name in fund_names_etf:
                    name = name.replace(':','-').replace('/','-')
                    names_etf.append(name)
                
                monthly_links_etf = report_html_etf.xpath('//div[@class="mainData"]//ul[@class="calendar"][1]//a/@href')
                for link in monthly_links_etf:
                    pdf_url_etf = 'http://etf.daiwa-am.co.jp' + link + '.pdf'
                    mlinks_etf.append(pdf_url_etf)
                
                for name,mlink in zip(names_etf,mlinks_etf):
                    name = re.sub('<.*?>','',name)
                    pdf_name = name + '.pdf'
                    download_directory = mdirectory + '/' + pdf_name
                    mpdf_total += 1
                    try:
                        urllib.urlretrieve(mlink,download_directory)
                        with open(mlog_path,'a') as text_file:
                            text_file.write('[INFO] Downloaded ' + name.encode('utf-8') + ' from ' + mlink + '\n')
                    except Exception, e:
                        with open(mlog_path,'a') as text_file:
                            text_file.write('[ERROR] Failed to download ' + name.encode('utf-8') + ' from ' + mlink + '\n' + '[ERROR] ' + str(e) + '\n')
                        continue
               
        else:
            
            detail_url = 'http://www.daiwa-am.co.jp' + link
            detail_page = requests.get(detail_url)
            detail_html = html.fromstring(detail_page.content)
            
            names = []
            mlinks = []
            alinks = []
            
            fund_names = detail_html.xpath('//div[@class="fundname"]//h2/text()')
            for name in fund_names:
                name = name.replace(':','-').replace('/','-')
                names.append(name.strip())
            
            monthly_links = detail_html.xpath('//ul[@class="prospectusList "]//li[@class="clearfix w149"]//a/@href')
            for link in monthly_links:
                pdf_url = 'http://www.daiwa-am.co.jp' + link + '.pdf'
                mlinks.append(pdf_url)
            
            for name,mlink in zip(names,mlinks):
                name = re.sub('<.*?>','',name)
                pdf_name = name + '.pdf'
                download_directory = mdirectory + '/' + pdf_name
                mpdf_total += 1
                try:
                    urllib.urlretrieve(mlink,download_directory)
                    with open(mlog_path,'a') as text_file:
                            text_file.write('[INFO] Downloaded ' + name.encode('utf-8') + ' from ' + mlink + '\n')
                except Exception, e:
                    with open(mlog_path,'a') as text_file:
                            text_file.write('[ERROR] Failed to download ' + name.encode('utf-8') + ' from ' + mlink + '\n' + '[ERROR] ' + str(e) + '\n')
                    continue
            
            annualreport_link = detail_html.xpath('//ul[@class="prospectusList"]//li[@class="clearfix w188"]//a/@href')
            for link in annualreport_link:
                annualreport_url = 'http://www.daiwa-am.co.jp' + link
                annualreport_page = requests.get(annualreport_url)
                annualreport_html = html.fromstring(annualreport_page.content)
                
                annual_links = annualreport_html.xpath('//td[@class="tdData"][1]//a/@href')
                for link in annual_links:
                    alinks.append(link)
            
            for name,alink in zip(names,alinks):
                name = re.sub('<.*?>','',name)
                pdf_name = name + '.pdf'
                download_directory = adirectory + '/' + pdf_name
                apdf_total += 1
                try:
                    urllib.urlretrieve(alink,download_directory)
                    with open(alog_path,'a') as text_file:
                        text_file.write('[INFO] Downloaded ' + name.encode('utf-8') + ' from ' + alink + '\n')
                except Exception, e:
                    with open(alog_path,'a') as text_file:
                            text_file.write('[ERROR] Failed to download ' + name.encode('utf-8') + ' from ' + alink + '\n' + '[ERROR] ' + str(e) + '\n')
                    continue
                
#close logs 
with open(mlog_path,'a') as text_file:
    text_file.write('[INFO] ' + str(datetime.now()) + ' end pdf download...' + '\n' + '[INFO] ' + str(mpdf_total) + ' pdf files downloaded' + '\n' + '[INFO] Download complete.' + '\n')

with open(alog_path,'a') as text_file:
    text_file.write('[INFO] ' + str(datetime.now()) + ' end pdf download...' + '\n' + '[INFO] ' + str(apdf_total) + ' pdf files downloaded' + '\n' + '[INFO] Download complete.' + '\n')    