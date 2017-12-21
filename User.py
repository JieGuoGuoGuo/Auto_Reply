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


# 获取当前日期的字符串
def get_cur_date():
  return str(time.strftime("%Y-%m-%d", time.localtime()))


""" -------------------------------------------------------------------------------------------------"""
#                                               转账记录
""" -------------------------------------------------------------------------------------------------"""
# 创建转账记录目录
def creat_transform_account_record( szFileName , szSheetName ):
  w   = Workbook()
  ws  = w.add_sheet(szSheetName)
  ws.write(0, 0, label = '微信名称')
  ws.write(0, 1, label = '转账金额')
  ws.write(0, 2, label = '处理时间')
  w.save(szFileName)


# 存储数据到Excel
def record_transform_record( name ,count ):
  # 1. 获取文件名字
  szCurDate   = get_cur_date()
  szFileName  = szCurDate + '(微信转账记录).xls'
  szSheetName = 'Sheet1'

  # 2. 如果目标文件不存在则创建文件
  if not os.path.isfile(szFileName):
    creat_transform_account_record(szFileName , szSheetName)

  # 2. 打开Excel文件
  bk        = xlrd.open_workbook(szFileName , formatting_info=True)
  shxrange  = range(bk.nsheets)
  try:
   sh       = bk.sheet_by_name(szSheetName)
  except:
   sh     = bk.add_sheet(szSheetName)
   print ("no sheet in %s named Sheet1" % file)

  # 3. 获取行数和列数
  nrows     = sh.nrows

  # 4. 在新的一行中写入数据
  newWb   = copy(bk)
  newWs   = newWb.get_sheet(0)
  newWs.write(nrows, 0 , label = str(name))
  newWs.write(nrows, 1 , label = str(count)) 
  newWs.write(nrows, 2 , label = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))) 

  newWb.save(szFileName)



""" -------------------------------------------------------------------------------------------------"""
#                                               Excel处理
""" -------------------------------------------------------------------------------------------------"""
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
  szFileName 	= szCurDate + '(商品购买记录).xls'
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


""" -------------------------------------------------------------------------------------------------"""
#                                               判断当前步骤
""" -------------------------------------------------------------------------------------------------"""
## [[ 判断目标聊天步骤是否正常 ]] ##
# @param       nFirstStep          当前聊天大步骤
# @param       nSecondStep         当前聊天小步骤
# end --
def check_step( nFirstStep , nSecondStep ):
	if str(nFirstStep) not in Talkint_Step:
		return 0

	if str(nSecondStep) not in Talkint_Step[str(nFirstStep)]:
		return 0

	return 1


## [[ 判断聊天回复内容是否异常 ]] ##
# @param       nFirstStep          当前聊天大步骤
# @param       nSecondStep         当前聊天小步骤
# @param       szContent           玩家回复内容
# end --
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


## [[ 判断当前步骤是否有金钱限制 ]] ##
# @param       szFriendName        玩家名称
# @param       nFirstStep          当前聊天大步骤
# @param       nSecondStep         当前聊天小步骤
# @param       nFriendPay          朋友支付的金额
# @return      bool , bool , bool  参数一是否出现异常情况(参数异常),参数二为当前步骤是否存在金钱检测,参数三为如果当前步骤存在金钱检测那么玩家支付是否满足
# end --
def check_money_limit( szFriendName , nFirstStep , nSecondStep , nFriendPay ):
  # 1. 判断数据是否异常
  if check_step(nFirstStep , nSecondStep) != 1:
    print(r"check_money_limit failed for the wrong step : First{%s} , second{%s}" % (str(nFirstStep) , str(nSecondStep)))
    return (False , None , None)

  if (not isinstance(nFriendPay, int) and not isinstance(nFriendPay, float)) or nFriendPay < 0:
    print(r"check_money_limit failed for the wrong friend_pay{%s} , type{%s} cur step : First{%s} , second{%s}" % (str(nFriendPay) , type(nFriendPay) , str(nFirstStep) , str(nSecondStep)))
    return (False , None , None)

  # 2. 判断玩家当前是否有记录物品消耗总金额
  if UserList[szFriendName]['game_purchase_info'] is None or UserList[szFriendName]['game_purchase_info']['all_cost'] is None:
    print(r"check_money_limit failed for all_cost not record before cur step : First{%s} , second{%s}" % (str(nFirstStep) , str(nSecondStep)))
    return (False , None , None)

  nAllCost    = UserList[szFriendName]['game_purchase_info']['all_cost']
  if (not isinstance(nAllCost, int) and not isinstance(nAllCost, float)) or nAllCost < 0:
    print(r"check_money_limit failed for the wrong all_cost{%s} cur step : First{%s} , second{%s}" % (nAllCost , str(nFirstStep) , str(nSecondStep)))
    return (False , None , None)

  # ------------------------------------
  # 条件满足
  # 1. 如果当前步骤不需要检查金额
  if Talkint_Step[str(nFirstStep)][str(nSecondStep)]['special_handle'] != 3:
    return (True , False , None)

  # 3. 判断之前玩家的支付是否足够
  return (True , True , nFriendPay >= nAllCost)


