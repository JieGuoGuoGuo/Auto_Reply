# coding:utf-8
import itchat
from itchat.content import TEXT
from itchat.content import *
import sys
import time
import re
import string 

import importlib
importlib.reload(sys)
import os
import Main

msg_information = {}
face_bug=None  #针对表情包的内容


@itchat.msg_register([TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, ATTACHMENT, VIDEO],isFriendChat=True, isGroupChat=True, isMpChat=True)
def handle_receive_msg(msg):
    global face_bug
    #接受消息的时间
    msg_time_rec = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())   

    #在好友列表中查询发送信息的好友昵称
    msg_from = itchat.search_friends(userName=msg['FromUserName'])
    if msg_from is not None and msg_from['NickName'] is not None:
        msg_from = msg_from['NickName'] 
    # msg_from = itchat.search_friends(userName=msg['FromUserName'])['NickName']   

    msg_time        = msg['CreateTime']     #信息发送的时间
    msg_id          = msg['MsgId']          #每条信息的id
    msg_content     = None                  #储存信息的内容
    msg_share_url   = None                  #储存分享的链接，比如分享的文章和音乐
    # print('handle_receive_msg ---- >Log Test : Begin')
    # print (msg)
    # print (msg_time_rec)
    # print (msg['Type'])
    # print (msg['MsgId'])
    # print (msg['User']['RemarkName'])
    # print('handle_receive_msg ---- >Log Test : End')

    # 1. 如果发送的消息是文本或者好友推荐
    if msg['Type'] == 'Text' or msg['Type'] == 'Friends':     
        msg_content = msg['Text']

        # 获取对方的名字(如果有备注的话则记录备注)
        szUserName      = msg['User']['NickName']
        if 'RemarkName' in msg['User'] and msg['User']['RemarkName'] != '':
            szUserName  = msg['User']['RemarkName']

        # 获取回复内容
        strData                 = {}
        strData['szUserName']   = szUserName
        strData['FromUserName'] = msg['FromUserName']
        strData['msg_content']  = msg_content
        strData['msg_time']     = msg_time

        strAnswer = Main.friend_talk_to_me(strData)
        itchat.send( strAnswer , msg['FromUserName'])
        
        print (msg_content)

    # 2. 如果发送的消息是附件、视屏、图片、语音
    elif msg['Type'] == "Attachment" or msg['Type'] == "Video" \
            or msg['Type'] == 'Picture' \
            or msg['Type'] == 'Recording':
        msg_content = msg['FileName']    #内容就是他们的文件名
        msg['Text'](str(msg_content))    #下载文件
        # print msg_content

    # 3. 如果消息是推荐的名片
    elif msg['Type'] == 'Card':  
        # 内容就是推荐人的昵称和性别
        msg_content = msg['RecommendInfo']['NickName'] + '的名片'    
        if msg['RecommendInfo']['Sex'] == 1:
            msg_content += '性别为男'
        else:
            msg_content += '性别为女'

        print (msg_content)

    # 4. 如果消息为分享的位置信息
    elif msg['Type'] == 'Map': 
        x, y, location = re.search(
            "<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*", msg['OriContent']).group(1, 2, 3)
        if location is None:
            msg_content = r"纬度->" + x.__str__() + " 经度->" + y.__str__()     #内容为详细的地址
        else:
            msg_content = r"" + location

    # 5. 如果消息为分享的音乐或者文章，详细的内容为文章的标题或者是分享的名字
    elif msg['Type'] == 'Sharing':
        msg_content = msg['Text']
        # 记录分享的url
        msg_share_url = msg['Url']       
        print (msg_share_url)
    face_bug=msg_content

##将信息存储在字典中，每一个msg_id对应一条信息
    msg_information.update(
        {
            msg_id: {
                "msg_from": msg_from, "msg_time": msg_time, "msg_time_rec": msg_time_rec,
                "msg_type": msg["Type"],
                "msg_content": msg_content, "msg_share_url": msg_share_url
            }
        }
    )


