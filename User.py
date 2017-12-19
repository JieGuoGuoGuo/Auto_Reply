#coding:utf-8
import re
import time 
import string 
import os
import xlrd
from xlwt import *
import BuyItem
from xlutils.copy import copy;  
import Talk_Step

#########################################
# 初始化数据
# 聊天间隔时间
TALKING_INTERVAL_TIME 				= 5 * 60

# 对话玩家列表
UserList 							= {}

# 总结文本
SUMMARIZE_CONTENT 					= "请确认您的购买信息: \r\n" + "大区 	: %s\r\n" + "角色名称: %s\r\n" + "商品信息:\r\n%s"

# 聊天步骤
Talkint_Step 						= Talk_Step.Talkint_Step

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
  ws.write(0, 3, label = '商品名称') 
  ws.write(0, 4, label = '商品个数') 
  ws.write(0, 5, label = '上一条微信信息发送的时间') 
  ws.write(0, 6, label = '系统处理时间')
  w.save(szFileName)

# 存储购买数据到Excel
def record_purchase_record(szFriendName):
  # 1. 如果玩家的物品列表不存在商品信息不做任何处理
  if 'game_purchase_info' not in UserList[szFriendName] or 'item_list' not in UserList[szFriendName]['game_purchase_info'] or UserList[szFriendName]['game_purchase_info']['item_list'] == '':
  	return False

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

  # 4. 在新的一行中写入数据(逐条写入)
  newWb		= copy(bk)
  newWs		= newWb.get_sheet(0)

  for str_item_info in UserList[szFriendName]['game_purchase_info']['item_list']:
  	newWs.write(nrows, 0 , label = str(UserList[szFriendName]['wechat_name']))
  	newWs.write(nrows, 1 , label = str(UserList[szFriendName]['game_purchase_info']['service_name'])) 
  	newWs.write(nrows, 2 , label = str(UserList[szFriendName]['game_purchase_info']['role_name'])) 
  	newWs.write(nrows, 3 , label = str(str_item_info))
  	newWs.write(nrows, 4 , label = str(UserList[szFriendName]['game_purchase_info']['item_list'][str_item_info])) 
  	newWs.write(nrows, 5 , label = str(UserList[szFriendName]['msg_time'])) 
  	newWs.write(nrows, 6 , label = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))) 
  	nrows = nrows + 1

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

	# 3_2. 如果没有特殊需求则选择默认步骤
	nNextFirstStep 			= strNextStepList['default'][0]
	nNextSecondStep 		= strNextStepList['default'][1]

	# 3_1. 如果是根据玩家的回复决定下一步
	if Talkint_Step[str(nFirstStep)][str(nSecondStep)]['replay_content_type'] == 3:

		# 3_1_2. 根据玩家的回复获取下一步内容(回复内容是否在限制列表中,在上面已经处理过)
		nNextFirstStep 			= strNextStepList[szTalkingContent][0]
		nNextSecondStep 		= strNextStepList[szTalkingContent][1]

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
	UserList[szFriendName]['step']['first_step'] 	= 0			# 大步骤
	UserList[szFriendName]['step']['second_step'] 	= 1			# 小步骤

