服务器流量监控小工具
====

### 安装：  

```shell script
$ pip install NetTraRec
```

### 终端使用：  

```shell script
$ netrec [-选项]

# 显示帮助
$ netrec -h

# 结果推入 redis
$ netrec -pr
# 然后在启动后输入相关信息：
# target redis host(127.0.0.1): 
# port(6379): 
# db(0): 
# password(123456):
# ...

# 目标 redis 可以是本地或远程
# redis 信息也可以使用参数 "-kp now>>>>参数字典" 传入，方便远程调度
# 例如：
$ netrec -pr -kp 'now>>>>{"host": ..., "port": ..., ...}'
```

### 代码调用：  
```python
from NetRecorder import NetTraRec as Nr
res = Nr.start(["eth0"], print_out=False, unit="auto")
print(res)

# {'eth0': ['126.00 Bytes/s', '132.00 Bytes/s', 'auto', '2020-07-08 09:51:17']}
```

### 参数介绍：  
懒得写了，看帮助吧
