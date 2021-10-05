---
title: Ubuntu配置Git并利用Gitee（码云）进行项目及代码的管理
date: 2021-05-01 10:54:27
tags: git linux
categories: Linux
---


# Ubuntu配置Git并利用Gitee（码云）进行项目及代码的管理

## git安装与卸载

```bash
apt-get install git
<!--more-->
apt-get remove git
```

## git配置

配置用户名

```bash
git config --global user.name “your name”
```

配置邮箱

```bash
git config --global user.email “your email”
```

查看配置信息

```bash
git config --global --list
```

生成公钥

```bash
ssh-keygen -t rsa -C "your email"
```

生成公钥后在ssh相应目录中将id\_rsa.pub中的内容拷贝至码云  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210501104524858.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)  
测试配置是否成功

```bash
ssh -T git@gitee.com
```

## git提交代码

将你本地所有修改了的文件添加到暂存区

```bash
git add .
```

将更改内容和日志消息一起存储在新的提交中

```bash
git commit -m "update"
```

下拉代码，将远程最新的代码先跟你本地的代码合并一下，如果确定远程没有更新，可以不用这个，最好是每次都执行以下，完成之后打开代码查看有没有冲突，并解决，如果有冲突解决完成以后再次执行1跟2的操作

```bash
git pull origin 远程分支名
```

将代码推至远程

```bash
git push origin master或者远程分支名
```