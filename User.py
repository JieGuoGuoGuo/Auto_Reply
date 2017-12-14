#coding:utf-8
import re
import time 
import string 
import os
import xlrd
from xlwt import *
import BuyItem
from xlutils.copy import copy;  

#########################################
# 初始化数据
# 聊天间隔时间
TALKING_INTERVAL_TIME 				= 5 * 60

# 对话玩家列表
UserList 							= {}

# 总结文本
SUMMARIZE_CONTENT 					= "请确认您的购买信息: \r\n" + "大区 	: %s\r\n" + "角色名称: %s\r\n" + "商品信息:\r\n%s" + "\r\n" + "[重新输入]请回复'1'\r\n[确认]请回复'2'\r\n"

# 聊天步骤
# param					next_step
# 						下一步的聊天步骤,如果replay_content_type为3则下一步聊天步骤的小步骤由玩家输入决定

# param					replay_content_limit
# 						回复内容约束

# param 				wrong_jump_to_next
# 						当前对话错误跳转到目标步骤


# param 				replay_content_type
# 						0为普通的聊天回复(不用管),1为商品,2为大区名称,3为下一步的小步骤,4为游戏内角色名称


# param					special_handle
# 						0为无任何特殊处理,1为总结购买信息并在此次对话中回复给玩家,2为记录数据到Excel中


Talkint_Step 						= {
	'0':
	{
		'1'					:
		{
			'talking_content'		:"",
			'replay_content_limit'	:'',
			'next_step'				:(1 , 1),
			'wrong_jump_to_next'	:(0 , 1),
			'replay_content_type'	:0,
			'special_handle'		:0,
		},
	},
	'1':
	{
		'1'					:
		{
			'talking_content'		:"你好,我休息去了~" + "\r\n" + "[购物]请回复'1'" + "\r\n" + "[聊天]请回复'2'" + "\r\n",
			'replay_content_limit'	:['1' , '2'],
			'next_step'				:(2 , 1),
			'wrong_jump_to_next'	:(1 , 1),
			'replay_content_type'	:3,
			'special_handle'		:0,
		},
	},
	'2':
	{
		'1'					:
		{
			'talking_content'	:"请输入大区完整名称" + "\r\n" + "如:龙门客栈",
			'replay_content_limit'	:['1' , '龙门客栈' , '龙门客栈'],
			'next_step'				:(3 , 1),
			'wrong_jump_to_next'	:(2 , 1),
			'replay_content_type'	:2,
			'special_handle'		:0,
		},
		
		'2'					:
		{
			'talking_content'	:"聊你妹啊!等我醒了弄死你!",
			'replay_content_limit'	:'',
			'next_step'				:(1 , 1),
			'wrong_jump_to_next'	:(1 , 1),
			'replay_content_type'	:0,
			'special_handle'		:0,
		},
	},
	'3':
	{
		'1'					:
		{
			'talking_content'	:"请输入角色名称:",
			'replay_content_limit'	:'',
			'next_step'				:(4 , 1),
			'wrong_jump_to_next'	:(3 , 1),
			'replay_content_type'	:4,
			'special_handle'		:0,
		}
	},
	'4':
	{
		'1'					:
		{
			'talking_content'	:"请输入需要购买的物品,按照以下格式输入" + "\r\n" + "火浣台 1 官银 100",
			'replay_content_limit'	:'',
			'next_step'				:(5 , 1),
			'wrong_jump_to_next'	:(4 , 1),
			'replay_content_type'	:1,
			'special_handle'		:1,
		}
	},
	'5':
	{
		'1'					:
		{
			'talking_content'	:"",
			'replay_content_limit'	:'',
			'next_step'				:(2 , 1),
			'wrong_jump_to_next'	:(1 , 1),
			'replay_content_type'	:0,
			'special_handle'		:2,
		}
	},
}

