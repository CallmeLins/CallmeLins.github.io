---
title: Linux下配置Selenium
date: 2021-07-04 10:23:01
tags: 
categories: # Python
---

<!--more-->

### Linux下使用Selenium进行自动化测试

- - [selenium的安装](#selenium_1)
  - [安装chrome以及chrome driver](#chromechrome_driver_5)
  - [Chrome driver 配置](#Chrome_driver__16)

## selenium的安装

```python
pip install selenium
```

## 安装chrome以及chrome driver

简单点直接从官网下载deb安装包，此时双击直接用默认应用商店安装可能会出现如下错误  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210704092644914.png)  
**解决方案**

```python
sudo apt-get install gdebi
```

接着在右击你要安装的 .deb 文件，选择 Open With —> GDebi Package Installer接着install package即可  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210704092759414.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)

## Chrome driver 配置

[Chrome 浏览器驱动下载地址](https://chromedriver.storage.googleapis.com/index.html)  
根据浏览器版本下载相应的driver版本，给文件赋予可执行权限

```python
chmod +x chromedriver
```

然后将文件放到系统环境变量PATH路径中

```python
sudo cp chromedriver /usr/bin/
```

查看chromedriver的版本号确认成功

```python
chromedriver --version
```

然后新建.py文件进行测试，此时已能自动打开chrome并访问百度

```python
from selenium import webdriver

wd = webdriver.Chrome()

wd.get('https://www.baidu.com')
```