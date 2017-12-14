#coding:utf-8
import re
import time 
import string 
import xlrd


#########################################
# 初始化数据

ItemList = {}

# 初始化数据
#########################################



# 获取物品总费用
def get_item_cost(content): 
  # 1. 解析字符串
  b_1 = re.compile("[\u4e00-\u9fa5]*")
  b_2 = re.compile('[0-9]*')
  c_1 = b_1.findall(content)
  c_2 = b_2.findall(content)
  
  # 2. 获取物品的单价
  szItemName = ''
  nSingleMoney = 0
  for i in  c_1:
    if i != '':
      szItemName = i
    
    if i in ItemList:
      nSingleMoney = ItemList.get(i)

  # 3. 获取物品的数量
  nCount = 0
  for i in  c_2:
    if i.isdigit():
    	nCount=int(i)

  return (szItemName , nSingleMoney , nCount)

# 解析数据
def analysis_data(content):
  # 1. 去除空格
  p=re.compile('\s+')
  new_string=re.sub(p,'',content)

  # 2. 截取信息
  b = re.compile("[\u4e00-\u9fa5]+[0-9]*")
  c = b.findall(new_string)
  nAllCost = 0
  send_msg = ''
  strItemDetial   = {}
  for i in  c:

    # 3. 获取单个商品的信息
    (szName , nCost , nBuyCount) = get_item_cost(i)

    # 4. 拼接字符串
    # 4_1. 如果物品有单价
    if nCost > 0:

      # 4_1_1. 回复内容拼接
      szSingleContent   = szName + ' : ' + str(nCost) + ' * ' + str(nBuyCount) + "\r\n"

      # 4_1_2. 记录玩家购买数据
      if szName not in strItemDetial:
        strItemDetial[szName] = 0

      strItemDetial[szName] = strItemDetial[szName] + nBuyCount

    # 4_2. 如果物品没有单价
    else:
      szSingleContent   = szName + ' : ' + '暂无此产品!' + "\r\n"

    # 5. 拼接总的字符串
    send_msg          = send_msg + szSingleContent

    # 6. 计算总金额
    nAllCost          = nBuyCount * nCost + nAllCost

  send_msg            = send_msg + "总计 : " + str(nAllCost)
  return (nAllCost , send_msg , strItemDetial)


# 读取Excel
def excel_table_byindex(file= 'Test.xlsx'):
  # 1. 打开Excel文件
  bk        = xlrd.open_workbook(file)
  shxrange  = range(bk.nsheets)
  try:
   sh       = bk.sheet_by_name("Sheet1")
  except:
   print ("no sheet in %s named Sheet1" % file)

  # 2. 获取行数和列数
  nrows     = sh.nrows
  ncols     = sh.ncols
  # print ('nrows : ' + str(nrows))
  # print ('ncols : ' + str(ncols))
  # print ('first : ' + str(sh.cell_value(0 , 0)))
    
  # 3. 获取各行数据
  nTempRow  = 0
  for i in range(nrows):
    for i_1 in range(ncols):

      # 3_1. 获取目标行目标列数据,如果是装备名称且不是最后一列
      cur_cell_value  = sh.cell_value(i , i_1)
      if cur_cell_value != '' and isinstance(cur_cell_value, str) and i_1 != ncols - 1:
        nxt_cell_value  = sh.cell_value(i , i_1 + 1)

        # 3_2. 如果目标行目标列的后面一列是数字
        if nxt_cell_value != '' and (isinstance(nxt_cell_value, int) or isinstance(nxt_cell_value, float)):
          ItemList[cur_cell_value] = nxt_cell_value

# 主函数
def Init():
  # 1. 解析Excel文件
  excel_table_byindex()
  # print(ItemList)
  print('BuyItem:Init')




#########################################
# 测试数据
# string = '鞋子 2 裤子3 饰品 6'
# send_msg = analysis_data(string)
# print (send_msg[1])