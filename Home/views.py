from collections import OrderedDict
import imutils
from PyQt5.QtWidgets import QFileDialog
from django.shortcuts import render
import  cv2 as cv
import  numpy as np
import time
import os
from  tqdm import  tqdm
from  bs4 import  BeautifulSoup as bs
from  urllib.parse import urljoin, urlparse
import  requests as rq
import  requests
from . import Facebook_Crawl
from . import DNSdumpster_Selenium2
# Create your views here.
link = ''
dem = 1
user = '0971660673'
password = 'Fbb23111999'
Facebook_Crawl.loginFB(user, password)
time.sleep(1)
class Result:
    input_image = ''
    output_image = ''
    labels = []
    time = 0
    result = ''
    true=''

def hienThiKetQua(o,labels):
    i = False
    print(labels)
    if 'nguoi' and 'tiet' in labels:
        i = True
        o.result += 'Ảnh có quân nhân, '
    if  'nguoi' and 'cauvaiSQ' and 'tiet' in labels:
        o.result += 'Ảnh có Sĩ quan quân đội, '
        i = True
    if 'tenlua' in labels:
        i = True
        o.result += 'Ảnh có tên lửa, '
    if 'sungAK' in labels:
        i = True
        o.result += 'Ảnh có súng AK, '
    if 'nguoi' and 'cauvaiHV' and 'tiet' in labels:
        i = True
        o.result += 'Ảnh có Học viên quân đội, '

    if i:
        o.true = "images/false.png"
    else:
        o.true = "images/true.png"
        if 'nguoi' in labels:
            o.result += 'Người, '
        if 'cauvaiSQ' in labels:
            o.result += 'Cầu vai sĩ quan, '
        if 'cauvaiHV' in labels:
            o.result += 'Cầu vai học viên, '


    return o

def home(request):
    return render(request,'pages/index.html')

def IP_DNS(request):
    global link
    url = DNSdumpster_Selenium2.cut_link(link)
    A = DNSdumpster_Selenium2.Crawl_Data_DNSdumpster(url)
    content = {
        'URL':A.link,
        'DNS': A.dns_servers,
        'MX': A.mx_records,
        'TXT':A.txt_records,
        'HOST':A.host_records,
        'MAP':A.mapping,
    }
    return render(request,'pages/app.html',content)

def Process_Link(request):
    global link
    link = request.POST["link"]
    choose = request.POST["choose"]
    # print(choose,type(choose))
    # xử lí 1 ảnh
    if choose == "1":
        luuAnh(link, 'B:\PycharmProjects\detai_django\Home\static\images\Image_link',1)
        output = DanhSachAnh('B:\PycharmProjects\detai_django\Home\static\images\Image_link')

        # print(output[0].labels)
        i=0
        for o in output:
            try:
                o = hienThiKetQua(o, o.labels[i])
            except:
                o.true = "images/true.png"
                pass

            i += 1
    elif choose == "2":
        # xử lí 1 trang web
        urls = layTatCa_URLAnh(link)
        luuToanBoAnh(urls, 'B:\PycharmProjects\detai_django\Home\static\images\Image_Web')
        output = DanhSachAnh('B:\PycharmProjects\detai_django\Home\static\images\Image_Web')
        i = 0
        for o in output:
            try:
                o = hienThiKetQua(o, o.labels[i])
            except:
                o.true = "images/true.png"
                pass

            i += 1

    elif choose == "3":
        urls = URL_API_Anh(link, 5)
        luuToanBoAnh(urls, 'B:\PycharmProjects\detai_django\Home\static\images\Image_API')
        output = DanhSachAnh('B:\PycharmProjects\detai_django\Home\static\images\Image_API')
        i = 0
        for o in output:
            try:
                o = hienThiKetQua(o, o.labels[i])
            except:
                o.true = "images/true.png"
                pass

            i += 1

    elif choose == "4":
        # 'https://www.facebook.com/MTA2017o'
        depth = 2  # args.depth
        count = 10  # args.count
        name = Facebook_Crawl.cut_name(link)
        Facebook_Crawl.Crawl_Info_Facebook(link, name)
        time.sleep(1)
        Facebook_Crawl.Crawl_Photo_Facebook(link, name, depth, count)
        time.sleep(1)
        output = DanhSachAnh('B:\PycharmProjects\detai_django\Home\static\images\Facebook_Crawl\\'+name)
        i=0
        for o in output:
            try:
                o = hienThiKetQua(o, o.labels[i])
            except:
                o.true = "images/true.png"
                pass

            i += 1
    elif choose == "5":
        depth = 2   #args.depth
        count = 10  #args.count
        name = Facebook_Crawl.cut_name_Group(link)
        Facebook_Crawl.Crawl_Photo_Facebook_Group(link,name,depth,count)
        output = DanhSachAnh('B:\PycharmProjects\detai_django\Home\static\images\Facebook_Group\\' + name)
        i=0
        for o in output:
            try:
                o = hienThiKetQua(o, o.labels[i])
            except:
                print('Lỗi ảnh')
                o.true = "images/true.png"
                pass
            i += 1

    content = {
        'content': output,
            # 'input_image': output[len(output)-1].input_image,
            # 'output_image':output[len(output)-1].output_image,
            # 'labels':      output[len(output)-1].labels,
            # 'time':        output[len(output)-1].time,
    }
    # print(output[0].input_image)
    return render(request,'pages/process.html',content)

