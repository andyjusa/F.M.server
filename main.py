import eventlet
import socketio
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

con = sqlite3.connect("./userData.db")
c = con.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS userdata
             (id INT PRIMARY KEY, name TEXT UNIQUE,psw TEXT)''')

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
        return True
    else:
        c.execute("SELECT * FROM userData WHERE id=?", (id,))
        if c.fetchone():
            return True
        return False

testNum = {"23ms2322":8989}

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)
@sio.on('connect')
def connect(sid, environ):
    print(f'Connected: {sid}')

@sio.on('email')
def emailTest(sid,data):
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
        sio.emit('logined',('failed',))

@sio.on('register')
def register(sid,data):
    if data[1]==testNum[data[0]] and not user_exists(data[2],int(data[0][4:8])):
        c.execute("INSERT INTO userData VALUES(?,?,?)",(int(data[0][4:8]),data[2],data[3]))
        print('Suceed')
        con.commit()
        sio.emit("registed","done")
    else:
        sio.emit("registed","fail")

@sio.on('getSchedule')
def getSchedule(sid,data):
    print(data)
    byte_data = bytes(schedule[data])
    sio.emit('schedule', byte_data)

@sio.on('disconnect')
def disconnect(sid):
    print(f'Disconnected: {sid}')

if __name__ == '__main__':
    try:
        eventlet.wsgi.server(eventlet.listen(('localhost', 8080)), app)
    except KeyboardInterrupt:
        con.commit()
        con.close()