#########################################
# 逻辑处理
# 获取总结文本
def get_summarize_content(szFriendName):
	# 大区 + 角色名字 + 购买信息
	szContent 	= SUMMARIZE_CONTENT % (UserList[szFriendName]['game_purchase_info']['service_name'] , UserList[szFriendName]['game_purchase_info']['role_name'] , UserList[szFriendName]['game_purchase_info']['item_answer'])
	return szContent


# < 3 > 
# 获取当前日期的字符串
def get_cur_date():
  return str(time.strftime("%Y-%m-%d", time.localtime()))

# 创建新的工作文本
def creat_new_work_excel( szFileName , szSheetName ):
  w 	= Workbook()
  ws 	= w.add_sheet(szSheetName)
  ws.write(0, 0, label = '微信名称')
  ws.write(0, 1, label = '大区名称')
  ws.write(0, 2, label = '角色名称')
  ws.write(0, 3, label = '商品信息') 
  ws.write(0, 4, label = '上一条微信信息发送的时间') 
  ws.write(0, 5, label = '系统处理时间')
  w.save(szFileName)

# 存储购买数据到Excel
def record_purchase_record(szFriendName):
  # 1. 获取文件名字
  szCurDate 	= get_cur_date()
  szFileName 	= szCurDate + '.xls'
  szSheetName 	= 'Sheet1'

  # 2. 如果目标文件不存在则创建文件
  if not os.path.isfile(szFileName):
  	creat_new_work_excel(szFileName , szSheetName)

  # 2. 打开Excel文件
  bk        = xlrd.open_workbook(szFileName , formatting_info=True)
  shxrange  = range(bk.nsheets)
  try:
   sh       = bk.sheet_by_name(szSheetName)
  except:
   sh 		= bk.add_sheet(szSheetName)
   print ("no sheet in %s named Sheet1" % file)

  # 3. 获取行数和列数
  nrows     = sh.nrows

  # 4. 在新的一行中写入数据
  newWb		= copy(bk)
  newWs		= newWb.get_sheet(0)
  newWs.write(nrows, 0 , label = str(UserList[szFriendName]['wechat_name']))
  newWs.write(nrows, 1 , label = str(UserList[szFriendName]['game_purchase_info']['service_name'])) 
  newWs.write(nrows, 2 , label = str(UserList[szFriendName]['game_purchase_info']['role_name'])) 
  newWs.write(nrows, 3 , label = str(UserList[szFriendName]['game_purchase_info']['item_list'])) 
  newWs.write(nrows, 4 , label = str(UserList[szFriendName]['msg_time'])) 
  newWs.write(nrows, 5 , label = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))) 
  newWb.save(szFileName)


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
	if Talkint_Step[str(nFirstStep)][str(nSecondStep)]['replay_content_type'] == 3:
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
	UserList[szFriendName]['step']['first_step'] 	= 1			# 大步骤
	UserList[szFriendName]['step']['second_step'] 	= 1			# 小步骤

# 重置目标玩家的游戏购买信息
def reset_game_purchase_info( szFriendName ):
	UserList[szFriendName]['game_purchase_info']					= {}		
	UserList[szFriendName]['game_purchase_info']['role_name']		= ''		# 游戏内的角色名字
	UserList[szFriendName]['game_purchase_info']['service_name']	= ''		# 大区名字
	UserList[szFriendName]['game_purchase_info']['item_list']		= {}		# 购买商品
	UserList[szFriendName]['game_purchase_info']['item_answer']		= ''		# 购买商品回复信息


# 重置玩家的信息
def reset_friend_info( strData ):
	szFriendName 									= strData['FromUserName']

	# 1. 初始化数据
	UserList[szFriendName]							= {}

	# 2. 重置目标玩家对话时间
	UserList[szFriendName]['msg_time']				= strData['msg_time']

	# 3. 重置玩家微信名称
	UserList[szFriendName]['wechat_name']			= strData['szUserName']

	# 4. 重置目标玩家的对话步骤
	reset_talking_step(szFriendName)

	# 5. 重置目标玩家的游戏购买信息
	reset_game_purchase_info(szFriendName)


