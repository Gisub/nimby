import time, random, datetime
import os
import requests
from account_list import *
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tractor_API
import traceback

def process_kill(host):
    os.popen("rsh {h} python /core/Linux/APPZ/shell/nimby/check/yslow.py -a".format(h=host))
    os.popen("rsh {h} rm -rf /var/tmp/*.mb /var/tmp/Maya*" \
             " /var/tmp/Pixar /var/tmp/houdini_temp /var/tmp/*katana".format(h=host))


# Start Log Date
folder_prepix = datetime.datetime.now().strftime('%Y-%m')
prepix = datetime.datetime.now().strftime('%y-%m-%d')
log_file = '/core/log/nimby/{0}/{1}.txt'.format(folder_prepix, prepix)
if not os.path.isdir(os.path.dirname(log_file)):
    os.mkdir(os.path.dirname(log_file))
start_prepix = datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')
os.system('echo "===================================" >> {0}'.format(log_file))
os.system('echo "[Start Log] {0}\n" >> {1}'.format(start_prepix, log_file))

# Web browser setting
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
PROXY = "192.168.10.15:3128"

# Website check
url = "https://m83.daouoffice.com/login"
headers = {"user-agent": user_agent}
proxies = {'http': PROXY, 'https': PROXY}
res = requests.get(url, headers=headers, proxies=proxies)
res.raise_for_status()
print('------Web crawling Start------')

# Web Scraping with Chrome.
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('window-size=1920x1080')
options.add_argument('user-agent=%s' % user_agent)
options.add_argument('--proxy-server=%s' % PROXY)

try:
    browser = webdriver.Chrome('/core/Linux/APPZ/shell/nimby/chromedriver', options=options)
    browser.get(url)
    browser.find_element_by_xpath('//*[@id="language_select"]/select/option[text()="English"]').click()
    time.sleep(random.uniform(1, 3))

    input_account = ' \
        document.getElementById("username").value = "{id}"; \
        document.getElementById("password").value = "{pw}"; \
    '.format(id=DAOUOFFICE_ID, pw=DAOUOFFICE_PASSWORD)
    browser.execute_script(input_account)
    browser.find_element_by_id("login_submit").click()
    print('Accessing the DaouOffice..')

    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn_oganization')))
    browser.find_element_by_class_name('btn_oganization').click()
    print('Loading..')
    time.sleep(1)

    soup = BeautifulSoup(browser.page_source, 'lxml')
    while True:
        tasks = soup.find_all("li", attrs={"class": ["jstree-closed", "jstree-closed jstree-last"]})
        if len(tasks) == 0:
            break
        for task in tasks:
            browser.find_element_by_id(task['id']).find_element_by_class_name('jstree-icon').click()
            time.sleep(0.25)
        soup = BeautifulSoup(browser.page_source, 'lxml')

    print('Collecting attendance information..')
    time.sleep(1)
    soup2 = BeautifulSoup(browser.page_source, 'lxml')
    members = soup2.find_all("li", attrs={"class":"jstree-leaf"})

    work_list = []
    holiday_list = []
    for member in members:
        browser.find_element_by_id(member['id']).find_element_by_tag_name('a').click()
        if 'org' in member['id']:
            continue
        account_soup = BeautifulSoup(browser.page_source, 'lxml')
        status = account_soup.find("a", attrs={"class": "btn_attend_info"}).get_text().strip('\n')
        mail = account_soup.find("span", attrs={"class": "mail"}).get_text()
        browser.find_element_by_xpath(('//*[@id="popupContent"]/div[2]/span[1]')).click()
        if status == 'Start':
            work_list.append(mail.split('@')[0])
        else:
            holiday_list.append(mail.split('@')[0])

    ignore_list = ['jeongwon', 'joonhyung', 'cheolhwang']
    work_host_list = []
    nonwork_host_list = []
    for a in work_list:
        if a in ignore_list:
            continue
        if a not in work_host_list:
            work_host_list.append(a)

    for a in holiday_list:
        if a in ignore_list:
            continue
        if a not in nonwork_host_list:
            nonwork_host_list.append(a)

    print('-----Web crawling complete-----')
    os.system('echo "{0}" >> {1}'.format('-----Web crawling complete-----', log_file))


    # check Nimby List
    nimby_ON_list = tractor_API.nimby_ON()
    nimby_OFF_list = tractor_API.nimby_OFF()

    nowtime = int(datetime.datetime.now().strftime('%H'))

    # Non-working employee #
    # If there is a non-working employee on the Nimby On list.
    if nowtime >= 5:
        for host, ipaddr in nimby_ON_list:
            if host in nonwork_host_list:
                process_kill(host)

        os.system('echo "{0}" >> {1}'.format('\n[Nimby On -> Off]', log_file))

        for host, ipaddr in nimby_ON_list:
            if host in nonwork_host_list:
                os.system('/core/Linux/APPZ/shell/nimby/tractor_nimby_swich 0 {h} {i}'.format(h=host, i=ipaddr))
                os.system('echo "  {0}" >> {1}'.format(host, log_file))

    # Working employee #
    # If there is a working employee on the Nimby Off list.
    os.system('echo "{0}" >> {1}'.format('\n[Nimby Off -> On]', log_file))
    for host, ipaddr in nimby_OFF_list:
        if host in work_host_list:
            os.system('/core/Linux/APPZ/shell/nimby/tractor_nimby_swich 1 {h} {i}'.format(h=host, i=ipaddr))
            os.system('echo "  {0}" >> {1}'.format(host, log_file))

    time.sleep(2) # Time interval for applying retry.

    for host, ipaddr in nimby_OFF_list:
        if host in work_host_list:
            tractor_API.retry_blade(host)

except Exception as e:
    err_msg = traceback.format_exc()
    os.system('echo "{0}" >> {1}'.format(err_msg, log_file))

finally:
    # Browser Quit
    browser.quit()
    print('>>> Browser Quit.')
    os.system('echo "{0}" >> {1}'.format('\n>>> Browser Quit.', log_file))

    # End Log Date
    end_prepix = datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')
    os.system('echo "[End Log] {0}" >> {1}'.format(end_prepix , log_file))
    os.system('echo "===================================" >> {0}'.format(log_file))