# 重置目标玩家的游戏购买信息
def reset_game_purchase_info( szFriendName ):
	UserList[szFriendName]['game_purchase_info']					= {}		
	UserList[szFriendName]['game_purchase_info']['role_name']		= ''		# 游戏内的角色名字
	UserList[szFriendName]['game_purchase_info']['service_name']	= ''		# 大区名字
	UserList[szFriendName]['game_purchase_info']['item_list']		= {}		# 购买商品
	UserList[szFriendName]['game_purchase_info']['item_answer']		= ''		# 购买商品回复信息
  UserList[szFriendName]['game_purchase_info']['all_cost']   = 0    # 商品总计应付金额
  UserList[szFriendName]['game_purchase_info']['friend_pay']   = 0    # 玩家实际支付的金额


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
  szWeChatName 		   = strMsgData['szUserName']
  szFriendName 		   = strMsgData['FromUserName']
  szTalkingContent   = strMsgData['msg_content']
  nMsgTime			     = strMsgData['msg_time']
  nFriendPay         = 0
  if strMsgData['friend_pay'] is not None:
    nFriendPay       = strMsgData['friend_pay']

  szAnswer           = '数据异常,错误步骤 : '
  # 1. 如果玩家之前没有跟自己说过话
  if szFriendName not in UserList:
  	reset_friend_info(strMsgData)

  # 2. 如果玩家距离上次对话时间超过间隔时间则重置聊天步骤
  if nMsgTime - UserList[szFriendName]['msg_time'] > TALKING_INTERVAL_TIME:
  	reset_friend_info(strMsgData)
  
  # 3. 判断玩家当前步骤是否记录
  if UserList[szFriendName]['step'] is None:
    reset_friend_info(strMsgData)

  nCurFirstStep   = UserList[szFriendName]['step']['first_step']
  nCurSecondSetp  = UserList[szFriendName]['step']['second_step']

  # 4. 获取下一步信息
  strData = get_next_step(UserList[szFriendName]['step'] , szTalkingContent)
  if strData[0] != 1:
    reset_friend_info(strMsgData)
    szAnswer         = szAnswer + ' : 1' + str(nCurFirstStep) + '  ' + str(nCurSecondSetp)
    return szAnswer

  # ------------------------------------
  # 条件满足
  szAnswer			= ''

  # 1. 获取回复内容
  szAnswer    = Talkint_Step[str(strData[1])][str(strData[2])]['talking_content']

  # 2. 判断玩家的回复内容是否需要特殊处理
  # 2_1. 如果玩家的回复内容为商品
  if Talkint_Step[str(nCurFirstStep)][str(nCurSecondSetp)]['replay_content_type'] == 1:

    # 2_1_1. 获取结算内容
    strItemAnswer           = BuyItem.analysis_data(szTalkingContent)

    # 2_1_2. 记录结算数据
    UserList[szFriendName]['game_purchase_info']['item_list']   = strItemAnswer[2]
    UserList[szFriendName]['game_purchase_info']['item_answer']   = strItemAnswer[1]
    UserList[szFriendName]['game_purchase_info']['all_cost']   = strItemAnswer[0]

  # 2_2. 如果玩家的回复内容为大区名称,则记录大区名称
  elif Talkint_Step[str(nCurFirstStep)][str(nCurSecondSetp)]['replay_content_type'] == 2:
    UserList[szFriendName]['game_purchase_info']['service_name']  = szTalkingContent

  # 2_3. 如果玩家的回复内容为角色名称,则记录游戏内角色名字
  elif Talkint_Step[str(nCurFirstStep)][str(nCurSecondSetp)]['replay_content_type'] == 4:
    UserList[szFriendName]['game_purchase_info']['role_name']   = szTalkingContent

  # 2_4. 其它的暂不处理
  else:
    pass

  # 3. 判断玩家当前步骤是否需要特殊处理
  # 3_1. 如果需要总结购买信息并在此次对话中回复给玩家
  if Talkint_Step[str(nCurFirstStep)][str(nCurSecondSetp)]['special_handle'] == 1:
    szAnswer = get_summarize_content( szFriendName ) + szAnswer

  # 3_2. 如果需要记录数据到Excel中
  elif Talkint_Step[str(nCurFirstStep)][str(nCurSecondSetp)]['special_handle'] == 2:
    record_purchase_record(szFriendName)

  # 3_3. 如果检查玩家转账
  elif Talkint_Step[str(nCurFirstStep)][str(nCurSecondSetp)]['special_handle'] == 3:
    if nFriendPay != 0 and UserList[szFriendName]['game_purchase_info']['all_cost'] is not None and 


  # 3_4. 其它的暂不处理
  else:
    pass

  # 4. 记录步骤数据
  UserList[szFriendName]['step']['first_step']   = strData[1]
  UserList[szFriendName]['step']['second_step']  = strData[2]

  # 5. 记录聊天时间
  UserList[szFriendName]['msg_time']				= nMsgTime

  # 6. 返回结果
  return szAnswer


#########################################
# 转账处理
def check_friend_transfer_to_my_accounts( strMsgData ):
  # 1. 解析数据
  szWeChatName       = strMsgData['szUserName']
  szFriendName       = strMsgData['FromUserName']
  szTalkingContent   = strMsgData['msg_content']
  nMsgTime           = strMsgData['msg_time']
  nFriendPay         = strMsgData['friend_pay']

  # 2. 判断数据是否异常
  szAnswer           = ""

  # 2_1. 判断之前的对话列表中是否存在该玩家
  if szFriendName not in UserList:
    szAnswer         = "一言不合就转账,这钱我不能收啊"
    return (False , szAnswer)

  # 2_2. 判断玩家的当前步骤是否异常
  if UserList[szFriendName]['step'] is None or UserList[szFriendName]['step']['first_step'] is None or UserList[szFriendName]['step']['second_step'] is None:
    szAnswer         = "当前步骤异常 -- 1"
    return szAnswer

  nCurFirstStep   = UserList[szFriendName]['step']['first_step']
  nCurSecondSetp  = UserList[szFriendName]['step']['second_step']
  if check_step(nCurFirstStep , nCurSecondSetp) != 1:
    szAnswer         = "当前步骤异常 -- 2"
    return (False , szAnswer)

  # 2_3. 




  # 2. 
  # 2_1. 判断玩家当前步骤是否异常



  


#########################################
# 主函数
def Init():
  print('User:Init')







