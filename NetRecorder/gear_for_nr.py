import math
import os
import re
import socket
import time
from pathlib import Path

import requests
from BaseColor.base_colors import blue, hcyan


def tell_the_datetime(time_stamp=None, compact_mode=False):
    time_stamp = time_stamp if time_stamp else time.time()
    if not compact_mode:
        format_str = '%Y-%m-%d %H:%M:%S'
    else:
        format_str = '%Y-%m-%d-%H-%M-%S'
    tm = time.strftime(format_str, time.localtime(time_stamp))
    return tm


def convert_bytes(bts, lst=None, refresh_rate="s"):
    if lst is None:
        lst = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = int(math.floor(  # 舍弃小数点，取小
        math.log(int(bts) or 1, 1024)  # 求对数(对数：若 a**b = N 则 b 叫做以 a 为底 N 的对数)
    ))

    if i >= len(lst):
        i = len(lst) - 1
    return ('%.2f' + f" {lst[i]}/{refresh_rate}") % (bts / math.pow(1024, i))


def find_local_redis_pass():
    rc_path_tmp = os.popen("whereis 'redis.conf'").read().split(' ')[-1].strip()
    rd_pass = None
    if rc_path_tmp:
        rcf_path = Path(rc_path_tmp)
        if rcf_path.is_dir():
            rcf_path = rcf_path / "redis.conf"
        if rcf_path.exists():
            rcf = get_file_lines(str(rcf_path.absolute()))
            rd_pass = [re.findall("^requirepass(.*)", x)[0].strip() for x in rcf if re.findall("^requirepass(.*)", x)][0]
    return rd_pass


def get_file_lines(f_path):
    try:
        with open(f_path, 'r') as rf:
            f_lines = rf.readlines()
    except PermissionError:
        f_lines = os.popen(f"sudo cat {f_path}").read().split('\n')
    f_lines = [x.strip() for x in f_lines]
    return f_lines


def gen_server_script(local_path):
    raw_script = os.path.join(local_path, "nettrarec.raw")
    with open(raw_script, 'r') as rf:
        rsf = rf.read()
    server_path = os.popen("whereis netrec-server | awk '{print $2}'").read()
    n_rsf = re.sub("abcdefg", server_path, rsf)
    script_path = os.path.join(local_path, "nettrarec")
    with open(script_path, 'w') as wf:
        wf.write(n_rsf)


def start_up_check():
    if os.path.exists("/etc/init.d/nettrarec"):
        return
    local_path = os.path.split(os.path.abspath(__file__))[0]
    gen_server_script(local_path)
    os.popen(f'sudo cp {os.path.join(local_path, "nettrarec")} /etc/init.d/ && sudo chmod +x /etc/init.d/nettrarec').read()
    print("It looks like the first run")
    do = input("you want to add the netrec to system service(it will not show again)? [y/n]: ").lower() or 'n'
    if do == 'y':
        print("please run the following steps: ")
        print(blue("1. push target redis info to local redis(replace the XXX to your info): "))
        print("   $", hcyan("redis-cli"))
        print("   127.0.0.1:6379>", hcyan('AUTH xxxxx'))
        print("   127.0.0.1:6379>", hcyan("""rpush NetRec_key_params '{"host": "xxx.xxx.xxx.xxx", "port": 6379, "db": 0, "password": "xxxxxx", "insert_key": "xxxxx"}'"""))

        print(blue("2. add system service and set to start automatically at system boot: "))
        print("   $", hcyan("chkconfig --add nettrarec"))
        print("   $", hcyan("chkconfig nettrarec on"))
        print("   $", hcyan("systemctl start nettrarec"))

        print(blue("3. Open target Redis to check if the data is correct\n"))


def _get_host_name():
    try:
        host_name = socket.gethostname()
    except Exception as E:
        print(f"Error in getting host name: \n{E}")
        host_name = ''
    return host_name


def _get_current_ip():
    ip_info = {}
    try:
        ip_info = requests.get("http://ipinfo.io", timeout=(10, 20)).json()
    except Exception as E:
        print(f"Error in getting ip info: \n{E}")
    return ip_info


if __name__ == '__main__':
    print(find_local_redis_pass())
