#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from selenium.webdriver.support.ui import Select, WebDriverWait
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, NoSuchWindowException
from selenium.webdriver.support import expected_conditions as EC
import re

URL = 'https://goodinfo.tw/tw2/StockList.asp?MARKET_CAT=%E7%86%B1%E9%96%80%E6%8E%92%E8%A1%8C&INDUSTRY_CAT=%E6%88%90%E4%BA%A4%E5%BC%B5%E6%95%B8+%28%E9%AB%98%E2%86%92%E4%BD%8E%29%40%40%E6%88%90%E4%BA%A4%E5%BC%B5%E6%95%B8%40%40%E7%94%B1%E9%AB%98%E2%86%92%E4%BD%8E'

num=200 # 篩選數量 最多300
K_max=20 # 篩選 K 最大
D_max=50 # 篩選 D 最大

# 创建 Edge WebDriver 對象
driver = webdriver.Edge()

# 打開網頁
driver.get(URL)

# 篩選 KD
select_element = driver.find_element(By.ID, 'selSHEET')
select = Select(select_element)
select.select_by_value('KD指標')

volume_num = 0
i_num = np.array([], dtype=int)
while volume_num < num:  # 設置循環條件
    try:
        # 等待 K 和 D 元素加载完成
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="row{volume_num}"]/td[11]/nobr/a')))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="row{volume_num}"]/td[12]/nobr/a')))

        print(volume_num+1,'/',num)
        volume_num += 1
        # 獲取 K 和 D 元素
        try:
            K_element = driver.find_element(By.XPATH, f'//*[@id="row{volume_num}"]/td[11]/nobr/a')
            K_text = K_element.text  # 使用 .text 属性獲取可見文本
            D_element = driver.find_element(By.XPATH, f'//*[@id="row{volume_num}"]/td[12]/nobr/a')
            D_text = D_element.text  # 使用 .text 属性獲取可見文本
            # 從文本中提取 K 值和 D 值的前兩個數字
            K_match = re.match(r'\d+', K_text)
            D_match = re.match(r'\d+', D_text)
            
            if K_match and D_match:
                K_value = K_match.group()[:2] if K_match.group() else None  # 提取前兩個數字
                D_value = D_match.group()[:2] if D_match.group() else None  # 提取前兩個數字
                if K_value is not None and D_value is not None:
                    if len(K_value) == 2 and len(D_value) == 2:  # 只處理兩位數的情况
                        if int(K_value) < K_max and int(D_value) < D_max:
                            i_num=np.append(i_num,volume_num)
        except StaleElementReferenceException:
            print("元素過時，重新嘗試...")
            time.sleep(1)  # 暂停 1 秒
            continue
    except (TimeoutException, NoSuchElementException):
        print("找不到元素或超時")
    except NoSuchWindowException:
        print("視窗已關閉")
        break


# 查看 PER 是否存在
# 選擇指定值的選項（在這裡選擇 "交易狀況"）
select_element = driver.find_element(By.ID, 'selSHEET')
select = Select(select_element)
select.select_by_value('交易狀況')

i=1
volume_num = 0
stock_names_lessETP = np.array([], dtype=int) # 創建一個空列表，用於儲存股票號碼
try:
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="row1"]/td[16]/nobr')))
except TimeoutException:
    pass
for volume_num in i_num:
    try:
        print(i,'/',len(i_num))
        i += 1
        stock_PER = driver.find_elements(By.XPATH, f'//*[@id="row{volume_num}"]/td[17]/nobr')
        
        if stock_PER:  # 检查 stock_PER 是否存在
            stock_names_lessETP=np.append(stock_names_lessETP,volume_num)  # 將股票排號添加到列表中
    except TimeoutException:
        pass


# 查看 毛利率 是否存在
select_element = driver.find_element(By.ID, 'selSHEET')
select = Select(select_element)
select.select_by_value('季獲利能力')

i=1
volume_num = 0
stock_names_GP = np.array([]) # 创建一個空列表，用于儲存股票名稱
for volume_num in stock_names_lessETP:
    try:
        print(i,'/',len(stock_names_lessETP))
        i += 1
        WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="hrow{volume_num}"]/td[3]/nobr/a')))
    
        stock_name = driver.find_element(By.XPATH, f'//*[@id="row{volume_num}"]/td[3]/nobr/a')
        
        stock_GP = driver.find_elements(By.XPATH, f'//*[@id="row{volume_num}"]/td[12]/nobr')
        
        if stock_GP:  # 检查 毛利率 是否存在
            stock_names_GP=np.append(stock_names_GP,stock_name.text)  # 將股票名稱添加到列表中
        else:
            pass
    except StaleElementReferenceException:
        print("元素已过时，重新尝试...")
        pass
    except TimeoutException:
        pass




print("篩選出的股票数量：", len(stock_names_GP))
print("篩選出的股票名稱：", stock_names_GP)


# In[ ]:




