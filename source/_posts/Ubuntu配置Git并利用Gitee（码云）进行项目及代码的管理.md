---
title: Ubuntu配置Git并利用Gitee（码云）进行项目及代码的管理
date: 2021-05-01 10:54:27
categories: Linux
---
# Ubuntu配置Git并利用Gitee（码云）进行项目及代码的管理
## git安装与卸载

`
apt-get install git
apt-get remove git
`
## git配置
配置用户名
`
git config --global user.name “your name”
`
配置邮箱
`
git config --global user.email “your email”
`
查看配置信息
`
git config --global --list
`
生成公钥
`
ssh-keygen -t rsa -C "your email"
`
生成公钥后在ssh相应目录中将id_rsa.pub中的内容拷贝至码云
![在这里插入图片描述](Ubuntu配置Git并利用Gitee（码云）进行项目及代码的管理.assets/20210501104524858.png)
测试配置是否成功
`
ssh -T git@gitee.com
`
## 代码推送的流程
1、初始化一个仓库：`git init`

2、增加代码后，添加：`git add .`

3、提交代码到仓库：`git commit -m "related_message"`

4、添加远程仓库地址，这里就是添加在gitee上建立的仓库地址

`git remote add origin https://gitee.com/****/****.git`

5、把本地仓库推到远程存储仓库中
`git push origin master`

## git提交代码（从仓库克隆修改后）
将你本地所有修改了的文件添加到暂存区
`
git add .
`
将更改内容和日志消息一起存储在新的提交中
`
git commit -m "update"
`
下拉代码，将远程最新的代码先跟你本地的代码合并一下，如果确定远程没有更新，可以不用这个，最好是每次都执行以下，完成之后打开代码查看有没有冲突，并解决，如果有冲突解决完成以后再次执行1跟2的操作
`
git pull origin 远程分支名
`
将代码推至远程
`
git push origin master或者远程分支名
`

 