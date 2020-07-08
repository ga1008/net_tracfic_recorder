import math
import time


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


def main():
    print(convert_bytes(int(input('Bytes: '))))


if __name__ == '__main__':
    main()
