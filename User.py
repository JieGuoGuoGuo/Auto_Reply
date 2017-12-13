#coding:utf-8
import re
import time 
import string 
import os
import xlrd
import xlwt
# from pyExcelerator import *
import BuyItem
from xlutils.copy import copy;  

#########################################
# 初始化数据
# 聊天间隔时间
TALKING_INTERVAL_TIME 				= 5 * 60

# 对话玩家列表
UserList 							= {}

# 聊天步骤
# param					next_by_replay 		
# 						是否根据对方的回复进行下一步对话(对方的回复决定下一步聊天的步骤 )
# 						0为否 , 1为是的

# param					next_step
# 						下一步的聊天步骤,如果next_by_replay为1则下一步聊天步骤的小步骤由玩家输入决定

# param					replay_content_limit
# 						回复内容约束

# param 				wrong_jump_to_next
# 						当前对话错误跳转到目标步骤


Talkint_Step 						= {
	'0':
	{
		'1'					:
		{
			'talking_content'		:"",
			'next_by_replay'		:0,
			'replay_content_limit'	:'',
			'next_step'				:(1 , 1),
			'wrong_jump_to_next'	:(0 , 1),
			'calculate_price'		:0,
		},
	},
	'1':
	{
		'1'					:
		{
			'talking_content'		:"困死了,我在睡觉" + "\r\n" + "[购物]请回复'1'" + "\r\n" + "[聊天]请回复'2'" + "\r\n",
			'next_by_replay'		:1,
			'replay_content_limit'	:['1' , '2'],
			'next_step'				:(2 , 1),
			'wrong_jump_to_next'	:(1 , 1),
			'calculate_price'		:0,
		},
	},
	'2':
	{
		'1'					:
		{
			'talking_content'	:"请输入大区完整名称" + "\r\n" + "如:龙门客栈",
			'next_by_replay'		:0,
			'replay_content_limit'	:['1' , '龙门客栈' , '龙门客栈'],
			'next_step'				:(3 , 1),
			'wrong_jump_to_next'	:(2 , 1),
			'calculate_price'		:0,
		},
		
		'2'					:
		{
			'talking_content'	:"聊你妹啊!等我醒了弄死你!",
			'next_by_replay'		:0,
			'replay_content_limit'	:'',
			'next_step'				:(1 , 1),
			'wrong_jump_to_next'	:(1 , 1),
			'calculate_price'		:0,
		},
	},
	'3':
	{
		'1'					:
		{
			'talking_content'	:"请输入需要购买的物品,按照以下格式输入" + "\r\n" + "火浣台 1 官银 100",
			'next_by_replay'		:0,
			'replay_content_limit'	:'',
			'next_step'				:(4 , 1),
			'wrong_jump_to_next'	:(3 , 1),
			'calculate_price'		:0,
		}
	},
	'4':
	{
		'1'					:
		{
			'talking_content'	:"",
			'next_by_replay'		:0,
			'replay_content_limit'	:'',
			'next_step'				:(1 , 1),
			'wrong_jump_to_next'	:(3 , 1),
			'calculate_price'		:1,
		}
	},
}

#########################################
# 逻辑处理
# < 3 > 
# 存储购买数据到Excel
def record_purchase_record( strUserName , strItemList , nMsgTime ):
  # 1. 打开Excel文件
  bk        = xlrd.open_workbook('Record.xls' , formatting_info=True)
  shxrange  = range(bk.nsheets)
  try:
   sh       = bk.sheet_by_name("Sheet1")
  except:
   sh 		= bk.add_sheet('Sheet 1')
   print ("no sheet in %s named Sheet1" % file)

  # 2. 获取行数和列数
  nrows     = sh.nrows

  print('record_purchase_record ---- >' + str(nrows))

  # 3. 在新的一行中写入数据
  newWb		= copy(bk); 
  newWs		= newWb.get_sheet(0); 
  newWs.write(nrows, 0, label = str(strUserName))
  newWs.write(nrows, 1, label = str(strItemList)) 
  newWs.write(nrows, 2, label = str(nMsgTime)) 
  newWs.write(nrows, 3, label = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))) 
  newWb.save('Record.xls')


# < 2 > 
# 继续对话
# 判断目标聊天步骤是否正常
def check_step( nFirstStep , nSecondStep ):
	if str(nFirstStep) not in Talkint_Step:
		return 0

	if str(nSecondStep) not in Talkint_Step[str(nFirstStep)]:
		return 0

	return 1

# 判断聊天回复内容是否异常
def check_reply_content( nFirstStep , nSecondStep , szContent ):
	# 1. 判断数据是否异常
	if check_step(nFirstStep , nSecondStep) != 1:
		print('check_reply_content failed for the wrong step : First ' + str(nFirstStep) + ' Second ' + str(nSecondStep))
		return 0

	# 2. 如果目标步骤没有回复内容约束
	if Talkint_Step[str(nFirstStep)][str(nSecondStep)]['replay_content_limit'] == '':
		return 1

	# 3. 返回结果
	strContentLimit = Talkint_Step[str(nFirstStep)][str(nSecondStep)]['replay_content_limit']
	return szContent in strContentLimit and 1 or 0


