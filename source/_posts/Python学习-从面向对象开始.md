---
title: Python学习-从面向对象开始
date: 2021-06-21 22:30:25
tags: 
categories: Python
---

<!--more-->

### Python学习-从面向对象开始

- [面向对象](#_1)
- - [类和实例](#_2)
  - [访问限制](#_75)
  - [继承和多态](#_88)

# 面向对象

## 类和实例

**面向对象编程**\(Object Oriented Programming\)\(OOP\)，是一种程序设计思想

与之相对应的事**面向过程编程**\(Procedure Oriented Programming\)\(POP\) 两者区别如下：

把大象放进冰箱需要几个步骤？

 1.     面向过程编程：  
    打开冰箱、放进大象、关闭冰箱

```python
def open_icebox():
    print("open icebox")

def close_icebox():
    print("close icebox")

def put_elephant():
    print("put elephant")    

if __name__ == "__main__":
    open_icebox()
    put_elephant()
    close_icebox()
```

 2.     面向对象编程：  
    冰箱一个类，大象一个类，放的动作一个类

```python
class icebox():
    def __init__(self,size,brand):
        self.size = size
        self.brand = brand
    
    def open_icebox(self):
        print("open size:%d brand:%s icebox" % (self.size,self.brand))

    def close_icebox(self):
        print("close size:%d brand:%s icebox" % (self.size,self.brand)) 


class elephant():
    def __init__(self,size,type):
        self.size = size
        self.type = type  

    def print_arr(self):
        print("elephant size is:%d type is:%s " % (self.size,self.type)) 

class action():
    def __init__(self,action) -> None:
        self.action = action
    
    def start_action(self):
        if self.action == 'put':
            print('put')
        elif self.action == 'get':
            print('get')


if __name__ == "__main__":
    icebox = icebox(100,'songxia')
    elephant = elephant(10,'yazhouxiang')
    action = action('put')

    icebox.open_icebox()
    action.start_action()
    elephant.print_arr()
    icebox.close_icebox()
```

面向对象是以功能来划分问题，功能上的统一保证了面向对象设计的**可扩展性**。比如我想把大象取出，就只需要在动作类中添加取出的方法即可，并且可以更改冰箱的种类、大象的种类

其中\_\_init\_\_方法的第一个参数永远是self，表示创建的实例本身，此方法有点类似与C++中的构造函数，比如一个人在出生时就携带了自身的属性，如人类、男性这样的属性，\_\_init\_\_方法就是在创建一个实例的同时，初始化一个自带的属性。

## 访问限制

类的最重要的属性之一就是**封装**，即从外部无法直接访问到类的属性

与C++中类的关键字private关键字类似，python中也有类似的方法，如下在init方法中加上双下划线即可

```python
class icebox():
    def __init__(self,size,brand):
        self.__size = size
        self.__brand = brand
```

此时如果想访问或更改类属性，就可以在类中定义相应的方法，通过类方法更改类属性，同时可以在方法中，可以对参数做检查，避免传入无效的参数

## 继承和多态

类的第二个特性-**继承**

子类可以继承父类的所有方法，如果需要子类自己的方法，只需要在子类中重写父类的方法就会自动覆盖

```python
class elephant():
    def run(self):
        print("elephant is runing") 

class asia_elephant(elephant):
    pass

if __name__ == "__main__":
    elephant = asia_elephant()
    elephant.run()
```

类的第二个特性-**多态**

在如下代码中可以发现函数run\_twice\(elephant\)中传入不同的实例对象时，其结果也随之变化，这就是多态

```python
class elephant(object):
    def run(self):
        print("elephant is runing") 

class asia_elephant(elephant):
    def run(self):
        print("asia elephant is runing")

class africa_elephant(elephant):
    def run(self):
        print("africa elephant is runing")

if __name__ == "__main__":
    asia_elephant = asia_elephant()
    africa_elephant = africa_elephant()

    def run_twice(elephant):
        elephant.run()
        elephant.run()
    
    run_twice(asia_elephant)
    run_twice(africa_elephant)

```