def phatHienDoituong (path_image, path_labels, path_weights, path_config):
    img = cv.imread(path_image)
    if type(img) is np.ndarray:
        # đọc các nhãn đưa vào array LABELS
        LABELS = open(path_labels).read().strip().split('\n')
        print(LABELS)

        # random màu sắc gán cho các nhãn
        np.random.seed(42)
        COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype='uint8')

        # đọc dữ liệu trong file .cfg và .weights
        net = cv.dnn.readNetFromDarknet(path_config, path_weights)

        # đọc ảnh
        #img = cv.imread(path_image)
        (height, width) = img.shape[:2]

        image = img.copy()

        ln = net.getLayerNames()
        ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

        blob = cv.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)

        net.setInput(blob)
        start = time.time()
        layetOutputs = net.forward(ln)
        end = time.time()
        thoigian = (end - start)
        boxes = []
        confidences = []
        classIDs = []

        for output in layetOutputs:

            for detection in output:
                scores = detection[5:]

                classID = np.argmax(scores)

                confidence = scores[classID]

                if confidence > 0.1:
                    box = detection[0:4] * np.array([width, height, width, height])
                    print(detection[4])
                    print(classID)

                    (centerX, centerY, W, H) = box.astype('int')

                    x = int(centerX - (W / 2))
                    y = int(centerY - (H / 2))

                    boxes.append([x, y, int(W), int(H)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        idxs = cv.dnn.NMSBoxes(boxes, confidences, 0.1, 0.25)
        label = []
        if len(idxs) > 0:
            for i in idxs.flatten():
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])

                color = [int(c) for c in COLORS[classIDs[i]]]
                cv.rectangle(image, (x, y), (x + w, y + h), color, 2)
                label.append(LABELS[classIDs[i]])
                text = '{}: {:.2f}'.format(LABELS[classIDs[i]], confidences[i])
                (h, w) = image.shape[:2]
                rong = 0
                if (h >= 1000 or w >= 1000):
                    rong = 4
                else:
                    rong = 2
                cv.putText(image, text, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.56, color, rong)

        return image, label, thoigian
    else :
        return None, None, None


#ham lay tat ca cac link anh ve mot array urls tu linnk web nhat dinh
def layTatCa_URLAnh(url):
    #hàm sẽ trả về array link ảnh trong link web
    try:
        soup = bs(requests.get(url).content, 'html.parser')
    except:
        print('trang web không tồn tại')
        return
    urls  = []
    for img in tqdm(soup.find_all('img'), 'Extracting images'):
        img_url = img.attrs.get('src')
        print(img_url)
        if not img_url:
            continue
        img_url = urljoin(url,img_url)
        try:
            pos = img_url.index('?')
            img_url = img_url[:pos]
        except ValueError:
            pass
        if is_valid(img_url):
            if (img_url.find('.jpg') or img_url.find('.png')):
                urls.append(img_url)

    return urls



