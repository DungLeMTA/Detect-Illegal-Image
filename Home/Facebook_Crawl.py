import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from tqdm import tqdm
import requests
from urllib.parse import urljoin, urlparse
import time

options = Options()
# options.add_argument("--headless")
options.add_argument("--disable-popup-blocking")
prefs = {"profile.default_content_setting_values.notifications" : 2}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome("B:\PycharmProjects\OCR_project\chromedriver.exe",options=options)

def loginFB(user,password):
    facebook = 'https://www.facebook.com/'
    driver.get(facebook)
    driver.maximize_window()
    # đăng nhập
    tbEmail = driver.find_element_by_css_selector('#email')
    tbPass = driver.find_element_by_css_selector('#pass')
    btnLogin = driver.find_element_by_name('login')
    tbEmail.send_keys(user)
    tbPass.send_keys(password)
    btnLogin.click()


def Crawl_Info_Facebook(link, folder):
    print('Starting crawl Profile...')
    if link.find('profile.php?') != -1:
        driver.get(link+'&sk=about')
    else:
        driver.get(link+'/about')
    name,sex,birth,work, studied,comefrom,status,phone='','','','','','','',''
    try:
        name = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div/div[1]/div/div/span/h1').text
    except:
        pass
    try:
        work = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div[1]/div/div/div[2]/div').text
    except:
        pass
    try:
        studied = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div[2]/div/div/div[2]/div').text
    except:
        pass
    try:
        comefrom = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div[3]/div/div/div[2]/div').text
    except:
        pass
    try:
        status = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div[4]/div/div/div[2]/div').text
    except:
        pass
    try:
        phone = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div[5]/div/div/div[2]/div[1]').text
    except:
        pass
    time.sleep(2)
    if link.find('profile.php?') != -1:
        driver.get(link+'&sk=about_contact_and_basic_info')
    else:
        driver.get(link+'/about_contact_and_basic_info')
    try:
        sex = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div[3]/div[2]/div/div/div[2]/div/div/div/div/div[1]/span').text
    except:
        pass
    try:
        birth = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div[3]/div[3]/div/div/div[2]/div/div/div/div/div[1]/span').text
    except:
        pass

    print('+ Họ tên: '+ name)
    print('+ Giới tính: '+ sex)
    print('+ Ngày sinh: '+birth)
    print('+ Công việc: '+work)
    print('+ Từng học tại: '+studied)
    print('+ Quê quán: '+comefrom)
    print('+ Tình trạng: '+status)
    print('+ Số điện thoại: '+phone)

    f = open('B:\PycharmProjects\detai_django\Home\static\images\Facebook_Crawl/'+folder+'/Profile.txt','w',encoding='utf-8')
    f.write(name+'\n'+sex+'\n'+birth+'\n'+work+'\n'+studied+comefrom+'\n'+status+'\n'+phone)
    f.close()

    f = open('B:\PycharmProjects\detai_django\Home\static\images\Facebook_Crawl/'+folder+'/Date_Time.txt','w',encoding='utf-8')
    f.close()
#
# def Crawl_Image_Facebook(link,name,depth,count):
#     driver.get(link)
#     for scroll in range(0,depth):
#         # Scroll down to bottom
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(1)
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
#         # Wait to load page
#         time.sleep(1)
#
#         # Once the full page is loaded, we can start scraping
#     images = driver.find_elements_by_tag_name('img')
#     urls=[]
#     dem = 1
#     for i in images:
#         try:
#             images_link = i.get_attribute('src')
#             if is_valid(images_link) and images_link not in urls:
#                 if (images_link.find('.jpg') or images_link.find('.png')):
#                     print(str(dem),': ',images_link)
#                     dem+=1
#                     urls.append(images_link)
#             # urls.append(images_link)
#             # time.sleep(3)
#             # request.urlretrieve(images_link, './Facebook_Crawl/' + name + '/' + str(i) + '.png')
#         except:
#             print('can not download')
#     luuToanBoAnh(urls, 'Facebook_Crawl/'+name)
#     # '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div[2]/div/div[2]/div[3]/div[2]/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a/span/span/b/b[32]'
#     # for i in range(1,count):
#     #     try:
#     #         image = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div
#     #         /div[4]/div[2]/div/div[2]/div[3]/div['+str(i)+']/div/div/div/div/div/div/div/div/div/div/div[2]/div/div[3]
#     #         /div[2]/div[1]/div/a/div[1]/div/div/div/img')
#     #         image_link = image.get_attribute("src")
#     #         request.urlretrieve(image_link, './Facebook_Crawl/'+name+'/'+str(i)+'.png')
#     #     except:
#     #         pass


