---
title: CAN总线基本知识
date: 2021-05-25 20:19:01
tags: 
categories: 汽车电子
---


# CAN总线基本知识

## 基本概念

CAN 是Contoller Area Network 缩写，即控制域网络，简单来说就是用于汽车不同电子器件之间传输网络。  
CAN 总线两个主要ISO国际标准是：ISO11898和ISO11519  
<!--more-->
ISO11898 定义了通信速率为 125 kbps～1 Mbps 的**高速 CAN** 通信标准，属于闭环总线，传输速率可达1Mbps，总线长度 ≤ 40米。  
ISO11519 定义了通信速率为 10～125 kbps 的**低速 CAN**通信标准，属于开环总线，传输速率为40kbps时，总线长度可达1000米。

CAN为了减少外部电磁场对内部点评的干扰，通常采用双绞线

![在这里插入图片描述](https://img-blog.csdnimg.cn/img_convert/8c4f412321d012aca6ec4f23efb4ce5b.png)

### CAN的拓扑结构

下图中，左边是高速CAN总线的拓扑结构，右边是低速CAN总线的拓扑结构。

![[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-CVTFaKPI-1621944831661)(https://gitee.com/xiaolinzinvshen/article-pic/raw/master/2019071514355785.jpeg)]](https://img-blog.csdnimg.cn/20210525202118238.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)

### CAN信号表示

在CAN总线上，利用CAN\_H和CAN\_L两根线上的电位差来表示CAN信号。CAN总线上的电位差分为显性电平和隐性电平。其中显性电平为逻辑0，隐性电平为逻辑1。  
ISO11898标准（125kbps \~ 1Mbps）和ISO11519标准（10kbps \~ 125kbps）中CAN信号的表示分别如下所示：

![在这里插入图片描述](https://img-blog.csdnimg.cn/img_convert/5cbf37862a779c69d6737487a755c4d2.png)

### CAN信号传输

发送过程：CAN控制器将CPU传来的信号转为逻辑电平（即逻辑0-显性电平或者逻辑1-隐性电平）。CAN发射器接收逻辑电平之后，再将其转换为差分电平输出到CAN总线上。

![在这里插入图片描述](https://img-blog.csdnimg.cn/img_convert/8d8c61b486a991f265908f2404fc03f9.png)

接受过程则刚好相反。

![在这里插入图片描述](https://img-blog.csdnimg.cn/img_convert/8b83142a7ce96e17755ee71390e74e39.png)

## CAN通信网络结构

### OSI基本参照模型

OSI参考模型为7层，物理层、数据链路层、网络层、传输层、会话层、表示层和应用层，而CAN通信底层仅使用了物理层和数据链路层

![在这里插入图片描述](https://img-blog.csdnimg.cn/img_convert/e40676e4e27a71ab3ea8eb9418914cad.png)

### CAN总线报文类型

CAN总线的报文类型主要有五种，数据帧、远程帧、错误帧、过载帧、帧间隔  
下面以数据帧为例进行简单介绍，其帧结构如下图所示，包含七个段：**帧起始、仲裁段、控制段、数据段、CRC段、ACK段、帧结束**

![[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-fHkSnbCs-1621944831669)(https://gitee.com/xiaolinzinvshen/article-pic/raw/master/20190715151924879.png)]](https://img-blog.csdnimg.cn/20210525201812946.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)

帧起始  
仲裁域：通过11位标识符对报文优先级进行判断，RTR位判断为数据帧还是远程帧  
控制域：描述数据域中的字节数  
数据域：8个字节传递信息，如转速等  
CRC域：循环冗余校验，避免因物理层传递出现丢失的情况  
ACK域：表明总线中至少有一个节点正确接收到发送的报文，没有发生干扰  
帧结束