#ham luu toan bo anh tu mot array cac link anh
def luuToanBoAnh(urls, pathname):
    dem = 0
    for url in urls:
        dem+=1
        try:
            luuAnh(url,pathname,dem)
        except:
            pass

#hàm lưu một ảnh khi đã có link ảnh
def luuAnh(url, pathname,dem):
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    response = rq.get(url, stream=True)
    file_size = int(response.headers.get('Content-Length', 0))
    # filename = os.path.join(pathname, url.split('/')[-1])
    filename = os.path.join(pathname,str(dem)+'.jpg')
    # print(filename)

    try:
        progress = tqdm(response.iter_content(file_size), f"Downloading {filename}", total=file_size, unit="B",
                    unit_scale=True, unit_divisor=1024)
    except:
        print('Lỗi mạng')
    with open(filename, 'wb') as f:
        for data in progress:
            f.write(data)
            progress.update(len(data))
    if filename.endswith('.jpg') or filename.endswith('.png'):
        img = cv.imread(filename)
        if type(img) is not np.ndarray:
            pass
        else:
            (w, h) = img.shape[:2]
            if h > 600 or w > 900:
                dim = (900, 600)
                img = cv.resize(img, dim)
            try:
                os.remove(filename)
                cv.imwrite(filename, img)
            except:
                print(str(dem))

def DanhSachAnh(path_file):

    result =[]

    print(path_file)
    i=1
    for url in os.listdir(path_file):
        r = Result()
        if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.JPG') or url.endswith('.PNG') or url.endswith('JPEG') or url.endswith('.jpeg'):
            path_img = os.path.join(path_file, url)
            print(path_img)
            r.input_image=path_img.replace('B:\PycharmProjects\detai_django\Home\static\\','')
            r.input_image=r.input_image.replace('\\','/')
            # bước phát hiện đối tượng
            img, lb, t = phatHienDoituong(path_img, 'B:\PycharmProjects\detai_django\Home\coco.names',
                                            'B:\PycharmProjects\detai_django\Home\yolov3-tiny_obj_33000.weights',
                                            'B:\PycharmProjects\detai_django\Home\yolov3.cfg')
            r.labels.append(lb)
            r.time = t

            if type(img) is not np.ndarray and r.labels == None and time == None: pass
            else:
                url_detection = 'detection_' + str(i) + '.jpg'
                path_img_detection = os.path.join(path_file, url_detection)
                r.output_image = path_img_detection.replace('B:\PycharmProjects\detai_django\Home\static\\','')
                r.output_image = r.output_image.replace('\\','/')
                print(r.output_image)
                try:
                    cv.imwrite(path_img_detection, img)
                except:
                    os.remove(path_img_detection.replace('detection_',''))
                    pass
                i+=1
        else:
            continue

        result.append(r)
    return result

#ham kiem tra xem duong link mot trang web cos bi ma hoa hay khhong
def is_valid(url):
    #phân tích url thành 6 thành phần chỉ cần kiểm tra tên miền và chương trình có hay không
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


#ham kiem tra co phai doi tuong can phat hien
def ktraDoiTuong(labels, object):
    dem = 0
    for i in range(0, len(labels)):
        for j in range(0, len(object)):
            if labels[i] == object[j]:
                dem = dem + 1

    if (dem == len(object)):
        return 1
    else:
        return 0


#ham thu thập tất cả các link ảnh về dùng truy vấn thông qua tên và số lượng ảnh
def URL_API_Anh(ten, soluong):
    r = requests.get("https://api.qwant.com/api/search/images",
                     params={
                         'count': soluong,
                         'q': ten,
                         't': 'images',
                         'safesearch': 1,
                         'locale': 'en_US',
                         'uiv': 4
                     },
                     headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
                     }
                     )

    response = r.json().get('data').get('result').get('items')
    urls = [r.get('media') for r in response]
    return urls