def Crawl_Photo_Facebook(link,name,depth,count):
    print('Starting crawl personal image...')
    if link.find('profile.php?') != -1:
        driver.get(link + '&sk=photos_all')
    else:
        driver.get(link + '/photos_all')
    for scroll in range(0,depth):
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        # Wait to load page
        time.sleep(1)

        # Once the full page is loaded, we can start scraping
    images = driver.find_elements_by_tag_name('img')
    urls=[]
    dates=[]
    dem = 1
    for i in images:
        try:
            i.click()
            time.sleep(3)
            image = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[3]/div[2]/div/div[2]/div/div[1]/div/div[2]/div/div/div/img')
            url = image.get_attribute('src')
            print(url)

            date_time = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[3]/div[2]/div/div[3]/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[2]/div/div[2]/span/span/span[2]/span/a/span/span/b').text
            print(date_time)
            if is_valid(url) and url not in urls:
                if (url.find('.jpg') or url.find('.png')):
                    print(str(dem),': ',url)
                    dem += 1
                    urls.append(url)
                    dates.append(date_time)
            escape = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[2]/div[1]/div[1]/span/div')
            escape.click()
            time.sleep(1)
        except:
            print('Lỗi mạng!')
        if dem > count:
            break
    print('Starting download personal image...')
    luuToanBoAnhFace(urls,dates, 'B:\PycharmProjects\detai_django\Home\static\images\Facebook_Crawl/'+name)


def Crawl_Photo_Facebook_Group(link,name,depth,count):

    driver.get(link + '/photos/?ref=page_internal')
    for scroll in range(0,depth):
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        # Wait to load page
        time.sleep(1)

        # Once the full page is loaded, we can start scraping
    images = []
    for i in range(1,count*2):
        try:
            a = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div[3]/div/div/div/div[2]/div['+str(i)+']/div/a/div/div/img')
            images.append(a)
        except:
            print('Không tìm thấy ảnh! Lỗi mạng!')
            pass
    urls=[]
    dates=[]
    dem = 1
    for i in images:
        try:
            i.click()
            time.sleep(3)
            image = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[3]/div[2]/div/div[2]/div/div[1]/div/div[2]/div/div/div/img')
            url = image.get_attribute('src')
            print(url)
            date_time = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[3]/div[2]/div/div[3]/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[2]/div/div[2]/span/span/span[2]/span/a/span/span/b').text
                                                     # '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[3]/div[2]/div/div[3]/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[2]/div/div[2]/span/span/span[2]/span/a/span/span/b/b[43]'
                                                     # '/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[1]/div/div[3]/div[2]/div/div[3]/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[2]/div/div[2]/span/span/span[2]/span/a/span/span/b'
            if is_valid(url) and url not in urls:
                if (url.find('.jpg') or url.find('.png')):
                    print(str(dem),': ',url)
                    dem += 1
                    urls.append(url)
                    dates.append(date_time)
                    # print(date_time)
            escape = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[2]/div[1]/div[1]/span/div')
            escape.click()

        except:
            print('Không thể tải do Lỗi mạng!')
            # driver.execute_script("window.history.go(-1)")
        if dem > count:
            break
    luuToanBoAnhFace(urls,dates, 'B:\PycharmProjects\detai_django\Home\static\images\Facebook_Group/'+name)

