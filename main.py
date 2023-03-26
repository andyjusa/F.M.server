import eventlet
import socketio
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import urllib3
import json

con = sqlite3.connect("./userData.db")
c = con.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS userdata
             (id INT PRIMARY KEY, name TEXT UNIQUE,psw TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS mealDatas(date INT,type INT,data TEXT,CALINFO INT)''')
sender = "andyjung1129@naver.com"

def sendNum(receiver,num):
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = "인증"
    body = "인증번호 : "+str(num)
    message.attach(MIMEText(body, 'plain'))
    smtp_server = "smtp.naver.com"
    smtp_port = 587
    smtp_session = smtplib.SMTP(smtp_server, smtp_port)
    smtp_session.starttls()
    smtp_session.login(sender, "spdlqj6428*")
    smtp_session.sendmail(sender, receiver, message.as_string())
    smtp_session.quit()
    

schedule = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[0,1,2,3,4,5,
             6,0,0,0,0,0,
             7,0,0,0,0,0,
             8,0,0,0,0,0,
             9,0,0,0,0,0,
             10,0,0,0,0,0,
             11,0,0,0,0,0,
             12,0,0,0,0,0],[],[],[0,1,2,3,4,5
                   ,6 ,13 ,15 ,120,120,20
                   ,7 ,122,21 ,121,122,20
                   ,8 ,14 ,122,22 ,21 ,121
                   ,9 ,15 ,22 ,19 ,121,15
                   ,10,21 ,23 ,13 ,17 ,120
                   ,11,121,17 ,13 ,14 ,122
                   ,12,23 ,120,0  ,15 ,21]]

def user_exists(name,id):
    c.execute("SELECT * FROM userData WHERE name=?", (name,))
    if c.fetchone():
        return 0
    else:
        c.execute("SELECT * FROM userData WHERE id=?", (id,))
        if c.fetchone():
            return 1
        return 2

testNum = {"23ms2322":8989,"mstr99@h.jne.go.kr":9090}

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)
@sio.on('connect')
def connect(sid, environ):
    print(f'Connected: {sid}')
    sio.emit("errored",1)

@sio.on('email')
def emailTest(sid,data):
    sio.emit("errored",0)
    testNum[data] = random.randint(1000,9999)
    sendNum(data,testNum[data])
    print(data)

@sio.on('login')
def login(sid,data):
    c.execute("SELECT * FROM userData WHERE name=? AND psw=?",(data[0],data[1]))
    result = c.fetchone()
    if result:
        print(('suceed',result[0],data[0]))
        sio.emit('logined',('suceed',result[0],data[0]))
    else:
        sio.emit("errored",2)

@sio.on('register')
def register(sid,data):
    # and not :
    try:
        if data[1]!=testNum[data[0]]:
            sio.emit("errored",3)
            return
        if data[0][:4]=="mstr":
            # result_of_exist = user_exists(data[2],int(data[0][4:6]))
            Id = int(data[0][4:6])
        else:
            Id = int(data[0][4:8])
        result_of_exist = user_exists(data[2],Id)
        if result_of_exist == 0:
            sio.emit("errored",4)
            return
        if result_of_exist == 1:
            sio.emit("errored",5)
            return
        c.execute("INSERT INTO userData VALUES(?,?,?)",(Id,data[2],data[3]))
        con.commit()
        sio.emit("errored",6)
    except KeyError:
        sio.emit('errored',7)

@sio.on('getSchedule')
def getSchedule(sid,data):
    print(data)
    byte_data = bytes(schedule[data])
    sio.emit('schedule', byte_data)

@sio.on('disconnect')
def disconnect(sid):
    print(f'Disconnected: {sid}')

@sio.on('getMeal')
def getMeal(sid,data):
    try:
        print(data)
        c.execute("SELECT * FROM mealDatas WHERE date=? AND type=?",(int(data[0]),int(data[1])))
        result = c.fetchone()
        print(result)
        if result:
            pass
        else:
                url =f'https://open.neis.go.kr/hub/mealServiceDietInfo?KEY=6ca5b28b85f4407fbaea34cce67a398e&Type=json&pIndex=1&pSize=100&ATPT_OFCDC_SC_CODE=Q10&SD_SCHUL_CODE=8490320&MMEAL_SC_CODE={data[1]}&MLSV_YMD={data[0]}'
                http_pool = urllib3.connection_from_url(url)
                r = http_pool.urlopen('GET',url)
                da = json.loads(r.data.decode('utf-8'))
                # print(json.loads("""{"mealServiceDietInfo":[{"head":[{"list_total_count":1},{"RESULT":{"CODE":"INFO-000","MESSAGE":"정상 처리되었습니다."}}]},{"row":[{"ATPT_OFCDC_SC_CODE":"Q10","ATPT_OFCDC_SC_NM":"전라남도교육청","SD_SCHUL_CODE":"8490320","SCHUL_NM":"매성고등학교","MMEAL_SC_CODE":"2","MMEAL_SC_NM":"중식","MLSV_YMD":"20220302","MLSV_FGR":"967","DDISH_NM":"기장쌀밥 쇠고기미역국13.16. 시금치나물 야채달걀말이1.5.6.13. 새우까스/소스1.2.5.6.9.13.16.18. 배추김치19.13. 목장요구르트2.","ORPLC_INFO":"쌀 : 국내산 김치류 : 국내산 고춧가루(김치류) : 국내산 쇠고기(종류) : 국내산(한우) 돼지고기 : 국내산 닭고기 : 국내산 오리고기 : 국내산 쇠고기 식육가공품 : 국내산 돼지고기 식육가공품 : 국내산 닭고기 식육가공품 : 국내산 오리고기 가공품 : 국내산 낙지 : 국내산 고등어 : 국내산 갈치 : 국내산 오징어 : 국내산 꽃게 : 국내산 참조기 : 국내산 두부 : 국내산 콩 : 국내산","CAL_INFO":"780.3 Kcal","NTR_INFO":"탄수화물(g) : 109.0 단백질(g) : 34.7 지방(g) : 23.2 비타민A(R.E) : 469.2 티아민(mg) : 0.2 리보플라빈(mg) : 0.7 비타민C(mg) : 21.1 칼슘(mg) : 283.7 철분(mg) : 4.5","MLSV_FROM_YMD":"20220302","MLSV_TO_YMD":"20220302"}]}]}"""))
                da = da['mealServiceDietInfo'][1]['row'][0]
                c.execute("INSERT INTO mealDatas VALUES(?,?,?,?)",(da['MLSV_YMD'],da['MMEAL_SC_CODE'],da['DDISH_NM'].replace('<br/>','\n'),int(float(da['CAL_INFO'][:5])*10)))
                con.commit()
        c.execute("SELECT * FROM mealDatas WHERE date=? AND type=?",(int(data[0]),int(data[1])))
        result = c.fetchone()
        print(result)
        sio.emit('mealInfo',result)
    except KeyError:
        pass

if __name__ == '__main__':
    try:
        eventlet.wsgi.server(eventlet.listen(('192.168.123.199', 8080)), app)
    except KeyboardInterrupt:
        con.commit()
        con.close()