# 监听是否有消息撤回
@itchat.msg_register(NOTE, isFriendChat=True, isGroupChat=True, isMpChat=True)
def information(msg):
    #这里如果这里的msg['Content']中包含消息撤回和id，就执行下面的语句
    if '撤回了一条消息' in msg['Content']:
        old_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)   #在返回的content查找撤回的消息的id
        old_msg = msg_information.get(old_msg_id)    #得到消息
        print (old_msg)
        if len(old_msg_id)<11:  #如果发送的是表情包
            itchat.send_file(face_bug,toUserName='filehelper')
        else:  #发送撤回的提示给文件助手
            msg_body = "告诉你一个秘密~" + "\n" \
                       + old_msg.get('msg_from') + " 撤回了 " + old_msg.get("msg_type") + " 消息" + "\n" \
                       + old_msg.get('msg_time_rec') + "\n" \
                       + "撤回了什么 ⇣" + "\n" \
                       + r"" + old_msg.get('msg_content')
            #如果是分享的文件被撤回了，那么就将分享的url加在msg_body中发送给文件助手
            if old_msg['msg_type'] == "Sharing":
                msg_body += "\n就是这个链接➣ " + old_msg.get('msg_share_url')

            # 将撤回消息发送到文件助手
            itchat.send_msg(msg_body, toUserName='filehelper')
            # 有文件的话也要将文件发送回去
            if old_msg["msg_type"] == "Picture" \
                    or old_msg["msg_type"] == "Recording" \
                    or old_msg["msg_type"] == "Video" \
                    or old_msg["msg_type"] == "Attachment":
                file = '@fil@%s' % (old_msg['msg_content'])
                itchat.send(msg=file, toUserName='filehelper')
                os.remove(old_msg['msg_content'])
            # 删除字典旧消息
            msg_information.pop(old_msg_id)

# 监听群里是否有人@自己
@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
    if msg.isAt:
        msg.user.send(u'@%s\u2005I received: %s' % (
            msg.actualNickName, msg.text))


# 转账
mycount = "强迫症的潘胖纸"
money_receiver = 'filehelper'
@itchat.msg_register([NOTE])
def text_reply(msg):
    pay_type = 0
    pay_type = re.search(".*\<paysubtype\>(.*?)\<\/paysubtype\>.*", msg['Content']).group(1)
    touser = itchat.search_friends(userName=msg['ToUserName'])
    print('msg ------------- >')
    print(msg)
    print(touser)
    print(str(touser['NickName'] == mycount))
    print(str(int(pay_type)))
    # 这里必须得改成你的微信昵称，用于判断是别人给你转的钱
    # pay_type是交易类型：1是发送 3是接收
    if touser['NickName'] == mycount and int(pay_type) == 1:
        print('Receive Money in ----- >')

        # 获取时间，异常处理
        try:
            mytime = time.localtime()  # 这儿获取的是本地时间
            money_time = mytime.tm_year.__str__() + "/" + mytime.tm_mon.__str__() + "/" + mytime.tm_mday.__str__() + " " + mytime.tm_hour.__str__() + ":" + mytime.tm_min.__str__() + ":" + mytime.tm_sec.__str__()
        except:
            None

        if money_time is None:
            money_time = r"读取时间失败，请手动查询"

        # 获取转账人 转账金额
        temp_name = itchat.search_friends(userName=msg['FromUserName'])
        if temp_name['RemarkName'] is not None:  # 备注名优先
            money_friend = temp_name['RemarkName']
        elif temp_name['NickName'] is not None:  # 昵称其次
            money_friend = temp_name['NickName']
        else:
            money_friend = r""

        try:
            money_count = re.search(r"(.*?)收到转账(.*?)元", msg['Text']).group(2)
        except:
            None

        if money_friend is None:
            money_friend = r"读取转账人失败，请手动查询"
        if money_count is None:
            money_count = r"读取转账金额失败，请手动查询"

        # 获取转账说明
        try:
            money_detial = re.search(".*\<pay_memo\>\<!\[CDATA\[(.*?)\]\].*", msg['Content']).group(1)
        except:
            None

        if money_detial is None:
            money_detial = r"无"
        try:
            msg_backup = r"付款人:%s  时间:%s  金额:%s元  付款说明:%s" % (
                money_friend.__str__(), money_time.__str__(), money_count.__str__(), money_detial.__str__())
            itchat.send(r"付款人:%s  "
                        r"时间:%s  "
                        r"金额:%s元  "
                        r"付款说明:%s" % (
                            money_friend.__str__(), money_time.__str__(), money_count.__str__(),
                            money_detial.__str__()),
                        toUserName=money_receiver)
        except:
            #若消息发送失败，尝试将失败消息发送到文件助手，并输出到控制台
            itchat.send(r"消息发送失败：" + msg_backup, toUserName='filehelper')
            print(r"消息发送失败：" + msg_backup)



#########################################
itchat.auto_login(hotReload=True)
Main.main()
itchat.run()

# 多开
# newInstance = itchat.new_instance()
# newInstance.auto_login(hotReload=True, statusStorageDir='newInstance.pkl')
# newInstance.run()

