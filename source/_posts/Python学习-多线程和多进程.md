---
title: Python学习-多线程和多进程
date: 2021-06-23 22:33:04
tags: 
categories: # Python
---

<!--more-->

### Python学习-多线程和多进程

- [基本概念](#_1)
- [线程](#_4)
- - [线程的创建](#_5)
  - [线程共享全局变量和锁](#_29)
- [进程](#_81)
- - [进程的创建](#_82)
  - [进程间的通信](#_117)

# 基本概念

1.  进程：程序的一次执行
2.  线程：CPU的基本调度单位

# 线程

## 线程的创建

线程的创建主要通过threading模块

```python
print('主线程开始')

from threading import Thread
import threading
from time import sleep

def sub_fun(arg1,arg2):
    print('子线程开始')
    print('子线程函数参数时：{0},{1}'.format(arg1,arg2))
    sleep(5)
    print('子进程结束')

thread = Thread(target=sub_fun, args=('参数1','参数2'))

thread.start()

thread.join()

print('主线程结束')
```

## 线程共享全局变量和锁

在一个进程内的所有线程共享全局变量，很方便在多个线程间共享数据  
缺点就是，线程是对全局变量随意遂改可能造成多线程之间对全局变量的混乱（即线程非安全）

```python
from threading import Thread
import time

num = 0 

def add1(n):
    global num
    for i in range(n):
        num = num+1
    print('in add1, num is {0}\n'.format(num))
    
def add2(n):
    global num
    for i in range(n):
        num = num+1
    print('in add2, num is {0}\n'.format(num))   

thread1 = Thread(target=add1, args=(1000000,))
thread1.start()

thread2 = Thread(target=add2, args=(1000000,))
thread2.start()

time.sleep(5)
print('final num is {0}\n'.format(num))
```

最后运行的结果是

```python
in add2, num is 1295511
in add1, num is 1324484
final num is 1324484
```

对num加1，2000000次，结果却不是2000000，这是由于线程共享全局变量

在num=0时，thread1 thread2同时取得num=0。  
此时thread1 sleeping，thread2 running， thread2使num=1  
然后thread2 sleeping，thread1 running， thread1使num=1  
这就导致两个线程重复操作了两次，num结果仍是1

简单来说就是线程被覆盖了，这时可以使用 threading库里面的锁对象 Lock 去保护

```python
lock = threading.Lock()

lock.acquire()
lock.release()
```

# 进程

## 进程的创建

在python中进程的创建主要通过Process函数  
Process\(\[group \[, target \[, name \[, args \[, kwargs\]\]\]\]\]\)

1.  target：如果传递了函数的引用，可以任务这个子进程就执行这里的代码
2.  args：给target指定的函数传递的参数，以元组的方式传递
3.  kwargs：给target指定的函数传递命名参数
4.  name：给进程设定一个名字，可以不设定
5.  group：指定进程组，大多数情况下用不到

Process创建的实例对象的常用方法：

1.  start\(\)：启动子进程实例（创建子进程）
2.  is\_alive\(\)：判断进程子进程是否还在活着
3.  join\(\[timeout\]\)：是否等待子进程执行结束，或等待多少秒
4.  terminate\(\)：不管任务是否完成，立即终止子进程

Process创建的实例对象的常用属性：

 1.     name：当前进程的别名，默认为Process-N，N为从1开始递增的整
 2.     pid：当前进程的pid（进程号）

```python
from multiprocessing import Process
import os
import time

def sub_fun():
        print('子进程运行中，pid=%d...' % os.getpid())

if __name__ == '__main__':
    print('父进程pid: %d' % os.getpid())
    for i in range(3):
        p = Process(target=sub_fun)
        p.start()
```

## 进程间的通信

进程间有多种通信机制，下面就常用的Queue为例进行说明

```python
from multiprocessing import Process,Queue
import os,time,random

def write(q):
    for value in ['a','b','c']:
        print('put {0} to queue'.format(value))
        q.put(value)
        time.sleep(random.random())

def read(q):
    while not q.empty():#此处死循环，ctrl+c终止
        value = q.get(True)
        print('get {0} to queue'.format(value))
        q.put(value)
        time.sleep(random.random())

if __name__ == '__main__':
    q = Queue()

    pw = Process(target=write, args=(q,))
    pr = Process(target=read, args=(q,))

    pw.start()
    pw.join()

    pr.start()
    pr.join()

    print('-----ok------')
```