#coding:utf-8
import re
import time 
import string 
import xlrd
import BuyItem
import User

#########################################
# 测试数据
string = '鞋子 4 裤子3 饰品 6.5'
# send_msg = analysis_data(string)
# print (send_msg[1])


# 主函数
def main():
  # 1. 初始化物品文件
  BuyItem.Init()

  # 2. 初始化玩家列表
  User.Init()

  # 测试
  # strAnswer = friend_talk_to_me('11111231231' , '1')
  # print(strAnswer[1])


# 有朋友与自己对话
def friend_talk_to_me( strData ):
  strAnswer = User.friend_talk_to_me(strData)
  return strAnswer




  

if __name__=="__main__":
 main()



