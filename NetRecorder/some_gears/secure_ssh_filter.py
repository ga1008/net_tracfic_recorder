import json
import random
import re
import time

import requests
from tqdm import tqdm


def location_format_requests(ip):
    t = requests.get(url=f"http://www.cip.cc/{ip}", headers={'accept': 'text/html,*/*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8', 'content-type': 'application/x-www-form-urlencoded;charset=UTF-8', 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36', 'x-requested-with': 'XMLHttpRequest'})
    if t.status_code == 200:
        t = re.findall("地址	: (.*?)\n", t.text)
        t = t[0].strip() if t else ''
        return t


def location_format_requests_2(ip):
    t = requests.get(f"https://www.ip.cn/?ip={ip}", headers={'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36', 'x-requested-with': 'XMLHttpRequest'})
    if t.status_code == 200:
        t = re.findall(r"所在地理位置：<code>([^<]+)<", t.text)
        t = t[0].strip() if t else ''
        return t


def format_secure_data(raw):
    sl = {x.strip() for x in raw.split("\n")}
    failed_password_connection = {}
    accepted_publickey_connection = {}
    accepted_password_connection = {}
    location_pool = {}
    td = tqdm(total=len(sl))
    for line in sl:
        res = re.findall(r"(.*?\d{2}:\d{2}:\d{2}).*(\d+\.\d+\.\d+\.\d+)", line)
        if res:
            h_time, ip = res[0]
            if ip not in location_pool:
                location = location_format_requests_2(ip)
                if location:
                    location_pool[ip] = location
            else:
                location = location_pool.get(ip)
            if "Failed password" in line:
                failed_password_connection[h_time] = failed_password_connection.get(h_time, []) + [{"ip": ip, "location": location}]
            if "Accepted publickey" in line:
                accepted_publickey_connection[h_time] = accepted_publickey_connection.get(h_time, []) + [{"ip": ip, "location": location}]
            if "Accepted password" in line:
                accepted_password_connection[h_time] = accepted_password_connection.get(h_time, []) + [{"ip": ip, "location": location}]
            time.sleep(random.randint(1, 2))
        td.update()
    total_dic = {
        "Failed_password": failed_password_connection,
        "Accepted_publickey": accepted_publickey_connection,
        "Accepted_password": accepted_password_connection,
    }
    return total_dic


def open_secure_data(path):
    with open(path, 'r') as rf:
        raw_data = rf.read()
    return raw_data


if __name__ == '__main__':
    results = format_secure_data(open_secure_data(
        input("path of the secure file: ")
    ))
    with open("ssh_secure_results.json", 'w') as wf:
        wf.write(json.dumps(results))
    print("done! ")