# 有朋友与自己对话
def friend_talk_to_me( strMsgData ):
  szWeChatName 		= strMsgData['szUserName']
  szFriendName 		= strMsgData['FromUserName']
  szTalkingContent	= strMsgData['msg_content']
  nMsgTime			= strMsgData['msg_time']

  # 1. 如果玩家之前没有跟自己说过话
  if szFriendName not in UserList:
  	reset_friend_info(strMsgData)

  # 2. 如果玩家距离上次对话时间超过间隔时间则重置聊天步骤
  if nMsgTime - UserList[szFriendName]['msg_time'] > TALKING_INTERVAL_TIME:
  	reset_talking_step(szFriendName)

  # 3. 获取玩家下一个聊天步骤
  strData = get_next_step(UserList[szFriendName]['step'] , szTalkingContent)

  # ------------------------------------
  # 条件满足
  szAnswer			= ''
  nCurFirstStep 	= UserList[szFriendName]['step']['first_step']
  nCurSecondSetp 	= UserList[szFriendName]['step']['second_step']


  # 1. 如果获取下一步聊天步骤正常
  if strData[0] == 1:

  	# 1_1. 获取回复内容
  	szAnswer 		= Talkint_Step[str(strData[1])][str(strData[2])]['talking_content']

  	# 1_2. 判断玩家的回复内容是否需要特殊处理
  	# 1_2_1. 如果玩家的回复内容为商品
  	if Talkint_Step[str(nCurFirstStep)][str(nCurSecondSetp)]['replay_content_type'] == 1:

  		# 1_2_1_1. 获取结算内容
  		strItemAnswer 					= BuyItem.analysis_data(szTalkingContent)

  		# 1_2_1_2. 记录结算数据
  		UserList[szFriendName]['game_purchase_info']['item_list']		= strItemAnswer[2]
  		UserList[szFriendName]['game_purchase_info']['item_answer']		= strItemAnswer[1]

  	# 1_2_2. 如果玩家的回复内容为大区名称,则记录大区名称
  	elif Talkint_Step[str(nCurFirstStep)][str(nCurSecondSetp)]['replay_content_type'] == 2:
  		UserList[szFriendName]['game_purchase_info']['service_name']	= szTalkingContent

  	# 1_2_3. 如果玩家的回复内容为角色名称,则记录游戏内角色名字
  	elif Talkint_Step[str(nCurFirstStep)][str(nCurSecondSetp)]['replay_content_type'] == 4:
  		UserList[szFriendName]['game_purchase_info']['role_name']		= szTalkingContent

  	# 1_2_4. 其它的暂不处理
  	else:
  		pass

  	# 1_3. 判断玩家当前步骤是否需要特殊处理
  	# 1_3_1. 如果需要总结购买信息并在此次对话中回复给玩家
  	if Talkint_Step[str(nCurFirstStep)][str(nCurSecondSetp)]['special_handle'] == 1:
  		szAnswer = szAnswer + get_summarize_content( szFriendName )

  	# 1_3_2. 如果需要记录数据到Excel中
  	elif Talkint_Step[str(nCurFirstStep)][str(nCurSecondSetp)]['special_handle'] == 2:
  		record_purchase_record(szFriendName)

  	# 1_3_3. 其它的暂不处理
  	else:
  		pass

  	# 1_4. 记录步骤数据
  	UserList[szFriendName]['step']['first_step'] 	= strData[1]
  	UserList[szFriendName]['step']['second_step'] 	= strData[2]


  # 2. 如果下一步聊天异常则重置聊天步骤
  else:
  	reset_talking_step(szFriendName)

  # 3. 记录聊天时间
  UserList[szFriendName]['msg_time']				= nMsgTime

  # 4. 返回结果
  return szAnswer


#########################################
# 主函数
def Init():
  print('User:Init')







