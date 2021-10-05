---
title: CAN总线知识串联
date: 2021-05-29 13:48:48
tags: 
categories: 汽车电子
---


## CAN Matrix定义

通常主机厂在设计电气相关软件时，总是不可避免的要设计软件的输入和输出，而在汽车上各个电气部件之间都是通过CAN总线进行通信，因此在制定软件功能规范时往往第一步就是CAN Matrix的定义，如下图。  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210529135417253.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)  
一个完整的CAN Matrix通常应该包括以下信息  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210529135441416.png)
<!--more-->

## CAN Matrix转化为DBC

通常主机厂提供的信号矩阵只是一个Excel文件，而要将信号矩阵应用于开发、模拟、测试等，就需要先将其转换成DBC\(Database Can\)文件，DBC文件是用来描述CAN网络通信信号的一种格式文件。它可以用来监测与分析CAN网络上的报文数据，也可以用来模拟某个CAN节点。

简单来说，DBC文件可以理解为密码本，当车辆运行时，ECU的发送器根据密码本对外发送010101……消息，接收器将010101……消息根据密码本转换为相应的指令。  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210529135819155.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)

DBC文件的转换规则可见：_https://blog.csdn.net/u010808702/article/details/104152745_