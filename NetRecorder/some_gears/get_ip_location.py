import os
import random
import re
import time

import requests


def location_format_requests(ip):
    t = requests.get(url=f"http://www.cip.cc/{ip}", headers={'accept': 'text/html,*/*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8', 'content-type': 'application/x-www-form-urlencoded;charset=UTF-8', 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36', 'x-requested-with': 'XMLHttpRequest'})
    if t.status_code == 200:
        t = re.findall("地址	: (.*?)\n", t.text)
        t = t[0].strip() if t else ''
        return t


def location_format(ip):
    t = os.popen(f"curl 'cip.cc/{ip}'").read()
    t = re.findall("地址\\t: (.*?)\n", t)
    if t:
        t = t[0].strip()
        return t
    return ''


def get_location(ips):
    sd = {}
    for x in ips:
        sd[x] = location_format_requests(x)
        time.sleep(random.randint(5, 10))
    return sd


if __name__ == '__main__':
    ld = get_location(
        ips={'119.23.174.205', '185.132.53.52', '196.221.19.39', '47.97.10.19', '85.209.0.102', '73.134.225.147', '124.70.198.218', '156.38.115.82', '192.35.168.197', '79.124.8.77', '222.186.30.59', '85.209.0.252', '218.92.0.212', '112.85.42.172', '192.35.168.209', '198.251.83.193', '109.208.118.196', '192.35.168.215', '24.240.238.158', '86.96.52.189', '65.49.20.66', '113.99.17.200', '45.136.108.65', '114.150.214.8', '49.88.112.75', '139.5.252.49', '112.85.42.104', '144.172.73.37', '85.209.0.100', '179.165.229.146', '117.169.95.98', '139.162.122.110', '85.209.0.251', '85.209.0.253', '141.98.81.42', '112.85.42.200', '47.100.64.9', '171.227.209.232', '91.248.239.100', '112.85.42.174', '192.35.169.48', '85.209.0.103', '85.209.0.83', '85.209.0.101', '116.21.95.49', '92.118.161.45', '115.72.128.235', '172.101.127.161', '209.249.85.177', '185.220.102.253', '54.39.16.73', '141.98.9.157', '185.159.163.247', '47.97.21.76', '162.247.74.216', '106.15.76.85', '47.96.254.10', '47.95.28.143', '60.184.136.212', '182.23.126.50', '62.96.54.212', '139.162.75.112', '198.98.54.28', '141.98.10.196', '47.100.64.86', '113.99.17.201'}
    )
    print(ld)