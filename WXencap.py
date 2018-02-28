from my_wx import Wx
class WXRobot():
    '''
    WXRobot所提供的所有方法
    '''
    __wx__=Wx()
    Messprcr=__wx__.getmessage  #消息处理,#这是一个获得消息的的装饰器，可以装饰到处理消息的函数上,处理消息函数需要一个参数来获取消息
    send_mesg=__wx__.send_message  #发送消息
    Refresh_name=__wx__.Refresh_name  #刷新用户信息
    get_comm=__wx__.get_comm        #获取普通用户
    NickName_to_UserName=__wx__.NickName_to_UserName #通过用户名去找到用户标识
    UserName_to_NickName=__wx__.UserName_to_NickName #通过用户标识去找用户名
    get_Public=__wx__.get_Public    #公众号
    get_all_name=__wx__.get_all_name  #获取所有用户
    login=__wx__.login                #登陆方法
    send_img=__wx__.sned_file         #发送文件
    my_name = __wx__.get_my_name    #获取自己的用户名



