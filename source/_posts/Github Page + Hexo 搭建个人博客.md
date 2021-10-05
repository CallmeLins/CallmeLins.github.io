---
title: Github Page + Hexo 搭建个人博客
categories: Hexo
---
复制代码

## Github Page + Hexo 搭建个人博客

### 准备环境

首先查看环境是否安装，主要用到的工具有git，node，npm

```bash
git version
node -v
npm -v
```

### 安装Hexo

如果以上环境准备好了就可以使用 npm 开始安装 Hexo 了。也可查看 [Hexo](https://link.segmentfault.com/?url=https%3A%2F%2Fhexo.io%2Fzh-cn%2F) 的详细文档
在命令行输入执行以下命令：

`npm install -g hexo-cli`

安装 Hexo 完成后，再执行下列命令，Hexo 将会在指定文件夹中新建所需要的文件

```bash
hexo init myBlog
cd myBlog
npm install
```

此时已安装完成，可以启动服务了

`hexo s`

在浏览器中输入 http://localhost:4000 回车就可以预览效果了

### Hexo 部署

安装 [hexo-deployer-git](https://github.com/hexojs/hexo-deployer-git)。

`npm install hexo-deployer-git --save`

修改配置。

```bash
deploy:
  type: git
  repository: git@github.com:xxx/xxx.git,branchName
  branch: master
  message: update myblog
```

### Hexo 备份

首先在 github 上 master 主分支下创建 hexo 空白分支
安装 hexo-git-backup 插件

`npm install hexo-git-backup --save`

到 Hexo 博客根目录的 `_config.yml` 配置文件里添加以下配置：

```bash
backup:
    type: git
    message: update myblog
    repository:
       github: git@github.com:xxx/xxx.git,branchName
```

然后使用命令即可

`hexo b`

### Hexo 文章显示摘要

在新版本中 _config.yml 下已经没有 auto_excerpt， 官方对于此选项已不支持，要显示摘要只有通过加 `<!--more-->`的方式，但此方式太繁琐，另外的方法是通过安装插件的方法

1：使用npm安装hexo-excerpt

```bash
npm install hexo-excerpt --save
```

2：在站点配置文件中添加

```bash
excerpt:
  depth: 5  
  excerpt_excludes: []
  more_excludes: []
  hideWholePostExcerpts: true
