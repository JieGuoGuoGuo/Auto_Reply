# 聊天步骤
# param					next_step
# 						下一步的聊天步骤,如果replay_content_type为3则下一步聊天步骤的步骤由玩家输入决定,其中0为默认

# param					replay_content_limit
# 						回复内容约束

# param 				wrong_jump_to_next
# 						当前对话错误跳转到目标步骤


# param 				replay_content_type
# 						0为普通的聊天回复(不用管),1为商品,2为大区名称,3为根据玩家的回复决定下一步的步骤,4为游戏内角色名称


# param					special_handle
# 						0为无任何特殊处理,1为总结购买信息并在此次对话中回复给玩家,2为记录数据到Excel中


Talkint_Step 						= {
	'0':
	{
		'1'					:
		{
			'talking_content'		:"",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (1 , 1),
			},
			'wrong_jump_to_next'	:(0 , 1),
			'replay_content_type'	:0,
			'special_handle'		:0,
		},
	},
	'1':
	{
		'1'					:
		{
			'talking_content'		:"你好,我休息去了~" + "\r\n" + "[购物]请回复'1'" + "\r\n" + "[聊天]请回复'2'" + "\r\n" + "[比特币]请回复'3'" + "\r\n",
			'replay_content_limit'	:['1' , '2' , '3'],
			'next_step'				:
			{
				'default'	: (2 , 1),
				'1'			: (2 , 1),
				'2'			: (2 , 2),
				'2'			: (2 , 3),
			},
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
			'next_step'				:
			{
				'default'	: (3 , 1),
			},
			'wrong_jump_to_next'	:(2 , 1),
			'replay_content_type'	:2,
			'special_handle'		:0,
		},
		
		'2'					:
		{
			'talking_content'	:"聊你妹啊!等我醒了弄死你!",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (1 , 1),
			},
			'wrong_jump_to_next'	:(1 , 1),
			'replay_content_type'	:0,
			'special_handle'		:0,
		},

		'3'					:
		{
			'talking_content'	:"功能开发中!",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (1 , 1),
			},
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
			'next_step'				:
			{
				'default'	: (4 , 1),
			},
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
			'next_step'				:
			{
				'default'	: (5 , 1),
			},
			'wrong_jump_to_next'	:(4 , 1),
			'replay_content_type'	:1,
			'special_handle'		:1,
		}
	},
	'5':
	{
		'1'					:
		{
			'talking_content'	:"\r\n" + "----------------------------------" + "\r\n" + "[重新输入]请回复'1'\r\n" + "[确	认]请回复'2'\r\n" + "[退出本次交易]请回复'3'\r\n",
			'replay_content_limit'	:['1' , '2'],
			'next_step'				:
			{
				'default'	: (0 , 1),
				'1'			: (2 , 1),
				'2'			: (6 , 1),
				'3'			: (0 , 1),
			},
			'wrong_jump_to_next'	:(5 , 2),
			'replay_content_type'	:3,
			'special_handle'		:0,
		},
		'2'					:
		{
			'talking_content'	:"输入错误" + '\r\n' + "[重新输入]请回复'1'\r\n" + "[确    认]请回复'2'\r\n" + "[退出本次交易]请回复'3'\r\n",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (0 , 1),
				'1'			: (2 , 1),
				'2'			: (6 , 1),
				'3'			: (0 , 1),
			},
			'wrong_jump_to_next'	:(5 , 2),
			'replay_content_type'	:3,
			'special_handle'		:0,
		}
	},
	'6':
	{
		'1'					:
		{
			'talking_content'	:"系统已接收到请求,请回复任意内容,继续本次操作",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (7 , 1),
			},
			'wrong_jump_to_next'	:(7 , 1),
			'replay_content_type'	:0,
			'special_handle'		:2,
		}
	},
	'7':
	{
		'1'					:
		{
			'talking_content'	:"正在处理,请到游戏中确认,谢谢合作",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (0 , 1),
			},
			'wrong_jump_to_next'	:(0 , 1),
			'replay_content_type'	:0,
			'special_handle'		:0,
		}
	},
}