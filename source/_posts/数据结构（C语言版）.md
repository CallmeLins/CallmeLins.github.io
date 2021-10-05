---
title: 数据结构（C语言版）
date: 2021-06-06 14:38:30
tags: 
categories: # C/C++
---

<!--more-->

## 数据结构（C语言版）

### 绪论

1、在计算机运行过程中，如何合理的组织数据、高效的处理数据，这就是数据结构

2、数据结构包括两个方面的内容：数据的逻辑结构和存储结构  
① 逻辑结构是从逻辑关系上描述数据，通常有四类：集合、线性、树状和图状  
② 存储结构是逻辑结构在计算机中的存储表示，有两类：顺序和链式

3、抽象数据类型（ADT）：提供类型属性和相关操作的抽象描述，下面是链表的抽象数据类型的定义，定义完抽象数据类型就可以进行接口的开发和实现了

4、算法是为了解决某类问题而规定的操作方法  
① 算法具有五个特性：有穷性、确定性、可行性、输入和输出。  
② 算法的优劣应该从以下四方面来评价：正确性、可读性、健壮性和高效性

5、算法的优劣主要是时间复杂度和空间复杂度

### 链表

#### 建立抽象

```
类型名：   简单链表
类型属性： 可以存储一系列项
类型操作： 初始化链表为空
			确定链表为空
			确定链表已满
			确定链表中的项数
			在链表末尾添加项
		  遍历链表，处理链表中的项
		  	清空链表
```

#### 建立接口

这个链表中主要分为两部分：表示数据的结构和操作数据的函数

在链表中每个链结叫做节点（_node_），每个节点包含了存储内容的信息和指向下一个节点的指针，首先对节点进行定义

```python
struct LinkNode
{
	void * data;
	struct LinkNode * next;
};
```

下面对链表结构体进行定义，包括节点信息和链表的长度信息

```python
struct LList
{
	//头节点
	struct LinkNode pHeader;
	//链表长度
	int m_size;
};
//使用typedef定义一个空指针作为链表的返回值
typedef void * LinkList;
```

以上，关于抽象数据类型的属性部分定义完成，接下来对类型的操作方法进行定义

```python
//初始化链表
LinkList init_LinkList()
//插入链表
void insert_LinkList(LinkList list, int pos, void * data)
//遍历链表
void foreach_LinkList(LinkList list, void(*myForeach)(void *))
//删除链表  按位置
void removeByPos_LinkList(LinkList list, int pos)
```

#### 实现接口

```python
void init_LinkList()
{
    struct LList * mylist = malloc(sizeof(strict LList))
    
    if(mylist == NULL){return NULL;}
    
    mylist->pHeader.data = NULL;
    mylist->pHeader.next = NULL;
    mylist->m_size = 0;
    
    return mylist;
}

void insert_LinkList(LinkList list, int pos, void * data)
{
    if(list == NULL){return;}
    if(data == NULL){return;}
    struct LList *mylist = list;
    if(pos<0 || pos>mylist->m_size){pos = mylist->m_size;}
    
    struct LinkNode * pCurrent = &mylist->pHeader;
    for(int i=0; i<pos; i++){pCurrent = pCurrent->next;}
    
    struct LinkNode * newNode = malloc(sizeof(struct LinkNode));
    neNode->data = data;
    neNode->next = NULL;
    
    newNode->next = pCurrent->next;
    pCurrent->next = pCurrent;
    
    mylist->m_size++;    
}

void foreach_LinkList(LinkList list, void(*myForeach)(void *))
{
	if (list ==NULL){return;}

	struct LList * mylist = list;

	struct LinkNode* pCurrent = mylist->pHeader.next;

	for (int i = 0; i < mylist->m_size;i++)
	{
		myForeach(pCurrent->data);
		pCurrent = pCurrent->next;
	}
}

void removeByPos_LinkList(LinkList list, int pos)
{
	if ( list == NULL){return;}

	struct LList * mylist = list;

	if (pos < 0 || pos > mylist->m_size - 1){return;}

	struct LinkNode * pCurrent = &mylist->pHeader;
	for (int i = 0; i < pos;i++){pCurrent = pCurrent->next;}

	struct LinkNode * pDel = pCurrent->next;

	pCurrent->next = pDel->next;

	free(pDel);
	pDel = NULL;

	mylist->m_size--;
}


```