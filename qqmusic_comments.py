import time
import selenium
import json
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

driver = webdriver.Chrome()  # 创建Edge浏览器实例
driver.get(r'https://y.qq.com/n/ryqq/songDetail/002B22Sf0TKFMs')  # 打开网页

try:
    scroll_count = 0  #计数：没滚动60次保存一次结果
    while True:
        # 向下滚动2000像素
        driver.execute_script("window.scrollBy(0, 2000);")
        # 等待2秒
        time.sleep(2)
        # 增加滚动计数
        scroll_count += 1
        if (scroll_count%60 == 0):
            # 获取当前页面的 HTML 内容并保存
            name = time.strftime('%Y-%m-%d_%H：%M：%S')
            path = f'./QQ_music/HTML/page.html'
            page_source = driver.page_source
            with open(path, 'w', encoding='utf-8') as file:
                file.write(page_source)
    
            # 打开保存的 HTML
            with open(path, 'r', encoding='utf-8') as file:
                html_content = file.read()
    
            # 使用Beautiful Soup解析HTML
            soup = BeautifulSoup(html_content, 'lxml')
            try:
                # 查找包含评论的<ul>元素
                contents = soup.find_all('li', class_='c_b_normal')
                
                # 初始化列表，用于存储四个指标的数据
                data = []
                # 遍历每条评论
                for content in contents:
                    try:
                        username = content.find('a', class_='c_tx_thin').text.strip()  # 提取网名
                    except:
                        username = '暂无数据'
                    try:
                        comment_content = content.find('p', class_='comment__text').text.strip()  # 提取评论内容
                    except:
                        comment_content = '暂无数据'
                    try:
                        timestamp = content.find('div', class_='comment__date').text.strip()  # 提取时间、地点
                        split_timestamp = timestamp.split('来自', 1)
                        try:
                            times = split_timestamp[0]  # 时间
                        except:
                            times = '暂无数据'
                        try:
                            location = split_timestamp[1]
                        except:
                            location = '暂无数据'
                    except:
                        continue
                    
                    # 将四个指标的数据存入字典
                    comment_data = {
                        'Username': username,
                        'CommentContent': comment_content,
                        'Time': times,
                        'Location': location
                    }
                
                    # 将字典添加到数据列表
                    data.append(comment_data)
                
                # 创建DataFrame并保存
                df = pd.DataFrame(data)
                df.to_csv(f'./QQ_music/{name}.csv', index=False, encoding='utf8')
    
            except:
                print(f'错误{name}')

except KeyboardInterrupt:
    # 捕获键盘中断（Ctrl+C），例如用户手动停止脚本
    pass
    
finally:
    # 关闭浏览器
    driver.quit()
