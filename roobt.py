from WXencap import WXRobot
import requests
import re
class robot:
    def __init__(self):
        self.TULING_KEY='19ae9874f4484b28a929128f6f3a139f'
        self.TULING_API='http://www.tuling123.com/openapi/api'
        self.TULING_off=False
    def roobt_tuling(self,info,uuid):
        data={
            'key':self.TULING_KEY,
            'info':info,
            'userid':uuid,
        }
        TL_req=requests.post(self.TULING_API,data=data).json()
        return TL_req['text']
    def mesage(self):
        @WXRobot.Messprcr
        def __mesage__(msages):
            for msag in msages:
                if msag['megtype']!='群消息':
                    FromUserName = msag['FromUserName']
                    Content = msag['Content']
                    if msag['megtype']=='@我的':
                        Content=re.findall(r'@{}\u2005(\D+)'.format(WXRobot.my_name()),Content)[0]
                        print(Content)
                    if self.TULING_off:
                        if Content=='图灵机器人':
                            self.TULING_off=False
                            WXRobot.send_mesg(FromUserName,'图灵机器人已经关闭')

                        else:
                            TL_req=self.roobt_tuling(Content,FromUserName.strip('@'))
                            WXRobot.send_mesg(FromUserName,TL_req)

                    else:
                        if Content=='开启图灵机器人':
                            self.TULING_off=True
                            WXRobot.send_mesg(FromUserName,'图灵机器人已经开启')

                        else:
                            mes='hello 现在微信由主人写的程序监管，你可以输入 开启图灵机器人  来和机器人对话，也可以输入 关闭图灵机器人'
                            WXRobot.send_mesg(FromUserName,mes)

        __mesage__()
    def run(self):
        WXRobot.login()
        self.mesage()
if __name__ == '__main__':
    rob=robot()
    rob.run()