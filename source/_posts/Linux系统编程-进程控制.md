---
title: Linux系统编程-进程控制
date: 2021-06-10 13:09:41
tags: 
categories: Linux
---

<!--more-->

### 基本概念

#### 程序和进程

1.  程序：编译好的二进制文件，占用磁盘空间，静态
2.  进程：程序的运行过程，占用内存、CPU等，动态

#### 并行和并发

1.  并行：一边吃饭一边看电影，这就是并行
2.  并发：在一个时间段内, 是在同一个cpu上, 同时运行多个程序。如：若将CPU的1S的时间分成1000个时间片，每个进程执行完一个时间片必须无条件让出CPU的使用权，这样1S中就可以执行1000个进程。**简单来说就是可以先暂停吃饭去看电影，再暂停看电影去吃饭，这就是并发**

#### 进程状态

初始态，就绪态，运行态，挂起态与终止态

### 创建进程

Fork函数

1.  函数作用：创建子进程
2.  原型: pid\_t fork\(void\);
3.  函数参数：无
4.  返回值：调用成功:父进程返回子进程的PID，子进程返回0； 调用失败:返回-1，设置errno值。

● fork函数代码片段实例

```c
......
	pid_t pid = fork();
	if(pid<0)
	{
		perror("fork error");
		return -1;
	}
	else if(pid>0)
	{
		printf("father: [%d], pid==[%d], fpid==[%d]\n", pid, getpid(),getppid());
		//sleep(1);
	}
	else if(pid==0) 
	{
		printf("child: pid==[%d], fpid==[%d]\n", getpid(), getppid());
	}
......
```

### exec函数族

如果想在一个进程内部执行系统命令或者是应用程序, 可以使用execl和execlp函数拉起可执行程序或者命令.

 1.     execl\(\) 通常用来执行用户自定义程序
 2.     execlp\(\) 通常用力啊执行系统命令，如要执行自定义程序，需将程序加入系统环境变量

```c
.......
else if(pid==0) //子进程
	{
		printf("child: pid==[%d], fpid==[%d]\n", getpid(), getppid());
		execl("/bin/ls", "ls", "-l", NULL);
		execl("./test", "test", "hello", "world", "ni", "hao", NULL);
		execlp("ls", "ls", "-l", NULL);
......
```

### 回收进程

当一个进程退出之后，进程能够回收自己的用户区的资源，但是不能回收内核空间的PCB资源，必须由它的父进程调用wait或者waitpid函数完成对子进程的回收，避免造成系统资源的浪费。

#### 孤儿进程

孤儿进程是指父进程已死而子进程还活着，此时子进程就是孤儿进程。  
孤儿进程会被init进程领养。

#### 僵尸进程

若子进程死了，父进程还活着， 并且父进程没有调用wait或waitpid函数回收子进程，此时子进程就成了僵尸进程。  
由于僵尸进程已死，不能用kill命令杀死子进程，回收子进程的方法如下：  
杀死父进程->僵尸进程被init进程领养->由init回收

#### 回收函数

##### 函数原型

```c
#include <sys/wait.h>
pid_t wait(int * statloc);
pid_t waitpid(pid_t pid,int *statloc,int options);
```

调用wait或waitpid的进程发生的情况如下：

1.  如果所有子进程都还在运行，则阻塞
2.  如果一个子进程已终止，正等待父进程获取其终止状态，则取得该子进程的终止状态立即返回
3.  如果它没有任何子进程，则立即出错返回