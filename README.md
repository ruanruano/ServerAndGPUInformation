# 1. 简介
在网页上同时查看多个服务器的信息（网络、内存、硬盘、显卡）

大致原理是后端的python程序通过ssh连接服务器，定期通过终端解析获取所需数据存在字典中，然后前端网页定期获取字典的内容进行可视化。

![](pics/test.png)
# 2. 安装
## 2.1. 运行环境
即运行后端程序所需的环境，可在conda中安装虚拟环境，linux和windows都可以。
```bash
pip install flask flask-cors paramiko -i https://pypi.tuna.tsinghua.edu.cn/simple
```
## 2.2. 服务器环境
即需要被查看的服务器上所安装的环境。

因为本质上是通过ssh连接服务器，然后通过命令来获取相应的信息，有的命令可能服务器系统上不自带需要另外安装，否则无法获取到对应的数据。
- **ifstat**，用于获取网络数据的工具，可通过apt安装（如果不需要显示网络数据则不用安装）。并且需要在服务器上运行一下命令，查看哪个网卡才是主要的，写到配置文件里去（如果不需要查看网络信息可以不写）。
- **gpustat**，用于获取显卡上用户的使用情况，也可通过apt安装。
- **nvidia驱动**，需要需要安装N卡的驱动，能够通过`nvidia-smi`来获取显卡信息即可（AMD的应该就没办法了）。

其中这个ifstat查看网卡的步骤如下：通过apt安装完成之后，在终端输入`ifstat`，可以看到类似下面的输出（ctrl+c停止），因为一般会不只一个网卡，而且名称也会不一样。此时可以看一下哪个名称的网卡有数据变化，比如下方的就是`eno2`，可以写到配置文件里。
```
       eno1                eno2          br-6c8650526aef         docker0           veth1d3300f
 KB/s in  KB/s out   KB/s in  KB/s out   KB/s in  KB/s out   KB/s in  KB/s out   KB/s in  KB/s out
    0.00      0.00      3.31      1.96      0.00      0.00      0.00      0.00      0.00      0.00
    0.00      0.00      2.23      1.52      0.00      0.00      0.00      0.00      0.00      0.00
    0.00      0.00      7.56      8.03      0.00      0.00      0.00      0.00      0.00      0.00
    0.00      0.00      4.00      4.55      0.00      0.00      0.00      0.00      0.00      0.00
    0.00      0.00      3.66      0.19      0.00      0.00      0.00      0.00      0.00      0.00
    0.00      0.00      8.34      8.26      0.00      0.00      0.00      0.00      0.00      0.00
    0.00      0.00      8.25      4.78      0.00      0.00      0.00      0.00      0.00      0.00
```
## 2.3. 后端部署
安装好运行环境且设置好配置文件后，直接开一个screen，然后在目录下运行`python app.py`即可。（需要确保当前机器能够访问到所需要监视的服务器）

需要注意的是，app.py内最后几行可以找到`app.run(debug=True, host='127.0.0.1', port=port)`这行代码，可以将debug改为`False`，host可以改为`0.0.0.0`（在云服务器上部署时貌似需要改为这个），port可以按需修改。并且需要在防火墙上打开对应端口。可修改`check_interval`变量，默认为2，代表检测一次服务器信息的间隔。


其中配置文件默认名称为`serverList.json`，需要自己创建，格式参考`serverList_example.json`，具体规则如下：
- title：服务器名称，用于显示。
- ip：服务器ip地址，用于连接。
- port：访问的端口，一般是22，如果访问容器等则按需修改。
- username：用于登录的账户名称。
- password：用于登录的账户密码。
- key_filename：用于登录的账户密钥**路径**。（password和key_filename只需要设置一个即可，如果服务器只能使用密钥登陆则填密钥即可）
- network_interface_name：网卡名称。（非必须项，如果不需要可视化网速则不需要设置）
- storage_list：需要查看存储空间使用情况的路径list。（非必须项，无论有没有设置都会默认检查根目录的使用情况）
```json
{
    "title": "SERVER_76",
    "ip": "123.123.123.76",
    "port": 22,
    "username": "lxb",
    "password": "abcdefg",
    "key_filename": "/home/.ssh/id_rsa",
    "network_interface_name": "eno2",
    "storage_list": [
        "/media/D",
        "/media/F"
    ]
}
```

开启运行之后，如果`serverList.json`有修改，需要重新启动app.py才能生效。

## 2.4. 网页部署
可以使用docker运行一个nginx的容器来简单的部署这个网页。
首先安装docker，安装完之后可执行命令`docker run -d -p 80:80 -v /home/lxb/nginx_gpus:/usr/share/nginx/html --name nginx_gpus nginx:latest`，注意**按需修改命令**，具体可修改内容如下。
```bash
docker run -d \
  -p <宿主机上映射的端口>:80 \
  -v <宿主机上数据卷的位置>:/usr/share/nginx/html \
  --name <容器名称> \
  nginx:latest
```

**另外需要**将index.html中的fetchData函数内的地址替换为对应后端的ip+端口。（`fetch('<替换这里>/all_data')`）

然后把`index.html`放入数据卷中，替换掉原来的。然后访问主机`ip:映射的端口号`，如`123.123.123.123:80`（默认8080的话可以不输入）即可打开网页。

另外可以修改setInterval的时间，即多久访问一次后端，建议时间不要小于后端的check_interval，不然经常获取的也是没有更新的数据浪费了。
```javascript
// 页面加载时获取数据并定时刷新
document.addEventListener('DOMContentLoaded', function() {
    fetchData();
    setInterval(fetchData, 3000); // 每3秒刷新一次数据
});
```

有域名的话也可以搞一个反向代理，可参考 [服务器上使用Nginx部署网页+反向代理](http://blog.lxblxb.top/archives/1723257245091)。

# 3. 其他
- `永辉`帮忙搞了一下顶部checkbox布局的问题。
- 参考`治鹏`的方法加了每张显卡的用户使用的情况。
