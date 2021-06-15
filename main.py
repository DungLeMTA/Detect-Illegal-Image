from PyQt5.QtWidgets import *
import  sys
from  PyQt5 import  QtGui, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import  cv2 as cv
import cv2
import  requests
import  os
from PIL import Image
import  io
from  collections import  OrderedDict
import  array as ar
import  time
from  tqdm import  tqdm
from  bs4 import  BeautifulSoup as bs
from  urllib.parse import urljoin, urlparse
import  numpy as np
import imutils
import time
from imutils.video import VideoStream
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
# import pafy

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

#hàm lưu một ảnh khi đã có link ảnh
def luuAnh(url, pathname):
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    response = requests.get(url, stream=True)
    file_size = int(response.headers.get('Content-Length', 0))
    filename = os.path.join(pathname, url.split('/')[-1])
    print(filename)
    progress = tqdm(response.iter_content(file_size), f"Downloading {filename}", total=file_size, unit="B",
                    unit_scale=True, unit_divisor=1024)
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
            os.remove(filename)
            cv.imwrite(filename, img)

 #ham luu toan bo anh tu mot array cac link anh
def luuToanBoAnh(urls, pathname):
    for url in urls:
        luuAnh(url,pathname)


#ham kiem tra xem duong link mot trang web cos bi ma hoa hay khhong
def is_valid(url):
    #phân tích url thành 6 thành phần chỉ cần kiểm tra tên miền và chương trình có hay không
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


#ham lay tat ca cac link anh ve mot array urls tu linnk web nhat dinh
def layTatCa_URLAnh(url):
    #hàm sẽ trả về array link ảnh trong link web
    soup = bs(requests.get(url).content, 'html.parser')
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

    return  urls


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


#hàm phát hiện đối tượng thông qua yolov3
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
        labe = []
        if len(idxs) > 0:
            for i in idxs.flatten():
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])

                color = [int(c) for c in COLORS[classIDs[i]]]
                cv.rectangle(image, (x, y), (x + w, y + h), color, 2)
                labe.append(LABELS[classIDs[i]])
                text = '{}: {:.2f}'.format(LABELS[classIDs[i]], confidences[i])
                (h, w) = image.shape[:2]
                rong = 0
                if (h >= 1000 or w >= 1000):
                    rong = 4
                else:
                    rong = 2
                cv.putText(image, text, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.56, color, rong)

        return image, labe, thoigian
    else :
        return None, None, None
