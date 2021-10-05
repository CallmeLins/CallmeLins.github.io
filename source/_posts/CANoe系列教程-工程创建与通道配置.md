---
title: CANoe系列教程-工程创建与通道配置
date: 2021-05-27 20:04:18
tags: 
categories: 汽车电子
---

<!--more-->

# 工程创建与通道配置

点击File中的New按钮选择相应的模板后点击Create Configuration，一个工程文件就创建完成了  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210526210840844.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)

# 通道数目和通信波特率配置

选择Channel Usage 就可以对总线的通道数进行配置  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210526211036227.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)  
选择Network Hardware对CAN网络的通讯速率进行配置，通讯速率需和连接的ECU保持一致  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210527194905414.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)

# 软件通道与硬件通道的映射配置

此步将物理通道和逻辑通道之间进行匹配和映射，选择Driver将物理通道分别分配给模板中的两路CAN网络，此时CANoe已经可以接收来自ECU的报文了  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210527195234173.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)![在这里插入图片描述](https://img-blog.csdnimg.cn/20210527195326903.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)

# 添加总线通信数据库

选择add时仅添加数据库，选择wizard时可以在添加数据库的同时将仿真节点导入到仿真框图中，此时CANoe就可以通过数据库对节点进行仿真  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210527195942723.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)