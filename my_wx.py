import requests
import time
import re
import json
from threading import Thread
from PIL import Image
import math
from collections import OrderedDict
import random
import os
import hashlib
from conf import FILE_TYPE,random_str,get_time,get_locatID
class Wx:
    def __init__(self):
        self.FILE_MAX = 524288
        self.session=requests.session()
        self.session.headers={
            'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://wx.qq.com/',
            'Origin':'https://wx2.qq.com',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
        self.FILE_HEADERS={
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type':'multipart/form-data',
        'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://wx.qq.com/',
            'Accept': '*/*',
        'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'

        }
        self.__open_index()
    def __open_index(self):#打开首页，
        self.session.get('https://wx.qq.com/')
    def __imgs(self,uuid): #获得二维码
        url='https://login.weixin.qq.com/qrcode/{}'.format(uuid)
        imgs=self.session.get(url).content
        with open('img.jpg','wb')as f:
            f.write(imgs)
        im=Image.open('img.jpg')
        im.show()
    def __get_uuid(self):  #先获得uuid，然后可以通过uuid获得唯一的二维码
        url='https://login.wx.qq.com/jslogin'
        data={
            'appid':'wx782c26e4c19acffb',
            'redirect_uri':'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage',
        'fun':'new',
        'lang':'zh_CN',
        '_': get_time() #获得时间戳
        }
        req_text=self.session.get(url,params=data).text
        uuid=re.findall(' window.QRLogin.uuid = "(.*?)";',req_text)[0]
        return uuid
    def __loginicon(self,uuid):
        a = True
        while True:
            url='https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login'
            data={
            'loginicon':'true',
            'uuid':uuid,
            'tip':'1',
           # r:-912395275  #据说是一个取反操作
            '_':get_time()
            }
            req_text=self.session.get(url,params=data,allow_redirects=False).text
            code=re.findall('window.code=(\d+);',req_text)[0]
            code=int(code)
            if code==408:
                pass
            elif code==400:
                return 'flass'
            elif code==201:  #201状态，用户扫码了，但是没有确定
                if a:
                    print('已经扫码，请点击确定')
                a=False
            elif code==200: #状态是200，表示扫码了，而且点击了确认
                ticket=re.findall('ticket=(.*?)&',req_text)[0]
                self.HOST=re.findall('window.redirect_uri="https://(.*?)/cgi-bin/',req_text)[0]
                print('登录成功')
                return ticket

    def ___lgin(self,ticket,uuid): #登陆最后步骤，大部分参数都在这里返回
        url='https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage'
        data={
            'uuid':uuid,
            'ticket':ticket,
            'scan':int(time.time()),
            'lang':'zh_CN',
        }
        req_text=self.session.get(url,params=data,allow_redirects=False).text
        skey=re.findall('<skey>(.*?)</skey>',req_text)[0]
        sid=re.findall('<wxsid>(.*?)</wxsid>',req_text)[0]
        pass_ticket=re.findall('<pass_ticket>(.*?)</pass_ticket>',req_text)[0]
        wxuin=re.findall('<wxuin>(.*?)</wxuin>',req_text)[0]
        return skey,sid,pass_ticket,wxuin

    def __synckey_Mosaic(self, syckey):
        self.syckey_str = ''
        for i in syckey['List']:
            self.syckey_str += '{}_{}|'.format(i['Key'], i['Val'])
        self.syckey_str = self.syckey_str.strip('|')

    def __get_synckey(self):  ##获取syckey参数，这是一个post请求
        '''
        登陆成功以后，需要获取首个syckey参数，第一次获取，一般都是4个，还可以获得自己账户的UserName和，当前会话的窗口信息
        :return:
        '''
        url = 'https://'+self.HOST+'/cgi-bin/mmwebwx-bin/webwxinit?lang=zh_CN&pass_ticket={}'.format(self.pass_ticket)
        data = {
            "BaseRequest": {"Uin": self.Uin, "Sid": self.sid, "Skey": self.skey, "DeviceID":random_str()}
        }
        syckey = self.session.post(url, data=json.dumps(data)).content.decode('utf-8')
        syckey=json.loads(syckey)
        self.syckey = syckey['SyncKey']
        self.my_UserName = syckey['User']['UserName']
        self.my_name = syckey['User']['NickName']
        self.__synckey_Mosaic(self.syckey)
    def get_my_name(self):
        return self.my_name
    def __getBaseRequest(self):
        return {"Uin": self.Uin, "Sid": self.sid,
                "Skey": self.skey,
                "DeviceID": random_str()}
    def __get_messg(self):
        '''

        在轮询请求返回的selector将会大于0 的情况下，调用获取消息的函数
        每次会获得新的syckey参数，下次获取消息请求使用新的syckey参数
        '''
        mesglist=[]
        url = 'https://'+self.HOST+'/cgi-bin/mmwebwx-bin/webwxsync?sid={sid}&skey={skey}&lang=zh_CN&pass_ticket={pass_tic}'.format(
            sid=self.sid, skey=self.skey, pass_tic=self.pass_ticket)
        data = {"BaseRequest":self.__getBaseRequest(),
                "SyncKey": self.syckey
                }
        syckey_text = self.session.post(url, data=json.dumps(data)).content.decode('utf-8')
        syckey_json = json.loads(syckey_text)
        self.syckey = syckey_json['SyncKey']
        self.__synckey_Mosaic(self.syckey)
        for meg in syckey_json['AddMsgList']:
            if meg['FromUserName']!=self.my_UserName:

                if re.findall('@@',meg['FromUserName']):
                    meg['megtype']='群消息'
                    if re.findall('@{}'.format(self.my_name),meg['Content']):
                        meg['megtype']='@我的'
                else:
                    meg['megtype']='个人消息'
                mesglist.append(meg)

        return mesglist
    def __get_NickName(self,UserName):
        for name in self.get_all_name():
            if UserName == name['UserName']:
                return name['NickName']
        else:
            return None
    def UserName_to_NickName(self,UserName):
        NickName = self.__get_NickName(UserName)
        if NickName:
            return NickName
        else:
            NickName = self.Refresh_name()
            return NickName

    def NickName_to_UserName(self,NickName):
        UserName=self.__get_UserName(NickName)
        if UserName:
            return UserName
        else:
            UserName=self.Refresh_name()
            return UserName
    def __get_UserName(self,NickName):
        for name in self.get_all_name():
            if NickName == name['NickName']:
                return name['UserName']
        else:
            return None
    def __RkNames(self):
        '''
        获取所有联系人的函数

        '''
        url = 'https://'+self.HOST+'/cgi-bin/mmwebwx-bin/webwxgetcontact'
        data = {
            'r': get_time(),
            'seq': '0',
            'skey': self.skey
        }
        name_text = self.session.get(url, params=data).content.decode('utf-8')
        name_json = json.loads(name_text)
        self.NameList = []
        for name in name_json['MemberList']:
            namedict = {
                'Province': name['Province'],  # 所在省
                'City': name['City'],  # 所在地区
                'NickName': name['NickName'],  # 用户昵称
                'Signature': name['Signature'],  # 用户的个人说明
                'Sex': name['Sex'],  # 性别1为男，2为女，0为未设置
                'UserName': name['UserName'],  # 该用户的唯一标识，用来发信息都用它
                'VerifyFlag': name['VerifyFlag'],  # 用户的类型0是普通用户，24是公众号
                'HeadImgUrl': name['HeadImgUrl']  # 用户头像的地址

            }
            self.NameList.append(namedict)
        return self.NameList
    def login(self):#登陆主体函数，
        while True:
            uuid=self.__get_uuid()  #首先获得uuid参数
            self.__imgs(uuid) ###通过uuid参数获得二维码
            ticket=self.__loginicon(uuid) ##发送，登陆状态判定的请求，如果用户扫码点击登陆了，会返回200状态码，在拿到ticket参数
            if ticket=='flass':
                print('验证码已经过期')
                print('生成新的验证码')
                continue
            self.skey,self.sid,self.pass_ticket,self.Uin=self.___lgin(ticket,uuid)  #传入ticket，和uuid参数，完成登陆的最后一步,获得skey,sid参数表示登陆成功
            self.__get_synckey()
            print(self.my_name,'登陆成功')
            print('获取所有用户信息')
            self.__RkNames()  # 登陆成功后获取所有用户信息
            self.webwx_data_ticket=self.session.cookies.get('webwx_data_ticket')
            break

    def Refresh_name(self):
        self.__RkNames()  ##刷新用户信息
    def get_comm(self): #获得所有普通用户:
        return [i for i in self.NameList if i['VerifyFlag']==0]
    def get_Public(self):#获取所有公众号
        return [i for i in self.NameList if i['VerifyFlag']!=0]
    def get_all_name(self): #获取所有用户
        return self.NameList
    def __OPTIONS(self):
        url='https://file.'+self.HOST+'/cgi-bin/mmwebwx-bin/webwxuploadmedia?f=json'
        self.session.options(url)
    def update_file(self,path,ToUserName):#上传文件
        Maxsize=os.path.getsize(path)
        file_time=time.strftime('%a %b %d %Y %H:%M:%S GMT+0800 (CST)',time.localtime(os.path.getatime(path)))
        with open(path, 'rb')as f:
            FileMd5=hashlib.md5(f.read()).hexdigest()
        chunks=math.ceil(Maxsize/self.FILE_MAX)
        print(chunks)
        filename=os.path.basename(path)    #获取文件全名
        filetype=FILE_TYPE[os.path.splitext(filename)[1]] #获取文件的类型
        # def file_open(path,chuksiz):
        #     with open(path,'rb')as f:
        #         while True:
        #             data=f.read(chuksiz)
        #             if data:
        #                 yield data
        #             else:
        #                 return
        files = open(path, 'rb')
        url='https://file.'+self.HOST+'/cgi-bin/mmwebwx-bin/webwxuploadmedia?f=json'
        uploadmediarequest=json.dumps(OrderedDict([("UploadType", 2),
                                        ("BaseRequest", self.__getBaseRequest()),
                                        ("ClientMediaId", get_time()),
                                        ("TotalLen", str(Maxsize)),
                                        ("StartPos", 0),
                                        ("DataLen", str(Maxsize)),
                                        ("MediaType", 4),
                                    ("FromUserName", self.my_UserName),
                                        ("ToUserName", ToUserName),
                                        ("FileMd5", FileMd5)
                                        ]))
        for chunk in range(chunks):
            data=OrderedDict([
                ('id',(None,'WU_FILE_0')),
                 ('name',(None,filename)),
                 ('type',(None,filetype)),
                 ('lastModifiedDate',(None,file_time)),
                 ('size',(None,str(Maxsize))),
                 ('chunks',(None,str(chunks))),
                 ('chunk',(None,str(chunk))),
                 ('mediatype',(None,'doc')),
                 ('uploadmediarequest',(None,uploadmediarequest)),
                 ('webwx_data_ticket',(None,self.webwx_data_ticket)),
                  ('pass_ticket',(None,self.pass_ticket)),
                  ('filename',(filename,files.read(self.FILE_MAX),'application/octet-stream'))
                    ])
            if chunks==1:
                del data['chunks']
                del data['chunk']
            # self.__OPTIONS()
            req=self.session.post(url,files=data,headers=self.FILE_HEADERS).text
        print(req)
        MediaId=json.loads(req)['MediaId']
        files.close()
        return MediaId


    def sned_file(self,filepath,ToUserName=None,NickName=None):
        '''
        发送文件函数，需要两个参数，文件路径和发送目标,也可以直接输入y用户名
        :param filepath:
        :param ToUserName:
        :return:
        '''
        if NickName and ToUserName==None:
            ToUserName=self.NickName_to_UserName(NickName)
        MediaId=self.update_file(filepath,ToUserName)
        url='https://'+self.HOST+'/cgi-bin/mmwebwx-bin/webwxsendmsgimg'
        params={
            'fun':'async',
            'f':'json',
            'lang':'zh_CN',
            'pass_ticket':self.pass_ticket
        }
        locatID=get_locatID()
        data={
            'BaseRequest':self.__getBaseRequest(),
            'Msg':{"Type": 3,
                 "Content": "",
                 'MediaId':MediaId,
                'FromUserName':self.my_UserName,
                 "ToUserName": ToUserName,
                 "LocalID": locatID, "ClientMsgId": locatID},
            'Scene':'0'

        }
        print(data)
        data_json=json.dumps(data,ensure_ascii=False).encode('utf-8')
        req_json=self.session.post(url,data=data_json,params=params).json()
        print(req_json)
        if req_json['BaseResponse']['Ret']==0:
            print('文件发成功')


    def send_message(self,UserName,conten):
        '''
        发送消息的方法，需要发送目标的UserName，和发送内容
        :param UserName:
        :param conten:
        :return:
        '''
        url='https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg'
        locatID=get_locatID()
        data={"BaseRequest":self.__getBaseRequest(),
              "Msg":{"Type":1,
                     "Content":conten,
                     "FromUserName":self.my_UserName,
                     "ToUserName":UserName,
                     "LocalID":locatID,
                     "ClientMsgId":locatID},
              "Scene":0}
        self.session.post(url,data=json.dumps(data,ensure_ascii=False).encode('utf-8')).json()
        #json.dumps会自动把中文转码成ascii，然后在解码成转码成utf-8，微信端才能接收到中文


    def getmessage(self,message_Handle):  #这是一个获得消息的的装饰器，可以装饰到处理消息的函数上

        '''
        定义一个装饰器，里面定义了一个线程，来轮询消息，如果有新的消息调用被装饰的函数来处理消息
        获得消息，需要需要发送https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck链接的轮询请求，
        如果有消息，请求返回的window.synccheck={retcode:"0",selector:2" ,selector将会大于0，大于0的情况下，
        可以发送__get_messg这个函数的请求来返回消息
        :param message_Handle:
        :return:
        '''
        def message_func(*args):
            def message_Thed():
                while True:
                    try:
                        url='https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck'
                        data={
                            'r':get_time(),
                            'skey':self.skey,
                            'sid':self.sid,
                            'uin':self.Uin,
                            'deviceid':random_str(),
                            'synckey':self.syckey_str,
                            '_': get_time()
                        }
                        req_text=self.session.get(url,params=data).text
                        selector=re.findall('window.synccheck={retcode:"0",selector:"(\d+)"}',req_text)
                        if selector!='0':
                            message_list=self.__get_messg()
                            if message_list:
                                message_Handle(message_list)  #返回获得的信息列表
                                '''
                                是一个列表，嵌套字典，其中FromUserName字段是发送消息的唯一标识，
                                Content是他发送的内容
                            '''
                    except Exception as e:
                        pass
            Thread(target=message_Thed).start()  #启动一个线程，一直发送请求来获得最新的信息
        return message_func
# if __name__ == '__main__':
#     # wx_my=Wx()
#     # @wx_my.getmessage
#     # def message_(megs):
#     #     for meg in megs:
#     #         usrname=meg['FromUserName']  #发消息的人，
#     #         conten=meg['Content']  #消息内容
#     #         send_conten='本条信息来微信机器人的测试信息'
#     #         wx_my.send_message(usrname,send_conten)
#     # wx_my.login()
#     #
#     # print(namelist)
#     # # wx_my.__get_synckey()
#     # # message_()