#
# def phatDoiTuongVideo(labelsPath,configPath,weightsPath, url_video):
#     # url of the video
#     url = "https://www.youtube.com/watch?v=Ns4LCeeOFS4&t=320s"
#     video = pafy.new(url)
#     vs = video.getbestvideo()
#     #url_video='airport.mp4'
#     LABELS = open(labelsPath).read().strip().split("\n")
#
#
#     #radom màu sắc nhận diện đối tượng
#     np.random.seed(42)
#     COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
#         dtype="uint8")
#
#     #load file  trọng số và file config
#
#     net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
#     ln = net.getLayerNames()
#     ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]
#
#     #load file video
#     #vs = cv2.VideoCapture(url_video)
#     writer = None
#     (W, H) = (None, None)
#
#
#     #xác định tổng số frames trong file video
#     try:
#         prop = cv2.cv.CV_CAP_PROP_FRAME_COUNT if imutils.is_cv2() \
#             else cv2.CAP_PROP_FRAME_COUNT
#         total = int(vs.get(prop))
#         print("[INFO] {} total frames in video".format(total))
#
#     #khi xảy ra lỗi trong khi tính số lượng frame trong file video
#     except:
#         print("[INFO] could not determine # of frames in video")
#         print("[INFO] no approx. completion time can be provided")
#         total = -1
#
#     #vòng lặp qua các frame trong video
#     while True:
#     # đọc frame tiếp theo từ fille
#         (grabbed, frame) = vs.read()
#
#         # nếu hết khung hình trong video thì kết thúc vòng lặp
#         if not grabbed:
#             break
#
#         # nếu khung hình không có W, H thì kiểm tra
#         if W is None or H is None:
#             (H, W) = frame.shape[:2]
#
#
#     #xây dựng 1 blob từ input frame và sau đó thực hiện chuyển đổi
#     #phát hiện đối tượng, vẽ box và tính xác xuất tương ứng
#         blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
#             swapRB=True, crop=False)
#         net.setInput(blob)
#         start = time.time()
#         layerOutputs = net.forward(ln)
#         end = time.time()
#
#     # Khởi tạo danh sách danh sách box phát hiện đối tượng, confidences, và class IDs tương ứng
#         boxes = []
#         confidences = []
#         classIDs = []
#
#     #Lặp qua từng  layer đầu ra
#         for output in layerOutputs:
#         # lặp qua mỗi đối tượng phát hiện
#             for detection in output:
#             # trích xuất Class Id và confidenc của từng đối tượng
#                 scores = detection[5:]
#                 classID = np.argmax(scores)
#                 confidence = scores[classID]
#
#             # lọc loại bỏ những đối tượng có confidence <=0.5
#                 if confidence >= 0.5:
#
#                     box = detection[0:4] * np.array([W, H, W, H])
#                     (centerX, centerY, width, height) = box.astype("int")
#
#                     x = int(centerX - (width / 2))
#                     y = int(centerY - (height / 2))
#
#                     boxes.append([x, y, int(width), int(height)])
#                     confidences.append(float(confidence))
#                     classIDs.append(classID)
#
#
#         idxs = cv2.dnn.NMSBoxes(boxes, confidences,0.5,
#             0.2)
#
#         if len(idxs) > 0:
#
#             for i in idxs.flatten():
#
#                 (x, y) = (boxes[i][0], boxes[i][1])
#                 (w, h) = (boxes[i][2], boxes[i][3])
#
#                 color = [int(c) for c in COLORS[classIDs[i]]]
#                 cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
#                 text = "{}: {:.4f}".format(LABELS[classIDs[i]],
#                     confidences[i])
#                 cv2.putText(frame, text, (x, y - 5),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
#
#
#         if writer is None:
#         #khỏi tạo video đk viết vô
#             fourcc = cv2.VideoWriter_fourcc(*"MJPG")
#             writer = cv2.VideoWriter("output.avi", fourcc, 30,
#                 (frame.shape[1], frame.shape[0]), True)
#
#         # some information on processing single frame
#             if total > 0:
#                 elap = (end - start)
#                 print("[INFO] single frame took {:.4f} seconds".format(elap))
#                 print("[INFO] estimated total time to finish: {:.4f}".format(
#                     elap * total))
#
#     # write the output frame to disk
#         writer.write(frame)

def phatHienDoiTuongCamera():
    labelsPath  = 'coco.names'
    configPath = 'yolov3.cfg'
    weightsPath = 'yolov3-tiny_obj_33000.weights'

#load file chứa labels
    LABELS = open(labelsPath).read().strip().split("\n")


#radom màu sắc nhận diện đối tượng
    np.random.seed(42)
    COLORS = np.random.randint(0, 255, size=(len(LABELS), 3),
    dtype="uint8")

#load file  trọng số và file config 

    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

#khỏi tạo  video stream và cho phép camera khỏi động
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()

    time.sleep(2.0)

