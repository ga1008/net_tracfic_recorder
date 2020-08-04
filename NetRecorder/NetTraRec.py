# coding: utf-8
import json
import os
import sys
import time
from argparse import ArgumentParser, RawTextHelpFormatter

import redis
from redis import AuthenticationError
import psutil
from BaseColor.base_colors import hgreen, hblue, red, hred

from NetRecorder.gear_for_nr import tell_the_datetime, convert_bytes, find_local_redis_pass, start_up_check, \
    _get_host_name, _get_current_ip


def get_refresh_time(refresh_rate):
    if refresh_rate == "h":
        rft = 3600
    elif refresh_rate == "m":
        rft = 60
    else:
        rft = 1
    return rft


def waiting(rw, head_str=None):
    while rw >= 0:
        m, s = divmod(rw, 60)
        h, m = divmod(m, 60)
        print(f'{head_str}: [ {red(f"{h}:{m}:{s}")} ]\r', end='') if head_str else print(f'[ {red(f"{h}:{m}:{s}")} ]\r', end='')
        rw -= 1
        time.sleep(1)
    # print()


def cal_space(s="Gathering data, please wait: [ 0:0:0 ]]"):
    sl = len(s)
    try:
        length = os.get_terminal_size().columns - sl
    except:
        length = 120 - sl
    return length


def get_key():
    io_counters = psutil.net_io_counters(pernic=True)
    key_info = io_counters.keys()  # 获取网卡名称
    recv = {}
    sent = {}
    for key in key_info:
        recv.setdefault(key, io_counters.get(key).bytes_recv)  # 各网卡接收的字节数
        sent.setdefault(key, io_counters.get(key).bytes_sent)  # 各网卡发送的字节数
    return key_info, recv, sent


def get_rate(func, unit="auto", refresh_rate="s"):
    rf_time = get_refresh_time(refresh_rate)
    k_info, old_recv, old_sent = func()  # 收集的数据
    if rf_time > 1:
        # f_space = cal_space()
        waiting(rf_time, f"Gathering data, please wait")
    else:
        time.sleep(rf_time)
    k_info, now_recv, now_sent = func()  # 当前所收集的数据
    u_dic = {'bytes': 0, 'kb': 1, 'mb': 2, 'gb': 3, 'tb': 4, 'pb': 5}
    u_set = u_dic.get(unit, 1)
    n_in = {}
    n_out = {}
    for k in k_info:
        diff_recv = now_recv.get(k) - old_recv.get(k) or 1
        diff_sent = now_sent.get(k) - old_sent.get(k) or 1
        if unit == 'auto':
            n_in.setdefault(k, convert_bytes(diff_recv, refresh_rate=refresh_rate))
            n_out.setdefault(k, convert_bytes(diff_sent, refresh_rate=refresh_rate))
        else:
            n_in.setdefault(k, f"{round(diff_recv / pow(1024, u_set), 1)} {unit}/{refresh_rate}")  # 每秒接收速率
            n_out.setdefault(k, f"{round(diff_sent / pow(1024, u_set), 1)} {unit}/{refresh_rate}")  # 每秒发送速率
    return k_info, n_in, n_out


def get_redis_cli(redis_params):
    return redis.Redis(
        host=redis_params.get("host", "127.0.0.1"),
        port=redis_params.get("port", 6379),
        db=redis_params.get("db", 0),
        password=redis_params.get("password", "123456"),
    )


def default_redis_params(updates=None):
    def_para = {
        "host": "127.0.0.1",
        "port": 6379,
        "db": 0,
        "password": "123456",
    }
    def_para.update(updates if updates and isinstance(updates, dict) else {})
    return def_para


