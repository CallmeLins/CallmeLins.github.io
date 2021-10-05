---
title: Linux安装Jupyter并且远程访问
date: 2021-06-20 13:16:12
tags: 
categories: Linux
---

<!--more-->

### pip的安装

下载pip安装脚本  
`wget https://bootstrap.pypa.io/get-pip.py`  
使用python命令运行安装脚本  
`python3 get-pip.py`

### Jupyter的安装

```bash
pip install ipython  
pip install jupyter
```

Ubuntu此时使用jupyter notebook命令启动jupyter会提示未找到命令，按照提示安装jupyter即可  
`sudo snap install jupyter`  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210620102132972.png)

### 配置Jupyter notebook server

#### 生成配置文件

安装jupyter后续通过以下命令生成配置文件  
`jupyter notebook \--generate-config`

#### 生成访问密码

只需要需要运行一行命令 jupyter notebook password ，会让你填写密码和确认密码，并且生成含有密码的hash的jupyter\_notebook\_config.json在配置文件中

```bash
jupyter notebook password
Enter password: 
Verify password: 
[NotebookPasswordApp] Wrote hashed password to /home/coke/snap/jupyter/6/.jupyter/jupyter_notebook_config.json
```

#### 生成hash密码

下面我们还需要手动生成一个hash密码。

可能你会问，为什么前面我们生成了一个Jupyter密码，这里还需生成一个hash密码呢？

原因很简单，如果你没有生成这么一个hash密码的话，那么每次通过浏览器远程访问Jupyter时，你都需要输入一次密码，这很繁琐！

但如果我们启用了这个hash密码，只需要首次远程访问Jupyter文档时，输入一次密码，在下次访问时，这个hash密码就好比一个钥匙（token），替我们打开密码之门，也就是免密码登录。

然后在IPython中，依次输入如下代码：

```bash
In [1]: from notebook.auth import passwd
In [2]: passwd()
Enter password:
Verify password:
Out[2]: 'sha1:67c9e60bb8b6:9ffede0825894254b2e042ea597d771089e11aed'
```

#### 修改默认配置文件

使用vim对配置文件进行修改，配置文件目录以本机为准  
`vim /home/coke/snap/jupyter/6/.jupyter/jupyter_notebook_config.py`  
主要对以下几条进行修改

```bash
c.NotebookApp.ip='0.0.0.0'
c.NotebookApp.password = u'sha:ce...刚才复制的那个密文'
c.NotebookApp.open_browser = False #避免服务器端浏览器自动打开
c.NotebookApp.port =8888 #随便指定一个端口
```

如果此时依然无法访问，最简单的方法在本地主机建立SSH通道

```bash
PS C:\Users\z> ssh coke@192.168.20.135
coke@192.168.20.135's password:
Welcome to Ubuntu 20.04.2 LTS (GNU/Linux 5.8.0-55-generic x86_64)
```

此时启动jupyter notebook 就可以在本地主机进入notebook了

```bash
jupyter notebook #服务启动

http://192.168.0.1:8888/tree #访问ip地址更换为服务器地址
```