#ham kiem tra xem duong link mot trang web cos bi ma hoa hay khong
def is_valid(url):
    #phân tích url thành 6 thành phần chỉ cần kiểm tra tên miền và chương trình có hay không
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def cut_name(link):
    names= link.split('/')
    name = names[len(names)-1]
    name = name.replace('profile.php?','')
    try:
        os.mkdir('B:\PycharmProjects\detai_django\Home\static\images\Facebook_Crawl/'+name)
    except:
        print('Người này đã có trong danh sách !')
    return name

def cut_name_Group(link):
    names= link.split('/')
    name = names[len(names)-1]
    try:
        os.mkdir('B:\PycharmProjects\detai_django\Home\static\images\Facebook_Group/'+name)
    except:
        print('Trang này đã có trong danh sách !')
    return name

def luuToanBoAnhFace(urls,date, pathname):
    ten = 1
    for url in urls:
        luuAnhFace(url,date[ten-1],pathname,ten)
        ten+=1

def luuAnhFace(url,date, pathname,ten):

    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    try:
        response = requests.get(url, stream=True)
        file_size = int(response.headers.get('Content-Length', 0))
        # filename = os.path.join(pathname, url.split('/')[-1])
        filename = os.path.join(pathname,str(ten)+'.png')
        progress = tqdm(response.iter_content(file_size), f"Downloading {filename}", total=file_size, unit="B",
                    unit_scale=True, unit_divisor=1024)
        with open(filename, 'wb') as f:
            for data in progress:
                f.write(data)
                progress.update(len(data))

        f = open(pathname+'/Date_Time.txt','a',encoding='utf-8')
        print(date)
        f.write(str(ten)+'.png\t'+date+'\n')
        f.close()

    except:
        pass

def read_LinkList():
    f = open('B:\PycharmProjects\OCR_project\Facebook_Crawl\list_link.txt','r')
    str = f.read()
    mang = str.split('\n')
    print(mang)
    f.close()
    return mang

def read_ListGroup():
    f = open('B:\PycharmProjects\OCR_project\Facebook_Group/list_group.txt','r')
    str = f.read()
    mang = str.split('\n')
    print(mang)
    f.close()
    return mang

import argparse
if __name__ == '__main__':

    # parser = argparse.ArgumentParser(description='Non API public FB miner')
    #
    # parser.add_argument('-l', '--link', nargs='+',
    #                     dest="link",
    #                     help="link Facebook")
    #
    # parser.add_argument("-d", "--depth", action="store",
    #                     dest="depth", default=2, type=int,
    #                     help="Độ sâu")
    # parser.add_argument("-c", "--count", action="store",
    #                     dest="count", default=20, type=int,
    #                     help="Số lượng ảnh crawl.")
    # parser.add_argument("-u", "--user",
    #                     dest="user", default="0971660673",
    #                     help="Tên đăng nhập")
    # parser.add_argument("-p", "--password",
    #                     dest="password", default="Fb23/11/1999",
    #                     help="Mật khẩu")
    # args = parser.parse_args()
    # if not args.link:
    #     print("Chưa có link!")
    #     print(parser.print_help())
    #     exit()

    list = read_LinkList()
    user = '0971660673'
    password = 'Fb23/11/1999'
    loginFB(user, password)
    time.sleep(1)

    for link in list:
        link = str(link) #'https://www.facebook.com/MTA2017o'
        depth = 2   #args.depth
        count = 20  #args.count
        name = cut_name(link)
        Crawl_Info_Facebook(link,name)
        time.sleep(1)
        Crawl_Photo_Facebook(link,name,depth,count)
        time.sleep(1)
        # Crawl_Image_Facebook(link,name,depth,count)

    # for link in list:
    #     depth = 3   #args.depth
    #     count = 20  #args.count
    #     name = cut_name_Group(link)
    #     Crawl_Photo_Facebook_Group(link,name,depth,count)