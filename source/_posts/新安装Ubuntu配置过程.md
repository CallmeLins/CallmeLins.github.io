---
title: 新安装Ubuntu配置过程
date: 2021-04-26 21:19:18
tags: linux
categories: Linux
---

<!--more-->

## 2021.5.3 Update

## Linux-Setting

#### 介绍

Linux安装后自动配置脚本

#### 说明

1.  更换自带源为阿里源
2.  卸载自带无用软件如libreoffice、thunderbird等
3.  安装常用软件如git、curl、vim等
4.  git设置
5.  zsh\&oh-my-zsh

#### 使用说明

首先安装git，curl，zsh

```
sudo apt install git curl
```

然后安装zsh

```
sudo apt install -y zsh

sh -c "$(curl -fsSL https://gitee.com/pocmon/ohmyzsh/raw/master/tools/install.sh)"
```

 1.     克隆本仓库至本地

```
git clone https://gitee.com/xiaolinzinvshen/linux-setting.git
```

 2.     cd到相应文件夹中
 3.     对相应的脚本增加执行权限后执行脚本

```
chmod +x ./init-ubuntu.sh

./init-ubuntu.sh
```

---
---
---

## Old

## 更换清华镜像源

Ubuntu 的软件源配置文件是 /etc/apt/sources.list。将系统自带的该文件做个备份

```powershell
sudo cp /etc/apt/sources.list /etc/apt/sources_backup.list
```

使用gedit将源中内容替换

```bash
sudo gedit /etc/apt/sources.list
```

链接: [清华镜像源](https://mirror.tuna.tsinghua.edu.cn/help/ubuntu/).  
升级自带包

```powershell
sudo apt update
```

安装常用基本软件

```powershell
sudo apt install curl git openssh-server net-tools
```

## 自动脚本配置

搜索marswang42 找到My-Vim-Conf  
安装第三方shell-zsh，并替换自带的bash

```powershell
sudo apt install -y zsh
```

```powershell
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

clone博主的源

```powershell
git clone https://github.com/MarsWang42/My-Vim-Conf.git
```

```powershell
cd My-Vim-Conf
```

脚本自动安装

```powershell
chmod +x ./setup.sh ./tmux.sh
```

```powershell
./setup.sh
```

最后刷新应用最新的设置

```powershell
source ~/.zshrc
```

## Ubuntu助手：一键安装软件、进行系统配置

```xml
https://github.com/borninfreedom/linux-assistant
```