---
title: 虚拟机安装Ubuntu配置记录
date: 2021-04-26 18:45:11
categories: Linux
---
# 虚拟机安装Ubuntu配置记录
关闭动画
```powershell
gsettings set org.gnome.desktop.interface enable-animations false
```
打开动画

```powershell
gsettings set org.gnome.desktop.interface enable-animations true
```

# 精简软件
卸载libreoffice

```powershell
sudo apt-get remove libreoffice-common
```
卸载无用软件
```powershell
sudo apt-get remove thunderbird totem rhythmbox empathy brasero simple-scan gnome-mahjongg aisleriot gnome-mines cheese transmission-common gnome-orca gnome-sudoku
```
# WIN10+Ubuntu双系统完全删除Ubuntu并删除BOOT引导中的启动项
1、首先进入BIOS将Windows boot manager设为第一启动项
2、进入Windows后使用DiskGenius 删除系统EFI分区中的Ubuntu启动项

![](虚拟机安装Ubuntu配置记录.assets/1564853-20210503154131681-935014681.png)

3、最后使用EasyUEFI删除启动项中的Ubuntu即可，大功告成

![在这里插入图片描述](虚拟机安装Ubuntu配置记录.assets/2021042618584411.png)

![在这里插入图片描述](虚拟机安装Ubuntu配置记录.assets/20210426185853166.png)

