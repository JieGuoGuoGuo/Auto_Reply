# 聊天步骤
# param					next_step
# 						下一步的聊天步骤,如果replay_content_type为3则下一步聊天步骤的步骤由玩家输入决定,其中0为默认

# param					replay_content_limit
# 						回复内容约束

# param 				wrong_jump_to_next
# 						当前对话错误跳转到目标步骤

# param 				super_jump_to_next
# 						超级用户跳转到目标步骤

# param 				replay_content_type
# 						0为普通的聊天回复(不用管),1为商品,2为大区名称,3为根据玩家的回复决定下一步的步骤,4为游戏内角色名称


# param					special_handle
# 						0为无任何特殊处理,1为总结购买信息并在此次对话中回复给玩家,2为记录数据到Excel中,3为检查玩家转账,4为还原玩家的步骤

# param					super_handle
# 						0为不做任何处理,1为当前步骤确认为超级用户,2为重置超级用户数据


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
            'super_handle'		    :0,
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
				'1'			: {'default' : (2 , 1)},
				'2'			: {'default' : (2 , 2)},
				'3'			: {'default' : (2 , 3)},
			},
			'wrong_jump_to_next'	:(1 , 1),
			'replay_content_type'	:3,
            'super_handle'		    :0,
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
            'super_handle'		    :0,
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
            'super_handle'		    :0,
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
            'super_handle'		    :0,
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
            'super_handle'		    :0,
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
            'super_handle'		    :0,
			'special_handle'		:1,
		}
	},
	'5':
	{
		'1'					:
		{
			'talking_content'	:"\r\n" + "----------------------------------" + "\r\n" + "[重新输入]请回复'1'\r\n" + "[确	认]请回复'2'\r\n" + "[退出本次交易]请回复'3'\r\n",
			'replay_content_limit'	:['1' , '2' , '3'],
			'next_step'				:
			{
				'default'	: (0 , 1),
				'1'			: {'default' : (2 , 1)},
				'2'			: {'default' : (6 , 1) , 'super' : (7 , 1)},
				'3'			: {'default' : (0 , 1)},
			},
			'wrong_jump_to_next'	:(5 , 2),
			'replay_content_type'	:3,
            'super_handle'		    :0,
			'special_handle'		:0,
		},
		'2'					:
		{
			'talking_content'	:"输入错误" + '\r\n' + "[重新输入]请回复'1'\r\n" + "[确认]请回复'2'\r\n" + "[退出本次交易]请回复'3'\r\n",
			'replay_content_limit'	:['1' , '2' , '3'],
			'next_step'				:
			{
				'default'	: (0 , 1),
				'1'			: {'default' : (2 , 1)},
				'2'			: {'default' : (6 , 1) , 'super' : (7 , 1)},
				'3'			: {'default' : (0 , 1)},
			},
			'wrong_jump_to_next'	:(5 , 2),
			'replay_content_type'	:3,
            'super_handle'		    :0,
			'special_handle'		:0,
		}
	},
	'6':
	{
		'1'					:
		{
			'talking_content'	:"系统已接收到请求,请转账(暂时只支持转账,红包功能敬请期待)",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (7 , 1),
			},
			'wrong_jump_to_next'	:(6 , 1),
			'replay_content_type'	:0,
            'super_handle'		    :0,
			'special_handle'		:3,
		}
	},
	'7':
	{
		'1'					:
		{
			'talking_content'	:"请回复任意内容,继续本次操作",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (8 , 1),
			},
			'wrong_jump_to_next'	:(0 , 1),
			'replay_content_type'	:0,
            'super_handle'		    :0,
			'special_handle'		:2,
		},

		'2'					:
		{
			'talking_content'	:"支付出现问题,系统已记录,待会本人将会联系你",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (0 , 1),
			},
			'wrong_jump_to_next'	:(0 , 1),
			'replay_content_type'	:0,
            'super_handle'		    :0,
			'special_handle'		:0,
		}
	},
	'8':
	{
		'1'					:
		{
			'talking_content'	:"正在处理,稍后请到游戏中确认",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (0 , 1),
			},
			'wrong_jump_to_next'	:(0 , 1),
			'replay_content_type'	:0,
            'super_handle'		    :0,
			'special_handle'		:0,
		}
	},
    '100':
	{
		'1'					:
		{
			'talking_content'	:"触发开启超级用户指令,请输入超级用户密码",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (101 , 1),
			},
			'wrong_jump_to_next'	:(101 , 2),
			'replay_content_type'	:0,
            'super_handle'		    :0,
			'special_handle'		:0,
		}
	},
    '101':
	{
		'1'					:
		{
			'talking_content'	:"验证密码中\r\n请回复任意内容,继续本次操作",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (102 , 1),
			},
			'wrong_jump_to_next'	:(0 , 1),
			'replay_content_type'	:0,
            'super_handle'		    :1,
			'special_handle'		:4,
		},
        '2'					:
		{
			'talking_content'	:"验证密码中\r\n请回复任意内容,继续本次操作",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (102 , 2),
			},
			'wrong_jump_to_next'	:(0 , 1),
			'replay_content_type'	:0,
            'super_handle'		    :2,
			'special_handle'		:4,
		}
	},
    '102':
	{
		'1'					:
		{
			'talking_content'	:"超级用户开启成功\r\n请回复任意内容,继续本次操作",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (0 , 1),
			},
			'wrong_jump_to_next'	:(0 , 1),
			'replay_content_type'	:0,
            'super_handle'		    :0,
			'special_handle'		:0,
		},
        '2'					:
		{
			'talking_content'	:"超级用户开启失败\r\n请回复任意内容,继续本次操作",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (0 , 1),
			},
			'wrong_jump_to_next'	:(0 , 1),
			'replay_content_type'	:0,
            'super_handle'		    :0,
			'special_handle'		:0,
		}
	},
    '1000':
	{
		'1'					:
		{
			'talking_content'	:"",
			'replay_content_limit'	:'',
			'next_step'				:
			{
				'default'	: (0 , 0),
			},
			'wrong_jump_to_next'	:(0 , 0),
			'replay_content_type'	:0,
            'super_handle'		    :0,
			'special_handle'		:0,
		}
	},

}