# 获取目标步骤错误处理之后的步骤
def get_after_handle_error_step( nFirstStep , nSecondStep ):
	# 1. 判断数据是否异常
	if check_step(nFirstStep , nSecondStep) != 1:
		print('get_after_handle_error_step failed for the wrong step : First ' + str(nFirstStep) + ' Second ' + str(nSecondStep))
		return (0 , 0)

	# 2. 获取异常处理模式
	strWrongNextSteps 	= Talkint_Step[str(nFirstStep)][str(nSecondStep)]['wrong_jump_to_next']

	# 3. 返回结果
	return (strWrongNextSteps[0] , strWrongNextSteps[1])


# 有朋友与自己继续对话
def get_next_step( strStepList , szTalkingContent ):
	print('User:get_next_step -- Begin')

	# 1. 获取当前的聊天步骤
	nFirstStep				= strStepList['first_step']
	nSecondStep				= strStepList['second_step']
	if check_step(nFirstStep , nSecondStep) != 1:
		print('User:get_next_step failed for the step : First ' + str(nFirstStep) + ' Second ' + str(nSecondStep))
		return (0 , 0 , 0)

	# 2. 判断玩家的回复内容是否有限制
	if check_reply_content(nFirstStep , nSecondStep , szTalkingContent) != 1:
		print('User:get_next_step failed for reply content not in limit list : First ' + str(nFirstStep) + ' Second ' + str(nSecondStep))
		strErrorHandle 		= get_after_handle_error_step(nFirstStep , nSecondStep)
		return (1 , strErrorHandle[0] , strErrorHandle[1])

	# 3. 根据优先级获取下一步聊天内容
	strNextStepList			= Talkint_Step[str(nFirstStep)][str(nSecondStep)]['next_step']
	nNextFirstStep 			= strNextStepList[0]
	nNextSecondStep 		= strNextStepList[1]

	# 3_1. 如果是根据玩家的回复决定下一步
	if Talkint_Step[str(nFirstStep)][str(nSecondStep)]['next_by_replay'] == 1:
		nNextSecondStep		= szTalkingContent

	# 4. 判断下一步聊天步骤是否异常
	# 4_1. 如果下一步聊天步骤异常
	if check_step(nNextFirstStep , nNextSecondStep) != 1:
		strNextStepList		= get_after_handle_error_step(nNextFirstStep , nNextSecondStep)
		nNextFirstStep		= strNextStepList[0]
		nNextSecondStep		= strNextStepList[1]

	# 5. 判断新获取的步骤是否异常,如果异常强制结束
	if check_step(nNextFirstStep , nNextSecondStep) != 1:
		return (0 , 0 , 0)

	# 6. 返回正常结果
	return (1 , nNextFirstStep , nNextSecondStep)

# < 1 > 
# 重置目标玩家的对话步骤
def reset_talking_step(szFriendName):
	UserList[szFriendName]['step'] 					= {}
	UserList[szFriendName]['step']['first_step'] 	= 0
	UserList[szFriendName]['step']['second_step'] 	= 1


# 有朋友与自己对话
def friend_talk_to_me(  strMsgData ):
  szFriendName 		= strMsgData['FromUserName']
  szTalkingContent	= strMsgData['msg_content']
  nMsgTime			= strMsgData['msg_time']

  # 1. 如果玩家之前没有跟自己说过话
  if szFriendName not in UserList:
  	UserList[szFriendName]							= {}
  	UserList[szFriendName]['msg_time']				= nMsgTime
  	reset_talking_step(szFriendName)

  # 2. 如果玩家距离上次对话时间超过间隔时间则重置聊天步骤
  if nMsgTime - UserList[szFriendName]['msg_time'] > TALKING_INTERVAL_TIME:
  	reset_talking_step(szFriendName)

  # ------------------------------------
  # 条件满足
  # 1. 获取玩家下一个聊天步骤
  strData = get_next_step(UserList[szFriendName]['step'] , szTalkingContent)

  # 2. 如果获取下一步聊天步骤正常
  szAnswer= ''
  if strData[0] == 1:

  	# 2_1. 记录数据
  	UserList[szFriendName]['step']['first_step'] 	= strData[1]
  	UserList[szFriendName]['step']['second_step'] 	= strData[2]

  	# 2_2. 获取回复内容
  	szAnswer = Talkint_Step[str(strData[1])][str(strData[2])]['talking_content']

  	# 2_3. 如果玩家的内容需要计算
  	if Talkint_Step[str(strData[1])][str(strData[2])]['calculate_price'] == 1:

  		# 2_3_1. 获取结算内容
  		strItemAnswer 	= BuyItem.analysis_data(szTalkingContent)
  		szAnswer 		= szAnswer + strItemAnswer[1]

  		# 2_3_2. 记录结算数据
  		record_purchase_record(strMsgData['szUserName'] , strItemAnswer[2] , nMsgTime)

  # 3. 如果下一步聊天异常
  else:

  	# 3_1. 重置聊天步骤
  	reset_talking_step(szFriendName)

  # 4. 记录数据
  UserList[szFriendName]['msg_time']				= nMsgTime

  # 5. 返回结果
  return szAnswer


#########################################
# 主函数
def Init():
  print('User:Init')







