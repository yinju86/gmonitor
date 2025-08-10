import time
import gpcx
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
USERNAME = config["USERNAME"]
PASSWORD = config["PASSWORD"]
GROUP_NAME = config["GROUP_NAME"]
URL = config["URL"]
# 启动浏览器
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

def login_gree():
    driver.get("https://g.gree.com")

    # 等待登录页面加载并填入账号密码
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "account")))

    driver.find_element(By.ID, "account").send_keys(USERNAME)
    driver.find_element(By.ID, "pwd").send_keys(PASSWORD)
    # 点击登录按钮（视页面结构可能需要调整）
    driver.find_element(By.CLASS_NAME, "btn-login").click()

    # 登录后等待主页加载
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "nav_list_item")))
    print("✅ 登录成功")

def go_to_messages():
    # 点击“消息”标签（用 JS 强制点击）
    message_tab = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '//li[@class="nav_list_item" and @data-url="/im/xiaoxi/"]'))
    )
    driver.execute_script("arguments[0].click();", message_tab)

    # 切换 iframe

    print("✅ 进入消息页面")


def scroll_and_click_group( group_id, max_scrolls=30):
    message_tab = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '//li[@class="nav_list_item" and @data-url="/im/xiaoxi/"]'))
    )
    driver.execute_script("arguments[0].click();", message_tab)

    # 等待 iframe 出现并切换
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@data-url="/im/xiaoxi/"]'))
    )
    print("✅ 已切换到消息 iframe")
    print("🧭 等待群列表容器加载...")
    container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//ul[contains(@class, "im-session-list")]'))
    )

    # 模拟鼠标悬停区域
    actions = ActionChains(driver)
    actions.move_to_element_with_offset(container, 10, 200).perform()
    time.sleep(0.3)

    seen_ids = set()

    for _ in range(max_scrolls):
        try:
            group_li = container.find_element(By.ID, group_id)
            driver.execute_script("arguments[0].scrollIntoView();", group_li)
            time.sleep(0.3)
            group_li.click()
            print(f"✅ 成功点击群 {group_id}")
            return True
        except:
            container.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.6)

            new_ids = [e.get_attribute("id") for e in container.find_elements(By.XPATH, './li')]
            if set(new_ids) <= seen_ids:
                print("🚫 滚动到底，未找到目标群")
                return False
            seen_ids.update(new_ids)

    print("❌ 多次滚动后未找到目标群")
    return False

def scroll_and_click_group_by_name(group_name, max_scrolls=30):
    message_tab = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '//li[@class="nav_list_item" and @data-url="/im/xiaoxi/"]'))
    )
    driver.execute_script("arguments[0].click();", message_tab)

    # 等待 iframe 出现并切换
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@data-url="/im/xiaoxi/"]'))
    )
    print("✅ 已切换到消息 iframe")
    print("🧭 等待群列表容器加载...")
    container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//ul[contains(@class, "im-session-list")]'))
    )

    actions = ActionChains(driver)
    actions.move_to_element_with_offset(container, 10, 200).perform()
    time.sleep(0.3)

    seen_names = set()

    for _ in range(max_scrolls):
        try:
            group_li = None
            group_items = container.find_elements(By.XPATH, './li')
            for li in group_items:
                name_span = li.find_element(By.XPATH, './/span[contains(@class, "name-list")]')
                if name_span.text.strip() == group_name:
                    group_li = li
                    break
            if group_li:
                driver.execute_script("arguments[0].scrollIntoView();", group_li)
                time.sleep(0.3)
                group_li.click()
                print(f"✅ 成功点击群 {group_name}")
                return True
        except Exception as e:
            pass

        container.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.6)

        new_names = [li.find_element(By.XPATH, './/span[contains(@class, "name-list")]').text.strip() for li in container.find_elements(By.XPATH, './li')]
        if set(new_names) <= seen_names:
            print("🚫 滚动到底，未找到目标群")
            return False
        seen_names.update(new_names)

    print("❌ 多次滚动后未找到目标群")
    return False

def handle_new_message(content):

    if content.startswith("查"):
        print("🔍 处理查询指令")
        gpcxsh(content[1:])


def extract_latest_message():
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//iframe[@data-url="/im/xiaoxi/"]'))
    )

    # 记录程序启动时间
    start_time = datetime.now()

    print("🔄 开始循环监听新消息...")
    last_content = None
    while True:
        my_messages = driver.find_elements(By.XPATH, '//div[contains(@class, "chat-item")]')
        if my_messages:
            latest = my_messages[-1]
            try:
                # 获取消息发送时间
                send_body = latest.find_element(By.XPATH, './/div[contains(@class,"send-body")]')
                send_time_str = send_body.get_attribute("data-sendtime")  # 格式如 "2025-07-20 13:41:04"
                content = send_body.find_element(By.XPATH, './/div[contains(@class,"send-content")]').text
                msg_time = datetime.strptime(send_time_str, "%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(f"❌ 读取消息或时间失败: {e}")
                content = "(无法读取内容)"
                msg_time = None

            # 只处理程序启动后发出的消息
            if msg_time and msg_time >= start_time and content != last_content:
                print("📨 检测到新发言：")
                print(f"💬 内容：{content}")
                try:
                    handle_new_message(content)
                except Exception as e:
                    print(f"❌ 处理新消息失败: {e}")
                last_content = content
        else:
            print("❌ 没有找到我的发言")
        time.sleep(2)  # 每2秒检查一次





def gpcxsh(k):
    k = gpcx.get_stock_info(k)[0]['code']
    msg= gpcx.get_stock_price(k)
    gpcx.post_json(msg,URL)





def main():
    login_gree()
    go_to_messages()
    if scroll_and_click_group_by_name(GROUP_NAME):
        extract_latest_message()


if __name__ == "__main__":
    main()