def start(ip_keys, print_out=True, unit="auto", refresh_rate="s", push_redis=False, target_redis_params=None):
    unit = unit.lower()
    if print_out:
        target_redis_params = target_redis_params if target_redis_params else [default_redis_params()]
        if not isinstance(target_redis_params, list):
            target_redis_params = [target_redis_params]
        for trp in target_redis_params:
            insert_key = trp.get('insert_key', "NetRecs")
            if push_redis:
                print(f"will push results into target redis: [ {trp.get('host')}:{trp.get('db')}:{insert_key} ]")
        while 1:
            try:
                key_i, ne_in, ne_out = get_rate(get_key, unit, refresh_rate)
                s_key_set = {x for x in ip_keys if x in key_i}
                if not s_key_set:
                    print(red("device name may wrong, please check and run again"))
                    print(red(f"all net devices: {list(key_i)}"))
                    exit(1)
                if push_redis:
                    hostname = _get_host_name()
                    ip_info = _get_current_ip()
                    insert_obj = json.dumps({i_key: {"in": ne_in.get(i_key),
                                                     "out": ne_out.get(i_key),
                                                     "time": tell_the_datetime(),
                                                     "hostname": hostname,
                                                     "ip": ip_info.get('ip'),
                                                     "location": f"{ip_info.get('city')} - {ip_info.get('country')}",
                                                     } for i_key in s_key_set})
                    for trp in target_redis_params:
                        get_redis_cli(trp).rpush(trp.get('insert_key', "NetRecs"), insert_obj)
                s_out = "; ".join(
                    [f"{hred(ky)}: [ in: {hgreen(ne_in.get(ky))}, out: {hblue(ne_out.get(ky))} ]" for ky in s_key_set])
                s_out = f"{'-'*42}{tell_the_datetime()} {s_out}"
                try:
                    length = os.get_terminal_size().columns - (len(s_out)-13*2)
                except:
                    length = 100 - (len(s_out)-13*2)
                if length < 0:
                    length = 0
                print(f"{s_out}{' '*length}\r", end='')
            except KeyboardInterrupt:
                print()
                exit()
            except Exception as E:
                print(f"not functioning\n{E}")
                continue
    else:
        key_i, ne_in, ne_out = get_rate(get_key, unit, refresh_rate)
        s_key_set = {x for x in ip_keys if x in key_i}
        if not s_key_set:
            print(red("device name may wrong, please check and run again"))
            print(red(f"all net devices: {list(key_i)}"))
            return {}
        return {ky: [ne_in.get(ky), ne_out.get(ky), unit, tell_the_datetime()] for ky in s_key_set}


def record_starter():
    dp = '    这是一个查看或者返回服务器流量信息的工具。\n' \
         '    https://github.com/ga1008/net_tracfic_recorder'
    da = ""
    parser = ArgumentParser(description=dp, formatter_class=RawTextHelpFormatter, add_help=True)
    parser.add_argument("-n", "--net_devices", type=str, dest="net_devices", default='eth0,enp2s0',
                        help=f'{da}指定网络设备，默认 eth0。多个值使用英文逗号 "," 隔开\n')
    parser.add_argument("-u", "--unit", type=str, dest="unit", default='auto',
                        help=f'{da}指定流量单位，auto/bytes/kb/mb/gb，默认auto\n')
    parser.add_argument("-rf", "--refresh_rate", type=str, dest="refresh_rate", default='s',
                        help=f'{da}统计频率，h/m/s (时/分/秒)，默认s\n')
    parser.add_argument("-pr", "--push_redis", type=str, dest="push_redis", default='n', nargs='?',
                        help=f'{da}y/n。将结果推入指定的redis，默认n。如果设置了此参数，则接下来需要提供目标redis的信息\n')
    parser.add_argument("-kp", "--key_params", type=str, dest="key_params", default='input',
                        help=f'{da}关键参数提供方式，input/local/now，\n'
                             f'input是随后输入，\n'
                             f'local是在本地redis的"NetRec_key_params"内寻找，\n'
                             'now是后面直接跟上>>>>参数字典，例如：now>>>>{"host": "127.0.0.1", "port": ..., "db": ...}，'
                             'now方式仅限测试\n'
                             f'默认input\n')
    args = parser.parse_args()
    n_devices = [x.strip() for x in args.net_devices.split(",")]
    unit = args.unit
    refresh_rate = args.refresh_rate.lower()
    push_to_redis = args.push_redis
    key_params_mode = args.key_params
    push_to_redis = True if push_to_redis == 'y' or push_to_redis is None else False
    key_params = {}
    if push_to_redis:
        start_up_check()
        if key_params_mode.startswith("now"):
            key_params = key_params_mode.split(">>>>")[-1]
            try:
                key_params = json.loads(key_params)
            except Exception as E:
                print(f"can not load key params: \n{key_params}\n{E}")
                key_params = {}
        elif key_params_mode.startswith("input"):
            key_params = {
                "host": input("target redis host(127.0.0.1): ") or "127.0.0.1",
                "port": int(input("port(6379): ") or 6379),
                "db": int(input("db(0): ") or 0),
                "password": input("password(123456): ") or "123456",
                "insert_key": input("insert_key(NetRecs): ") or "NetRecs",
            }
        elif key_params_mode.startswith("local"):
            try:
                local_redis_pass = find_local_redis_pass()
                key_params_raw = get_redis_cli(default_redis_params(
                    updates={"password": local_redis_pass}
                )).lrange("NetRec_key_params", -1, -1)
                if not key_params_raw:
                    print("no setting found in local redis, please check and restart")
                    exit(1)
                key_params = json.loads(key_params_raw[0].decode())
            except AuthenticationError:
                print("password not correct! ")
                exit(1)
            except IndexError:
                print("no values in local redis key: NetRec_key_params")
                exit(1)
    # sys.stdout = Logger(os.path.join(os.getcwd(), f"netrecord_{tell_the_datetime(compact_mode=True)}.log"))
    start(n_devices, print_out=True, unit=unit, refresh_rate=refresh_rate, push_redis=push_to_redis, target_redis_params=key_params)


