#coding:utf-8
import re
import time 
import string 
import xlrd
import BuyItem

#########################################
# 初始化数据

UserList 			= {}

# next_by_replay 		是否根据对方的回复进行下一步对话(对方的回复决定下一步聊天的步骤 )
# 0为否 , 1为是的

# next_step 			如果由系统决定下一步聊天步骤(即next_by_replay为0),那么下一步的聊天步骤

# replay_content_limit 	回复内容约束

# wrong_handle_mode 	当前对话错误处理方式
# 0为结束当前对话 , 1为继续当前这一步聊天 , 2为返回上一步	

# wrong_talking_next	如果聊天异常(即wrong_handle_mode为1或者2),则跳转的目标步骤

Talkint_Step 	= {
	'0':
	{
		'1'					:
		{
			'talking_content'		:"",
			'next_by_replay'		:0,
			'replay_content_limit'	:'',
			'next_step'				:1,
			'wrong_handle_mode'		:1,
			'wrong_talking_next'	:1,
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
			'next_step'				:-1,
			'wrong_handle_mode'		:1,
			'wrong_talking_next'	:1,
			'calculate_price'		:0,
		},
	},
	'2':
	{
		'1'					:
		{
			'talking_content'	:"请输入大区完整名称" + "\r\n" + "如:龙门客栈",
			'next_by_replay'		:0,
			'replay_content_limit'	:['龙门客栈' , '龙门客栈'],
			'next_step'				:1,
			'wrong_handle_mode'		:1,
			'wrong_talking_next'	:1,
			'calculate_price'		:0,
		},
		
		'2'					:
		{
			'talking_content'	:"聊你妹啊!等我醒了弄死你!",
			'next_by_replay'		:0,
			'replay_content_limit'	:'',
			'next_step'				:-1,
			'wrong_handle_mode'		:2,
			'wrong_talking_next'	:1,
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
			'next_step'				:1,
			'wrong_handle_mode'		:1,
			'wrong_talking_next'	:1,
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
			'next_step'				:-1,
			'wrong_handle_mode'		:0,
			'wrong_talking_next'	:1,
			'calculate_price'		:1,
		}
	},
}

# 初始化数据
#########################################




#########################################
# 逻辑处理





# < 2 > 继续对话
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

	nNextFirstStep 			= nFirstStep + 1
	nNextSecondStep 		= 0

	# 2. 获取异常处理模式
	nWrongHandleMode 	= Talkint_Step[str(nFirstStep)][str(nSecondStep)]['wrong_handle_mode']

	# 3_1. 如果处理方式为结束当前聊天
	if nWrongHandleMode == 0:
		return (0 , 0)

	# 3_2. 如果处理方式为继续当前这一步聊天
	elif nWrongHandleMode == 1:
		nNextFirstStep	= nFirstStep
		nNextSecondStep = Talkint_Step[str(nFirstStep)][str(nSecondStep)]['wrong_talking_next']

	# 3_3. 如果处理方式为返回上一步聊天
	elif nWrongHandleMode == 2:
		nNextFirstStep	= nFirstStep - 1
		nNextSecondStep = Talkint_Step[str(nFirstStep)][str(nSecondStep)]['wrong_talking_next']

	# 3_4. 错误的方式
	else:
		print('get_after_handle_error_step failed for the wrong handle mode : First ' + str(nFirstStep) + ' Second ' + str(nSecondStep))
		return (0 , 0)

	# 4. 返回结果
	return (nNextFirstStep , nNextSecondStep)


# 有朋友与自己继续对话
def get_next_step( strStepList , szTalkingContent ):
	print('User:get_next_step -- Begin')
	print(szTalkingContent)
	print(strStepList)

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
	nNextFirstStep 			= nFirstStep + 1
	nNextSecondStep 		= 0

	# 3_1. 如果是根据玩家的回复决定下一步
	if Talkint_Step[str(nFirstStep)][str(nSecondStep)]['next_by_replay'] == 1:
		nNextSecondStep		= szTalkingContent

	# 3_2. 如果由系统决定决定下一步
	else:
		nNextSecondStep		= Talkint_Step[str(nFirstStep)][str(nSecondStep)]['next_step']

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
def friend_talk_to_me(szFriendName , szTalkingContent):
  # 1. 如果玩家之前没有跟自己说过话
  if szFriendName not in UserList:
  	UserList[szFriendName]							= {}
  	reset_talking_step(szFriendName)

  # 2. 获取玩家下一个聊天步骤
  strData = get_next_step(UserList[szFriendName]['step'] , szTalkingContent)
  print(strData)

  # 3. 如果获取下一步聊天步骤正常
  szAnswer= ''
  if strData[0] == 1:

  	# 3_1. 记录数据
  	UserList[szFriendName]['step']['first_step'] 	= strData[1]
  	UserList[szFriendName]['step']['second_step'] 	= strData[2]

  	# 3_2. 获取回复内容
  	szAnswer = Talkint_Step[str(strData[1])][str(strData[2])]['talking_content']

  	# 3_3. 如果玩家的内容需要计算
  	if Talkint_Step[str(strData[1])][str(strData[2])]['calculate_price'] == 1:
  		strItemAnswer 	= BuyItem.analysis_data(szTalkingContent)
  		szAnswer 		= szAnswer + strItemAnswer[1]

  # 4. 如果下一步聊天异常
  else:

  	# 4_1. 重置聊天步骤
  	reset_talking_step(szFriendName)

  # 5. 返回结果
  return szAnswer


#########################################
# 主函数
def Init():
  print('User:Init')







