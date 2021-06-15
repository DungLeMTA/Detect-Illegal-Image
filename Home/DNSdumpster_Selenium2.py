from bs4 import BeautifulSoup
import urllib.request as request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# url =  'https://vnexpress.net'
# page = request.urlopen(url)
# soup = BeautifulSoup(page, 'html.parser')
#
# new_feed = soup.find('h3', class_='title-news').find('a')
# title = new_feed.get('title')
# link = new_feed.get('href')
# print('Title: {} - Link: {}'.format(title, link))

class dnsdumster:
    link = ''
    dns_servers = []
    mx_records = []
    txt_records = []
    host_records = []
    mapping = ''

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome("B:\PycharmProjects\OCR_project\chromedriver.exe",options=options)
def Crawl_Data_DNSdumpster(url):

    A = dnsdumster()
    A.link = url

    dnsdumpster = 'https://dnsdumpster.com/'
    driver.get(dnsdumpster)
    tbInput = driver.find_element_by_css_selector('#regularInput')
    btnSearch = driver.find_element_by_css_selector('#formsubmit > button')
    tbInput.send_keys(url)
    btnSearch.click()

    table = driver.find_elements_by_class_name('table-responsive')

    ########################################################## lấy dns_server
    domain = table[0].find_elements_by_class_name('col-md-4')
    ip_name = table[0].find_elements_by_class_name('col-md-3')

    print('________________________________________________________________')
    print('DNS SERVER:')
    try:
        for i in range(0,len(domain)):
            print(domain[i].text,'---',ip_name[2*i].text.split('\n')[0],'---',ip_name[2*i-1].text.split('\n')[0],
                  '(',ip_name[2*i-1].text.split('\n')[1],')')
            A.dns_servers.append([domain[i].text, ip_name[2*i].text.split('\n')[0],
                                  ip_name[2*i-1].text.split('\n')[0]+', '+ip_name[2*i-1].text.split('\n')[1]])
        print('________________________________________________________________')
    except:
        print('No result')
    ########################################################## lấy MX record
    mail = table[1].find_elements_by_class_name('col-md-4')
    ip_mail = table[1].find_elements_by_class_name('col-md-3')
    print('________________________________________________________________')
    print('MX Records:')
    try:
        for i in range(0,len(mail)):
            print(mail[i].text,'---',ip_mail[2*i].text.split('\n')[0],'(',ip_mail[2*i].text.split('\n')[1],')',
                  '---',ip_mail[2*i-1].text.split('\n')[0],'(',ip_mail[2*i-1].text.split('\n')[1],')')
            A.mx_records.append([mail[i].text,ip_mail[2*i].text.split('\n')[0]],ip_mail[2*i].text.split('\n')[1],
                                ip_mail[2*i-1].text.split('\n')[0],ip_mail[2*i-1].text.split('\n')[1])
        print('________________________________________________________________')
    except:
        print('No result')

    ########################################################## lấy TXT_record

    txt = table[2].find_elements_by_tag_name('td')
    print('________________________________________________________________')
    print('TXT Records:')
    try:
        for i in range(0, len(txt)):
            print(txt[i].text)
            A.txt_records.append(txt[i].text)
        print('________________________________________________________________')
    except:
        print('No result')

    ########################################################## lấy Host_record
    host = table[3].find_elements_by_class_name('col-md-4')
    ip_host = table[3].find_elements_by_class_name('col-md-3')
    print('________________________________________________________________')
    print('Host Records:')
    try:
        for i in range(0,len(host)):
            host_name = host[i].text
            ip = ip_host[2*i].text
            if '\n' in host_name:
                host_name = host_name.split('\n')[0]
            if '\n' in ip:
                ip = ip.split('\n')[0]

            print(host_name,'---',ip)
            A.host_records.append([host_name,ip])
        print('________________________________________________________________')
    except:
        print('No result')

    ########################################################## lấy mapping
    # mapping = table[4]
    try:
        request.urlretrieve(dnsdumpster+'/static/map/'+url+'.png',
                            'B:\PycharmProjects\detai_django\Home\static\images\mapping\mapping_'+url+'.png')
        A.mapping = "images/mapping/mapping_"+url+".png"
        print('Saved mapping!',A.mapping)
    except:
        print('No mapping')
    return A

def cut_link(link):
    link2 = link.split('//')
    link3 = link2[1].split('/')
    return link3[0]

if __name__ == '__main__':
    link1 = 'https://facebook.com/'
    link = cut_link(link1)
    print(link)
    Crawl_Data_DNSdumpster(link)