def record_starter_server():
    dp = '    这是一个查看或者返回服务器流量信息的工具，以服务的方式启动，默认使用推 redis 的方式，单位为 bytes/m\n' \
         '    https://github.com/ga1008/net_tracfic_recorder'
    da = ""
    parser = ArgumentParser(description=dp, formatter_class=RawTextHelpFormatter, add_help=True)
    parser.add_argument("-n", "--net_devices", type=str, dest="net_devices", default='eth0,enp2s0',
                        help=f'{da}指定网络设备，默认 eth0。多个值使用英文逗号 "," 隔开\n')
    parser.add_argument("-u", "--unit", type=str, dest="unit", default='bytes',
                        help=f'{da}指定流量单位，auto/bytes/kb/mb/gb，默认bytes\n')
    parser.add_argument("-rf", "--refresh_rate", type=str, dest="refresh_rate", default='m',
                        help=f'{da}统计频率，h/m/s (时/分/秒)，默认s\n')
    parser.add_argument("-pr", "--push_redis", type=str, dest="push_redis", default='y', nargs='?',
                        help=f'{da}y/n。将结果推入指定的redis，默认n。如果设置了此参数，则接下来需要提供目标redis的信息\n')
    parser.add_argument("-kp", "--key_params", type=str, dest="key_params", default='local',
                        help=f'{da}关键参数提供方式，input/local/now，\n'
                             f'input是随后输入，\n'
                             f'local是在本地redis的"NetRec_key_params"内寻找，\n'
                             'now是后面直接跟上>>>>参数字典，例如：now>>>>{"host": "127.0.0.1", "port": ..., "db": ...}，'
                             'now方式仅限测试\n'
                             f'默认input\n')
    args = parser.parse_args()
    n_devices = [x.strip() for x in args.net_devices.split(",")]
    unit = args.unit
    refresh_rate = args.refresh_rate.lower()
    push_to_redis = args.push_redis
    key_params_mode = args.key_params
    push_to_redis = True if push_to_redis == 'y' or push_to_redis is None else False
    key_params = {}
    if push_to_redis:
        start_up_check()
        if key_params_mode.startswith("now"):
            key_params = key_params_mode.split(">>>>")[-1]
            try:
                key_params = json.loads(key_params)
            except Exception as E:
                print(f"can not load key params: \n{key_params}\n{E}")
                key_params = {}
        elif key_params_mode.startswith("input"):
            key_params = {
                "host": input("target redis host(127.0.0.1): ") or "127.0.0.1",
                "port": int(input("port(6379): ") or 6379),
                "db": int(input("db(0): ") or 0),
                "password": input("password(123456): ") or "123456",
                "insert_key": input("insert_key(NetRecs): ") or "NetRecs",
            }
        elif key_params_mode.startswith("local"):
            try:
                local_redis_pass = find_local_redis_pass()
                key_params_raw = get_redis_cli(default_redis_params(
                    updates={"password": local_redis_pass}
                )).lrange("NetRec_key_params", -1, -1)
                if not key_params_raw:
                    print("no setting found in local redis, please check and restart")
                    exit(1)
                key_params = json.loads(key_params_raw[0].decode())
            except AuthenticationError:
                print("password not correct! ")
                exit(1)
            except IndexError:
                print("no values in local redis key: NetRec_key_params")
                exit(1)
    # sys.stdout = Logger(os.path.join(os.getcwd(), f"netrecord_{tell_the_datetime(compact_mode=True)}.log"))
    start(n_devices, print_out=True, unit=unit, refresh_rate=refresh_rate, push_redis=push_to_redis, target_redis_params=key_params)


if __name__ == '__main__':
    s_keys = sys.argv[1:] or ["eth0", "enp2s0"]
    res = start(s_keys, print_out=False, unit="auto")
    print(res)