#lặp qua các frame từ video stream
    while True:
    #lấy khung hình từ ideo phân luồng và
    #đưa kích thước có chiều rộng tối đa là 400 pixels
        frame = vs.read()
        frame = imutils.resize(frame,width=400)

    #lấy chiều của frame và chuyển nó thành 1 điểm (blob)
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
            swapRB=True, crop=False)\
 
    #vượt qua-----
        net.setInput(blob)
        layerOutputs = net.forward(ln) 

    # Khởi tạo danh sách danh sách box phát hiện đối tượng, confidences, và class IDs tương ứng
        boxes = []
        confidences = []
        classIDs = []
    #lặp qua các đối tượng phát hiện
        for output in layerOutputs: 
        #trích xuất Class ID và cònidence của từng đối tượng
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
            # lọc các đối tượng nhận dạng yếu có điển confidence<0.5
                if confidence < 0.5:
                    continue

                box = detection[0:4] * np.array([w, h, w, h])
            # tính toán toạ độ x,y để vẽ đường biên cho đối tượng
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

        idxs = cv2.dnn.NMSBoxes(boxes, confidences,0.5,
            0.2)

        if len(idxs) > 0:
            for i in idxs.flatten():
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                color = [int(c) for c in COLORS[classIDs[i]]]
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                text = "{}: {:.4f}".format(LABELS[classIDs[i]],
                    confidences[i])
                cv2.putText(frame, text, (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    vs.stop()

# tạo chương trình
class MyWinDown(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Phần mềm nhận diện đối tượng trái phép trong ảnh'
        self.top = 0
        self.left = 0
        self.height = 1102
        self.width = 1942
        self.InitWinDow()

    #khoi tao cua so windown va cac thanh phan tren cua so
    def InitWinDow(self):
        self.setWindowIcon(QtGui.QIcon('logoMTA.jpg'))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top,self.left,self.width,self.height)
        self.Input()
        self.Output()

        self.show()

    def Input(self):

        gbInput = QGroupBox('INPUT', self)
        gbInput.setGeometry(6, 20, 1900, 250)
        gbInput.setFont(QtGui.QFont('Sanerof', 17))
        gbInput.setStyleSheet('color: blue')


        lbTenTruyVan = QLabel('GG Search API : ',gbInput)
        lbTenTruyVan.setGeometry(10,50,145,30)
        lbTenTruyVan.setFont(QFont('Sanerof',12))
        lbTenTruyVan.setStyleSheet('color: darkviolet')

        lbSLTruyVan = QLabel('Amount: ', gbInput)
        lbSLTruyVan.setGeometry(750, 50, 80, 30)
        lbSLTruyVan.setFont(QFont('Sanerof', 12))
        lbSLTruyVan.setStyleSheet('color: darkviolet')

        lbLinkWeb = QLabel('Link Website: ', gbInput)
        lbLinkWeb.setGeometry(10, 100, 140, 30)
        lbLinkWeb.setFont(QFont('Sanerof', 12))
        lbLinkWeb.setStyleSheet('color: darkviolet')

        lbLinkAnh = QLabel('Link image: ', gbInput)
        lbLinkAnh.setGeometry(10, 150, 140, 30)
        lbLinkAnh.setFont(QFont('Sanerof', 12))
        lbLinkAnh.setStyleSheet('color: darkviolet')

        self.tbTenTruyVan = QLineEdit(gbInput)
        self.tbTenTruyVan.setGeometry(180,50,500,30)
        self.tbTenTruyVan.setFont(QFont('Sanerof',10))

        self.tbSLTruyVan = QLineEdit(gbInput)
        self.tbSLTruyVan.setGeometry(850, 50, 100, 30)
        self.tbSLTruyVan.setFont(QFont('Sanerof', 10))

        self.tbLinkWeb = QLineEdit(gbInput)
        self.tbLinkWeb.setGeometry(180, 100, 500, 30)
        self.tbLinkWeb.setFont(QFont('Sanerof', 10))

        self.tbLinkAnh = QLineEdit(gbInput)
        self.tbLinkAnh.setGeometry(180, 150, 500, 30)
        self.tbLinkAnh.setFont(QFont('Sanerof', 10))

        self.btnStart = QPushButton('Start',gbInput)
        self.btnStart.setGeometry(1400,50,100,70)
        self.btnStart.setFont(QFont('Sanerof',13))
        self.btnStart.setStyleSheet('background-color: greenyellow')
        self.btnStart.clicked.connect(self.Click_Start)

        self.btnClear = QPushButton('Clear', gbInput)
        self.btnClear.setGeometry(1600, 50, 100, 70)
        self.btnClear.setFont(QFont('Sanerof', 13))
        self.btnClear.setStyleSheet('background-color: greenyellow')
        self.btnClear.clicked.connect(self.Click_Clear)

        self.btnFolder = QPushButton('Folder', gbInput)
        self.btnFolder.setGeometry(1400, 150, 100, 70)
        self.btnFolder.setFont(QFont('Sanerof', 13))
        self.btnFolder.setStyleSheet('background-color: greenyellow')
        self.btnFolder.clicked.connect(self.Click_folder)

        self.btnImage = QPushButton('Image', gbInput)
        self.btnImage.setGeometry(1600, 150, 100, 70)
        self.btnImage.setFont(QFont('Sanerof', 13))
        self.btnImage.setStyleSheet('background-color: greenyellow')
        self.btnImage.clicked.connect(self.Click_Image)

        self.btnVideo = QPushButton('Video',gbInput)
        self.btnVideo.setGeometry(1800,50,100,70)
        self.btnVideo.setFont(QFont('Sanerof',13))
        self.btnVideo.setStyleSheet('background-color: greenyellow')
        self.btnVideo.clicked.connect(self.Click_Video)

        self.btnCam = QPushButton('Camera',gbInput)
        self.btnCam.setGeometry(1800,150,100,70)
        self.btnCam.setFont(QFont('Sanerof',13))
        self.btnCam.setStyleSheet('background-color: greenyellow')
        self.btnCam.clicked.connect(self.Click_Camera)

    def Output(self):
        gbOutput = QGroupBox('OUTPUT', self)
        gbOutput.setGeometry(6, 300, 1900, 680)
        gbOutput.setFont(QtGui.QFont('Sanerof', 17))
        gbOutput.setStyleSheet('color: red')

        self.VLayout = QVBoxLayout()
        self.widget = QWidget()
        self.widget.setLayout(self.VLayout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.widget)

        HLayout = QHBoxLayout()
        HLayout.addWidget(scroll)
        gbOutput.setLayout(HLayout)
       # self.DanhSachAnh('E:\Anh')

    def Anh(self, path_img):
        image, labels, time = phatHienDoituong(path_img, 'coco.names', 'yolov3-tiny_obj_33000.weights',
                                               'yolov3.cfg')
        if type(image) is not np.ndarray and labels ==None and time == None: pass
        else:
            url_detection = 'detection.jpg'
            cv.imwrite(url_detection, image)

            # bước phát hiện xem ảnh có chứa đối tượng nào:

            groupbox = QGroupBox('Ảnh ')
            groupbox.setStyleSheet('color: red')
            groupbox.setFont(QFont('Sanerof', 10))

            gridLayout = QGridLayout()

            labelInput = QLabel()
            labelInput.setPixmap(QPixmap(path_img))
            self.lbCheck = QLabel()
            labelOutput = QLabel()
            labelOutput.setPixmap(QPixmap(url_detection))
            self.gbResult = QGroupBox('Result')
            self.gbResult.setFont(QFont('Sanerof', 15))
            self.gbResult.setStyleSheet('color: blue')

            self.hienKetQua(image, labels, time)

            gridLayout.addWidget(labelInput, 0, 0)
            gridLayout.addWidget(labelOutput, 0, 1)
            gridLayout.addWidget(self.gbResult, 1, 0)
            gridLayout.addWidget(self.lbCheck, 1, 1)

            groupbox.setLayout(gridLayout)
            self.VLayout.addWidget(groupbox)

    def DanhSachAnh(self, path_file):
        print(path_file)
        i = 1
        for url in os.listdir(path_file):
            if url.endswith('.jpg') or url.endswith('.png') or url.endswith('.JPG') or url.endswith('.PNG') or url.endswith('JPEG') or url.endswith('.jpeg'):
                path_img = os.path.join(path_file, url)
                print(path_img)
                # bước phát hiện đối tượng
                image, labels, time = phatHienDoituong(path_img, 'coco.names', 'yolov3-tiny_obj_33000.weights',
                                                       'yolov3.cfg')
                if type(image) is not np.ndarray and labels == None and time == None: pass
                else:
                    url_detection = 'detection' + str(i) + '.jpg'
                    path_img_detection = os.path.join(path_file, url_detection)
                    cv.imwrite(path_img_detection, image)

                    # bước phát hiện xem ảnh có chứa đối tượng nào:

                    groupbox = QGroupBox('Ảnh ' + str(i))
                    groupbox.setStyleSheet('color: red')
                    groupbox.setFont(QFont('Sanerof', 10))

                    gridLayout = QGridLayout()

                    labelInput = QLabel()
                    labelInput.setPixmap(QPixmap(path_img))
                    self.lbCheck = QLabel()

                    labelOutput = QLabel()
                    labelOutput.setPixmap(QPixmap(path_img_detection))
                    self.gbResult = QGroupBox('Result')
                    self.gbResult.setFont(QFont('Sanerof', 15))
                    self.gbResult.setStyleSheet('color: blue')

                    self.hienKetQua(image, labels, time)

                    gridLayout.addWidget(labelInput, 0, 0)
                    gridLayout.addWidget(labelOutput, 0, 1)
                    gridLayout.addWidget(self.gbResult, 1, 0)
                    gridLayout.addWidget(self.lbCheck, 1, 1)

                    groupbox.setLayout(gridLayout)
                    self.VLayout.addWidget(groupbox)
                    i += 1
            else :
                continue



    def hienKetQua(self, image, label, time):
        #khỏi tạo các label chứa đối tượng
        lbPixel = QLabel('Pixel:')
        lbPixel.setFont(QFont('Sanerof',15))
        lbTime = QLabel('Time :')
        lbTime.setFont(QFont('Sanerof',15))

        lbCacDoiTuong = QLabel('Các đối tượng :')
        lbCacDoiTuong.setFont(QFont('Sanerof',15))

        lbkq = QLabel('Kết quả : ')
        lbkq.setFont(QFont('Sanerof',15))
        lbkq.setStyleSheet('color: red')

        griblayout = QGridLayout()
        griblayout.addWidget(lbPixel,0,0)
        griblayout.addWidget(lbkq,3,0)
        griblayout.addWidget(lbTime,1,0)
        griblayout.addWidget(lbCacDoiTuong,2,0)
        self.gbResult.setLayout(griblayout)

        #hiển thị kết quả lên các label
        arraylabel = list(OrderedDict.fromkeys(label))
        HocVien = ['Người', 'Cầu vai học viên', 'Tiết']
        HocVien1 = ['Người', 'Cầu vai học viên']
        SiQuan = ['Người', 'Cầu vai sĩ quan', 'Tiết']
        SiQuan1 = ['Người', 'Cầu vai sĩ quan']
        QuanNhan = ['Người','Tiết']
        TenLua = ['Tên lửa']
        SungAK = ['Súng AK']
        lb = []
        time = round(time, 5)
        time = "Time :    " + str(time) + ' seconds'
        lbTime.setText(time)
        label = list(dict.fromkeys(label))
        print(label)

        #tìm pixel của ảnh
        (w, h) = image.shape[:2]
        #cv.imwrite('output.jpg', image)
        pixel = 'Pixel :   '+str(w) + ' x ' + str(h)
        lbPixel.setText(pixel)

        for  i in range(0,len(arraylabel)):
            if(label[i]=='nguoi'):
                lb.append('Người')
            if (label[i] =='tiet'):
                lb.append( 'Tiết')
            if (label[i]== 'cauvaiHV'):
                lb.append('Cầu vai học viên')
            if (label[i]=='cauvaiSQ'):
                lb.append('Cầu vai sĩ quan')
            if(label[i]== 'tenlua'):
                lb.append('Tên lửa')
            if (label[i]=='sungAK'):
                lb.append('Súng AK')
        lb = list(dict.fromkeys(lb))
        print(lb)
        str_label = ' , '.join(lb)
        string = 'Các đối tượng phát hiện:  ' + str_label
        lbCacDoiTuong.setText(string)
        doituong = ['(Ảnh có học viên)','(Ảnh có sĩ quan)','(Ảnh có tên lửa)','(Ảnh có súng AK)','(Ảnh có quân nhân)']
        dt = []
        if ktraDoiTuong(lb, HocVien) == 1:
            #self.lbKetQua.setText('(Ảnh có học viên)')
            dt.append(doituong[0])
        elif ktraDoiTuong(lb, SiQuan) == 1:
            #self.lbKetQua.setText('(Ảnh sĩ quan)')
            dt.append(doituong[1])
        elif ktraDoiTuong(lb,QuanNhan) ==1:
            dt.append(doituong[4])
        if ktraDoiTuong(lb, TenLua) == 1:
            #self.lbKetQua.setText('(Ảnh tên lửa)')
            dt.append(doituong[2])
        if ktraDoiTuong(lb, SungAK) == 1:
           # self.lbKetQua.setText('(Ảnh súng AK)')
            dt.append(doituong[3])
        if ktraDoiTuong(lb,HocVien1)==1:
            dt.append(doituong[0])
        if ktraDoiTuong(lb,SiQuan1) == 1:
            dt.append(doituong[1])

        dt = list(dict.fromkeys(dt))
        if len(dt) > 0:
            self.lbCheck.setPixmap(QPixmap('false.png'))
        else:
            self.lbCheck.setPixmap(QPixmap('true.png'))

        dt = '\n'.join(dt)
        print(dt)
        lbkq.setText(dt)

    def Click_Start(self):
        if (self.tbTenTruyVan.text()!='' and self.tbLinkAnh.text()=='' and self.tbLinkWeb.text()==''):
            urls = URL_API_Anh(self.tbTenTruyVan.text(), self.tbSLTruyVan.text())
            luuToanBoAnh(urls,'Image_API')
            self.DanhSachAnh('Image_API')

        elif (self.tbTenTruyVan.text()=='' and self.tbLinkAnh.text() !='' and self.tbLinkWeb.text()==''):
            luuAnh(self.tbLinkAnh.text(),'Image_link')
            self.DanhSachAnh('Image_link')

        elif (self.tbTenTruyVan.text()=='' and self.tbLinkAnh.text()=='' and self.tbLinkWeb.text()!=''):
            urls = layTatCa_URLAnh(self.tbLinkWeb.text())
            luuToanBoAnh(urls,'Image_Web')
            self.DanhSachAnh('Image_Web')

    def Click_Clear(self):
        for url in os.listdir('Image_API'):
            path = os.path.join('Image_API',url)
            os.remove(path)

        for url in os.listdir('Image_link'):
            path = os.path.join('Image_link',url)
            os.remove(path)

        for url in os.listdir('Image_Web'):
            path = os.path.join('Image_Web',url)
            os.remove(path)
        self.close()
        self.__init__()

    def Click_Image(self):
        fname = QFileDialog.getOpenFileName(self,'Open File','c:\\','Image Files(*jpg *png)')
        imgpath = fname[0]
        if imgpath!='':
             self.Anh(imgpath)
        else:
            pass

    def Click_folder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if file !='':
            self.DanhSachAnh(file)
        else:
            pass
        print(file)

    # def Click_Video(self):
        #fname = QFileDialog.getOpenFileName(self,'Open File','c:\\','Video File(*mp4)')
       # imgpath = fname[0]
       # if(imgpath!=''):
       #  phatDoiTuongVideo('coco.names','yolov3.cfg','yolov3-tiny_obj_33000.weights','airport.mp4')
       
       # else:
         #   pass

    def Click_Camera(self):
        phatHienDoiTuongCamera()

if __name__ == "__main__" :

    App = QApplication(sys.argv)
    win = MyWinDown()
    # win = Window()
    sys.exit(App.exec())












