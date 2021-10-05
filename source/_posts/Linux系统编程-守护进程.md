---
title: Linux系统编程-守护进程
date: 2021-06-14 13:41:19
tags: 
categories: Linux
---

<!--more-->

### 基本概念

1.  Linux后台服务进程
2.  独立于控制终端
3.  周期性的执行某种任务
4.  不受用户登陆和注销的影响
5.  一般采用以d结尾的名字

### 进程组和会话

进程组: 一个进程包含多个进程  
会话: 多个组组成一个会话.

创建会话的进程不能是组长进程;  
一般创建会话是父进程先fork子进程, 然后父进程退出, 让子进程调用setsid函数  
创建一个会话, 这个子进程既是会长也是组长;  
只要是创建了会话, 这个进程就脱离了控制终端的影响.

![[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-zja3K36a-1623649224301)(Untitled.assets/image-20210614124433571.png)]](https://img-blog.csdnimg.cn/20210614134052443.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0hhb190b3A=,size_16,color_FFFFFF,t_70)

### 创建守护进程

 1.     父进程fork子进程, 然后父进程退出.  
    目的是: 子进程肯定不是组长进程, 为后续调用setsid函数提供了条件.
 2.     子进程调用setsid函数创建一个新的会话.  
    该子进程成了该会话的会长  
    该子进程成了该组的组长进程.  
    不再受控制终端的影响了
 3.     改变当前的工作目录, chdir -----不是必须的
 4.     重设文件掩码, umask\(0000\) -----不是必须的
 5.     关闭STDIN\_FILENO STDOUT\_FILENO STDERR\_FILENO —不是必须的
 6.     核心操作

```c
//创建守护进程
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/time.h>

void myfunc(int signo)
{
	//打开文件
	int fd = open("mydemon.log", O_RDWR | O_CREAT | O_APPEND, 0755);
	if(fd<0)
	{
		return;
	}

	//获取当前的系统时间
	time_t t;
	time(&t);
	char *p = ctime(&t);
	
	//将时间写入文件
	write(fd, p, strlen(p));

	close(fd);

	return;
}

int main()
{
	//父进程fork子进程, 然后父进程退出
	pid_t pid = fork();
	if(pid<0 || pid>0)
	{
		exit(1);
	}
	
	//子进程调用setsid函数创建会话
	setsid();

	//改变当前的工作目录
	chdir("/home/itcast/log");

	//改变文件掩码
	umask(0000);

	//关闭标准输入,输出和错误输出文件描述符
	close(STDIN_FILENO);
	close(STDOUT_FILENO);
	close(STDERR_FILENO);

	//核心操作
	//注册信号处理函数
	struct sigaction act;
	act.sa_handler = myfunc;
	act.sa_flags = 0;
	sigemptyset(&act.sa_mask);	
	sigaction(SIGALRM, &act, NULL);

	//设置时钟
	struct itimerval tm;
	tm.it_interval.tv_sec = 2;
	tm.it_interval.tv_usec = 0;
	tm.it_value.tv_sec = 3;
	tm.it_value.tv_usec = 0;
	setitimer(ITIMER_REAL, &tm, NULL);

	printf("hello world\n");

	while(1)
	{
		sleep(1);
	}
}
```