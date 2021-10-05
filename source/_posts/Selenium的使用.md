---
title: Selenium的使用
date: 2021-07-04 19:48:42
tags: 
categories: Python
---

<!--more-->

### Selenium的使用

- [选择元素的基本方法](#_1)
- - [通过webdriver自带的元素选择器等选择元素](#webdriver_2)
  - - [选择元素](#_3)
    - [操纵元素](#_38)
  - [通过CSS Selector 选择元素](#CSS_Selector__52)
  - [通过xpath选择元素](#xpath_86)

# 选择元素的基本方法

## 通过webdriver自带的元素选择器等选择元素

### 选择元素

通过`find_element_by_xxxxxx`或`find_elements_by_xxxxxx`

`xxxxx`为选择元素的关键字，常用关键字有：

```python
1.id定位：find_element_by_id(self, id_)
2.name定位：find_element_by_name(self, name)
3.class定位：find_element_by_class_name(self, name)
4.tag定位：find_element_by_tag_name(self, name)
```

1.  使用 find\_elements 选择的是符合条件的**所有**元素， 如果没有符合条件的元素， 返回空列表
2.  使用 find\_element 选择的是符合条件的**第一个**元素， 如果没有符合条件的元素， 抛出NoSuchElementException 异常

通常程序的运行速度是远远大于网页请求渲染速度的，为了避免选择元素时`NoSuchElementException`异常的抛出，可以使用Selenium 的 Webdriver 对象 中的`implicitly_wait`方法

该方法接受一个参数， 用来指定 最大等待时长。

```python
from selenium import webdriver

wd = webdriver.Chrome()

wd.implicitly_wait(10)

wd.get('https://www.baidu.com')

element = wd.find_element_by_id('kw')

element.send_keys('lpl\n')

element = wd.find_element_by_id('1')

print (element.text)
```

### 操纵元素

1.  通过 WebElement 对象的`.click()`函数点击元素
2.  输入框的操作可以用 WebElement 对象的`.clear()`和`.send_keys()`方法
    ```python
    element.clear() # 清除输入框已有的字符串
    element.send_keys('白月黑羽') # 输入新字符串
    ```
3.  获取元素的文本信息可以通过`.text`方法
4.  获取元素属性和输入框内的文本则可以通过`.get_attribute()`方法
    ```python
    get_attribute('class') # 获取元素属性
    get_attribute('value')) # 获取输入框中的文本
    ```

## 通过CSS Selector 选择元素

通过 CSS Selector 选择元素的方法是

```python
find_element_by_css_selector(CSS Selector参数)
find_elements_by_css_selector(CSS Selector参数)
```

常用的选择方法

| 选择器 | 表达式 |
| --- | --- |
| 根据class选择 | .class值 |
| 根据id选择 | #id值 |
| 父类下的子类 | 元素1 空格/> 元素2 |
| 根据属性选择 | div\[class=‘SKnet’\] |

根据属性选择还可以通过通配符选择以包含…开头结尾的元素

1.  选择a节点，里面的href属性包含了 miitbeian 字符串，`a[href*="miitbeian"]`
2.  选择a节点，里面的href属性以 http 开头 ，`a[href^="http"]`
3.  要选择a节点，里面的href属性以 gov.cn结尾 ，`a[href$="gov.cn"]`
4.  如果一个元素具有多个属性`div[class=misc][ctype=gun]`

CSS选择器还可以联合使用，如`div.footer1 > span.copyright`  
以及进行组选择如 `div.footer1 ， span.copyright`

最后还可以按照次序进行选择

| 选择器 | 表达式 |
| --- | --- |
| 父元素的第n个子节点 | span:nth-child\(2\) |
| 父元素的倒数第n个子节点 | p:nth-last-child\(1\) |
| 父元素的第几个某类型的子节点 | span:nth-of-type\(1\) |
| 父元素的倒数第几个某类型的子节点 | p:nth-last-of-type\(2\) |
| 相邻兄弟节点选择 | h3 + span |
| 后续所有兄弟节点选择 | h3 \~ span |

## 通过xpath选择元素

通过 xpath 选择元素的方法是

```python
find_element_by_xpath(xpath参数)
find_elements_by_xpath(xpath参数)
```

xpath 可以通过**相对路径**和**绝对路径**两种方式进行选择，通常相对路径使用较多

常用的选择方法

| 选择器 | 表达式 |
| --- | --- |
| 根据属性选择 | \[\@属性名=‘属性值’\] |
| 属性值包含字符串 | //\*\[contains\(\@style,‘color’\)\] |
| 属性值以字符串开头 | //\*\[starts-with\(\@style,‘color’\)\] |
| 属性值以字符串结尾 | //\*\[ends-with\(\@style,‘color’\)\] |

xpath选择器进行组选择用`|` 进行分割，类似css的`,`

同样的xpath也可以通过次序进行选择

| 选择器 | 表达式 |
| --- | --- |
| 某类型 第几个 子元素 | //p\[2\] |
| 某类型 倒数第几个 子元素 | //p\[last\(\)-1\] |
| 范围选择 | //option\[position\(\)\<=2\] |
| 后续所有兄弟节点选择 | following-sibling:: |

同时xpath的优势在于可以使用子节点反选父节点使用`//*[@id='china']/../../..`

最后，以上包括css，xpath都可以通过chrome的开发者工具栏中`ctrl+f`进行表达式的验证
