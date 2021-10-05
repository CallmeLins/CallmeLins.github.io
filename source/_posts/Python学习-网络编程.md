---
title: Python学习-网络编程
date: 2021-06-25 22:44:30
tags: 
categories: Python
---


### Python学习-网络编程

- [引言](#_1)
- - [网络](#_5)
  - [IP](#IP_7)
  - [端口](#_9)
<!--more-->
  - [协议](#_11)
- [TCP/IP网络模型](#TCPIP_15)
- - [UDP](#UDP_27)
  - [TCP](#TCP_60)

# 引言

计算机网络是学习编程的基础四大件，而网络协议则是计算机网络的基础

TCP/IP 中有两个具有代表性的传输层协议，分别是 TCP 和 UDP，本文将介绍下这两者以及它们之间的区别。

## 网络

网络编程就是通过程序使不同主机上的软件能够通过网络进行通信

## IP

ip是用来在网络中标记一台电脑的地址，在本地局域网内是唯一的。

## 端口

一台电脑有一个ip，但是一台电脑上有多个软件，怎么识别到不同软件进行通信，这时就需要端口，每个软件的端口在本地主机上都是唯一的。

## 协议

有了ip有了端口，好比商家有了你家小区的地址，单元号，但是该采用什么快递，怎么确保你收到货这些并没有确定，这时就需要商家-顾客有一个统一的规定对这些内容进行规定，这就是**协议**

所以，ip地址+协议+端口 三者结合才可以可以标识网络中的进程，并利用这个标识进行进程之间的通信

# TCP/IP网络模型

计算机与网络设备要相互通信，双方就必须基于相同的方法。比如

- 如何探测到通信目标
- 由哪一边先发起通信
- 使用哪种语言进行通信
- 怎样结束通信

等等都需要事先确定规则。这种规则就是协议（protocol）

TCP/IP 是互联网相关的各类协议族的总称，比如：TCP，UDP，IP，FTP，HTTP，ICMP，SMTP 等都属于 TCP/IP 族内的协议。  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210624220714298.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)

## UDP

socket\(简称 套接字\) 是进程间通信的一种方式，通过socket函数，我们可以指定期望的通信协议类型

函数 socket.socket 创建一个 socket，该函数带有两个参数  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210625212120166.png)  
第一个参数指明了协议簇，目前支持5种协议簇，最常用的有AF\_INET\(IPv4协议\)和AF\_INET6\(IPv6协议\)  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210625212203662.png)  
第二个参数指明套接口类型，主要有种类型可选：SOCK\_STREAM\(字节流套接口\)、SOCK\_DGRAM\(数据报套接口\)和SOCK\_RAW\(原始套接口\)

下面是UDP客户端和服务器之间通信交互的时间线，相应的代码实现也是根据此框图进行实现  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210625212814498.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)

```python
from socket import *

udp_socket = socket(AF_INET, SOCK_DGRAM)

dest_addr = ('192.168.123.1', 8888)

send_data = input('请输入要发送的数据:')

udp_socket.sendto(send_data.encode('utf-8'), dest_addr)

recv_data = udp_socket.recvfrom(1024)

# 接收到的数据recv_data是一个元组
# 第1个元素是对方发送的数据
# 第2个元素是对方的ip和端口
print(recv_data[0].decode('gbk'))
print(recv_data[1])

udp_socket.close()
```

## TCP

\*\*TCP协议，传输控制协议（英语：Transmission Control Protocol，缩写为 TCP）\*\*是一种面向连接的、可靠的、基于字节流的传输层通信协议

TCP通信需要经过创建连接、数据传送、终止连接三个步骤

下面是TCP客户端和服务器之间通信交互的时间线，相应的代码实现也是根据此框图进行实现  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210625223637898.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)

```python
from socket import *

tcp_client = socket(AF_INET, SOCK_DGRAM)

server_ip = input('input server ip:')
server_port = input('input server port:')

tcp_client.connect((server_ip,server_port))

send_data = input('input send data:')

tcp_client.send(send_data)

tcp_client.send(send_data.encode("gbk"))

recvData = tcp_client.recv(1024)
print('接收到的数据为:', recvData.decode('gbk'))

tcp_client.close()
```