## [[ 检测当前步骤 ]] ##
# @param       szFriendName        玩家名称
# @param       nFirstStep          当前聊天大步骤
# @param       nSecondStep         当前聊天小步骤
# @param       szContent           玩家回复内容
# @param       nFriendPay          朋友支付的金额
# end --
def check_cur_step( szFriendName , nFirstStep , nSecondStep , szContent , nFriendPay ):
  # 1. 判断当期步骤是否异常
  if check_step(nFirstStep , nSecondStep) != 1:
    print(r"check_cur_step failed for the wrong step : First{%s} , second{%s}" % (str(nFirstStep) , str(nSecondStep)))
    return False

  # 2. 判断聊天回复内容是否异常
  if check_reply_content(nFirstStep , nSecondStep , szContent) != 1:
    print(r"check_cur_step failed for the wrong replay{%s} cur step : First{%s} , second{%s}" % (str(szContent) , str(nFirstStep) , str(nSecondStep)))
    return False

  # 3. 判断当前步骤是否有金钱限制(数据异常或者支付金额不够)
  strResultList   = check_money_limit(szFriendName , nFirstStep , nSecondStep , nFriendPay)
  if not strResultList[0] or (strResultList[0] and strResultList[1] and not strResultList[2]):
    print(r"check_cur_step failed for the money{%s} cur step : First{%s} , second{%s}" % (str(nFriendPay) , str(nFirstStep) , str(nSecondStep)))
    return False

  # ------------------------------------
  # 条件满足
  return True


""" -------------------------------------------------------------------------------------------------"""
#                                             下一步处理
""" -------------------------------------------------------------------------------------------------"""
## [[ 获取目标步骤错误处理之后的步骤 ]] ##
# @param       nFirstStep          当前聊天大步骤
# @param       nSecondStep         当前聊天小步骤
# end --
def get_after_handle_error_step( nFirstStep , nSecondStep ):
	# 1. 判断数据是否异常
	if check_step(nFirstStep , nSecondStep) != 1:
		print('get_after_handle_error_step failed for the wrong step : First ' + str(nFirstStep) + ' Second ' + str(nSecondStep))
		return (0 , 0)

	# 2. 获取异常处理模式
	strWrongNextSteps 	= Talkint_Step[str(nFirstStep)][str(nSecondStep)]['wrong_jump_to_next']

	# 3. 返回结果
	return (strWrongNextSteps[0] , strWrongNextSteps[1])


## [[ 获取当前聊天步骤的下一步 ]] ##
# @param       nFirstStep          当前聊天大步骤
# @param       nSecondStep         当前聊天小步骤
# @param       bCurCheckResult     当前聊天步骤是否异常
# @param       szTalkingContent    玩家回复内容
# @return      bool , int , int    参数一为是否获取到下一步骤,参数二为下一步的大步骤,参数三为下一步的小步骤
# end --
def get_next_step( nFirstStep , nSecondStep , bCurCheckResult , szTalkingContent ):
  # 1. 获取当前的聊天步骤
  if check_step(nFirstStep , nSecondStep) != 1:
    print(r"get_next_step failed for the wrong step : First{%s} , second{%s}" % (str(nFirstStep) , str(nSecondStep)))
    return (False , 0 , 0)

  # 2. 如果玩家当前的聊天步骤异常,则获取异常跳转步骤
  if bCurCheckResult is False:
    strErrorHandle    = get_after_handle_error_step(nFirstStep , nSecondStep)
    return (True , strErrorHandle[0] , strErrorHandle[1])

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
    strNextStepList 	= get_after_handle_error_step(nNextFirstStep , nNextSecondStep)
    nNextFirstStep		= strNextStepList[0]
    nNextSecondStep		= strNextStepList[1]

  # 5. 判断新获取的步骤是否异常,如果异常强制结束
  if check_step(nNextFirstStep , nNextSecondStep) != 1:
    return (False , 0 , 0)

  # 6. 返回正常结果
  return (True , nNextFirstStep , nNextSecondStep)

