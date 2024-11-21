import re
from playwright.sync_api import Playwright, sync_playwright, expect
import time
import json
import pandas as pd

def login(page, url, username, password):
    page.goto(url)
    page.get_by_role("link", name="ZenTao Pro").click()
    page.locator("#account").click()
    page.locator("#account").fill(username)
    page.locator("#account").press("Tab")
    page.locator("input[name=\"password\"]").fill(password)
    page.get_by_role("button", name="登录").click()
    page.get_by_role("link", name="日程", exact=True).hover()
    page.get_by_role("link", name="日志").click()
    page.get_by_role("link", name="所有日志").click()

def add_log(page, date, tasks, addIfExist=False):
    print(f"日期: {date}")

    page.locator("#date").fill(date)
    page.locator("#date").press("Enter")
    page.locator("#date").press("Enter")
    time.sleep(1)
    
    table = page.locator("form.table-effort")
    
    # 检查表格下是否有数据
    rows = table.locator('tbody tr')  # 获取所有行
    if not addIfExist and rows.count() > 0:  # 判断表格中是否存在行
        print(f"表格有数据{rows.count()}条")
    else:
        page.get_by_role("link", name=" 新增日志").click()
        
        time.sleep(1.5)
        
        for idx, task in enumerate(tasks):
            print(f"任务: {task['task']}, 工时: {task['hours']}")
        
            # 定位到第一行（假设要修改第一行的数据）
            page.frame_locator("iframe[name=\"iframe-triggerModal\"]").locator("input[name=\"date\"]").fill(date)
            page.frame_locator("iframe[name=\"iframe-triggerModal\"]").locator("input[name=\"date\"]").press("Enter")


            row = page.frame_locator("iframe[name=\"iframe-triggerModal\"]").locator(f'table#objectTable tbody tr:nth-child({idx+1})')

            # 设置第一列的数据（ID列）
            row.locator('td:nth-child(2) input').fill(task['task'])  # 修改ID为100

            # 设置第四列的数据（项目列）
            row.locator('td:nth-child(6) input').fill(str(task['hours']))  # 修改项目为"项目A"
            
            time.sleep(1.5)
            
        # 提交保存按钮
        page.frame_locator("iframe[name=\"iframe-triggerModal\"]").get_by_role("button", name="保存").click()
        
        time.sleep(1)


def submit_git_log():
    data_path = 'work_summary.json'
    with open(data_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("about:blank")
        login(page,base_url,username,password )
        
        
        # 循环遍历字典
        for date, tasks in data.items():
            if not tasks:
                continue
            
            add_log(page, date, tasks)
                

        # ---------------------
        context.close()
        browser.close()

base_url = 'http://chandao.abc.com'
username = 'abc'
password = 'abc'


def edit_git_log():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("about:blank")
        login(page,base_url,username,password )
        df = pd.read_excel('分组日志详情页.xlsx')
        for date in df['日期'].tolist():
            print(f"日期: {date}")

            page.locator("#date").fill(date)
            page.locator("#date").press("Enter")
            page.locator("#date").press("Enter")
            time.sleep(1)
            
            table = page.locator("form.table-effort")
            
            # 检查表格下是否有数据
            rows = table.locator('tbody tr')  # 获取所有行
            if rows.count() == 1:  # 判断表格中是否存在行
                print(f"开始修改禅道日志")
                page.get_by_title("更新日志").click()
                work = page.frame_locator("iframe[name=\"iframe-triggerModal\"]").locator("#work").input_value()
                page.frame_locator("iframe[name=\"iframe-triggerModal\"]").locator("#consumed").fill("4")
                page.frame_locator("iframe[name=\"iframe-triggerModal\"]").get_by_role("button", name="保存").click()
                
                time.sleep(0.5)
                
                task = {'task': work,'hours': '4'}
                add_log(page, date, [task], True)
                
                
                
                
edit_git_log()