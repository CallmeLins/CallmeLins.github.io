---
title: Linux系统编程-进程间通讯
date: 2021-06-13 14:17:36
tags: 
categories: Linux
---

<!--more-->

### 基本概念

Linux环境下，进程地址空间相互独立，每个进程都有不同的用户地址空间，一个进程的全局变量在另一个中是看不到的，要交换数据必须通过内核，在内核中开辟一块缓冲区，一个进程写，另一个读，这种机制就是**进程间通信**

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210613141653818.png)

常用的进程间的通讯方式有以下几种：

1.  管道 \(使用最简单\)
2.  信号 \(开销最小\)
3.  共享映射区 \(无血缘关系\)
4.  本地套接字 \(最稳定\)

### 管道Pipe

#### 创建管道

**pipe函数**

1.  函数作用: 创建一个管道
2.  函数原型: int pipe\(int fd\[2\]\);
3.  函数参数: 若函数调用成功，fd\[0\]存放管道的读端，fd\[1\]存放管道的写端
4.  返回值: 成功返回0；失败返回-1，并设置errno值。

函数调用成功返回读端和写端的文件描述符，其中fd\[0\]是读端， fd\[1\]是写端\*\*，\*\*向管道读写数据是通过使用这两个文件描述符进行的，读写管道的实质是操作内核缓冲区

![在这里插入图片描述](https://img-blog.csdnimg.cn/2021061314171373.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)

**创建步骤总结：**

 1.     父进程调用pipe函数创建管道，得到两个文件描述符fd\[0\]和fd\[1\]，分别指向管道的读端和写端。
 2.     父进程调用fork创建子进程，那么子进程也有两个文件描述符指向同一管。
 3.     父进程关闭管道读端，子进程关闭管道写端。父进程可以向管道中写入数据，子进程将管道中的数据读出，这样就实现了父子进程间通信。

```c
......
int main()
{
    int fd[2];
    int ret = pipe(fd);
    if(ret<0)
    {
        perror("pipe error");
        return -1;
    }

    pid_t pid=fork();
    if((pid<0))
    {
        perror("fork error");
        return -1;
    }
    else if(pid>0)
    {
        close(fd[0]);
        sleep(5);
        write(fd[1],"hello world",strlen("hello world"));
        wait(NULL);
    }
    else
    {
        close(fd[1]);
        char buf[64];
        memset(buf,0x00,sizeof(buf));
        int n=read(fd[0],buf,sizeof(buf));
        printf("read over, n==[%d], buf==[%s]\n", n, buf);
    }
    return 0;
}
......
```

### FIFO

**FIFO常被称为命名管道**，以区分管道\(pipe\)。管道\(pipe\)只能用于“有血缘关系”的进程间通信。但通过FIFO，不相关的进程也能交换数据。

创建方式：

1.  **命令**：mkfifo 管道名

2.  **库函数**：int mkfifo\(const char \*pathname, mode\_t mode\); 成功：0； 失败：-1

    一旦使用mkfifo创建了一个FIFO，就可以使用open打开它，常见的文件I/O函数都可用于fifo。如：close、read、write、unlink等。

使用FIFO进行进程间通讯：

进程A：

1.  创建一个fifo文件：myfifo
2.  调用open函数打开myfifo文件
3.  调用write函数写入一个字符串如：“hello world”（其实是将数据写入到了内核缓冲区）
4.  调用close函数关闭myfifo文件

进程B：

1.  调用open函数打开myfifo文件
2.  调用read函数读取文件内容（其实就是从内核中读取数据）
3.  打印显示读取的内容
4.  调用close函数关闭myfifo文件