# < 1 > 
# 重置目标玩家的对话步骤
def reset_talking_step(szFriendName):
	UserList[szFriendName]['step'] 					         = {}
	UserList[szFriendName]['step']['first_step'] 	   = 0			# 大步骤
	UserList[szFriendName]['step']['second_step'] 	 = 1			# 小步骤

# 重置目标玩家的游戏购买信息
def reset_game_purchase_info( szFriendName ):
  UserList[szFriendName]['game_purchase_info']					        = {}		
  UserList[szFriendName]['game_purchase_info']['role_name']		  = ''		# 游戏内的角色名字
  UserList[szFriendName]['game_purchase_info']['service_name']	= ''		# 大区名字
  UserList[szFriendName]['game_purchase_info']['item_list']		  = {}		# 购买商品
  UserList[szFriendName]['game_purchase_info']['item_answer']		= ''		# 购买商品回复信息
  UserList[szFriendName]['game_purchase_info']['all_cost']      = 0    # 商品总计应付金额
  UserList[szFriendName]['game_purchase_info']['friend_pay']    = 0    # 玩家实际支付的金额


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
  if 'friend_pay' in strMsgData:
    nFriendPay       = float(strMsgData['friend_pay'])

  szAnswer           = '数据异常,错误步骤 : '
  # 1. 如果玩家之前没有跟自己说过话
  if szFriendName not in UserList:
    print(r'friend_talk_to_me not exist before , name is {%s}'%(szFriendName))
    reset_friend_info(strMsgData)

  # 2. 如果玩家距离上次对话时间超过间隔时间则重置聊天步骤
  if nMsgTime - UserList[szFriendName]['msg_time'] > TALKING_INTERVAL_TIME:
    print(r'friend_talk_to_me reset for the time over the interval  , name is {%s}'%(szFriendName))
    reset_friend_info(strMsgData)
  
  # 3. 判断玩家当前步骤是否记录
  if UserList[szFriendName]['step'] is None:
    print(r'friend_talk_to_me reset for his step not exist  , name is {%s}'%(szFriendName))
    reset_friend_info(strMsgData)

  nCurFirstStep   = UserList[szFriendName]['step']['first_step']
  nCurSecondSetp  = UserList[szFriendName]['step']['second_step']


  # print(r"nCurFirstStep : First{%s} , nCurSecondSetp{%s}" % (str(nCurFirstStep) , str(nCurSecondSetp)))

  # 4. 判断玩家当前步骤是否异常
  bCurResult      = check_cur_step(szFriendName , nCurFirstStep , nCurSecondSetp , szTalkingContent , nFriendPay)

  # 5. 获取下一步信息
  strData         = get_next_step(nCurFirstStep , nCurSecondSetp , bCurResult , szTalkingContent)
  if not strData[0]:
    reset_friend_info(strMsgData)
    szAnswer      = szAnswer + ' : 1' + str(nCurFirstStep) + '  ' + str(nCurSecondSetp)
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
    UserList[szFriendName]['game_purchase_info']['friend_pay']    = nFriendPay

  # 3_4. 其它的暂不处理
  else:
    pass

  # 4. 记录步骤数据
  UserList[szFriendName]['step']['first_step']   = strData[1]
  UserList[szFriendName]['step']['second_step']  = strData[2]

  # print(r"nNextFirstStep : First{%s} , nNextSecondSetp{%s}" % (str(strData[1]) , str(strData[2])))

  # 5. 记录聊天时间
  UserList[szFriendName]['msg_time']				= nMsgTime

  # 6. 返回结果
  return szAnswer

  


#########################################
# 主函数
def Init():
  print('User:Init')







