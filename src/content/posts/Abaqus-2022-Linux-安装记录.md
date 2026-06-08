---
title: Abaqus 2022 Linux 安装记录
date: 2026-06-08
categories: 运维
tags: [Ubuntu, CAE, FEA]
---

> 系统：Ubuntu（基于 Manjaro/Arch 教程适配）
> 安装日期：2026-06-08
> 安装目录：`/home/xfusion/Workspace/abaqus/`

## 1. 软件获取与解压

安装包为 4 个 7z 分卷（共 7.8G）：

```
Abaqus_2022_Linux.7z.001
Abaqus_2022_Linux.7z.002
Abaqus_2022_Linux.7z.003
Abaqus_2022_Linux.7z.004
```

解压命令（需安装 `p7zip-full`）：

```bash
sudo apt install p7zip-full
7z x Abaqus_2022_Linux.7z.001 -pwww.nekopara.uk
```

解压后得到目录 `Abaqus_2022/`，内含：

- `DS.SIMULIA.Suite.2022.Linux64/` — 安装包
- `ABAQUSLM__lmgrd__SSQ.lic` — 许可证文件

## 2. 安装前准备

### 2.1 赋予执行权限

```bash
chmod -R 777 DS.SIMULIA.Suite.2022.Linux64/
```

### 2.2 修改发行版检测脚本（本安装包已预制）

安装包内的 Linux.sh 已修改 `DSY_OS_Release` 为 `"CentOS"`。

需检查的脚本位置：

- `1/inst/common/init/Linux.sh`
- `3/*/Linux64/1/inst/common/init/Linux.sh`
- `4/SIMULIA_EstablishedProducts/Linux64/1/inst/common/init/Linux.sh`
- `5/*/Linux64/1/inst/common/init/Linux.sh`

修改内容：将 `DSY_OS_Release=\`lsb_release --short --id |sed 's/ //g'\`` 改为 `DSY_OS_Release="CentOS"`

## 3. 安装 FLEXnet License Server

### 3.1 安装依赖

```bash
sudo apt install patchelf libjpeg62
```

> Ubuntu 上需额外安装 `libxcb-xinerama0`，否则 GUI 安装程序启动时报错 `libxcb-xinerama.so.0: cannot open shared object file`。
>
> ```bash
> sudo apt install libxcb-xinerama0
> ```

### 3.2 运行安装程序

```bash
cd DS.SIMULIA.Suite.2022.Linux64/3/SIMULIA_FLEXnet_LicenseServer/Linux64/1/
./StartGUI.sh
```

**GUI 操作：**

- 安装目录：改为 `/home/xfusion/Workspace/abaqus/SIMULIA`
- 勾选 "Start FLEXnet License Server after installation"

> **注意**：License Server 和 Established Products 不能安装在同一目录。

### 3.3 复制许可证文件

```bash
cp Abaqus_2022/ABAQUSLM__lmgrd__SSQ.lic \
   /home/xfusion/Workspace/abaqus/SIMULIA/linux_a64/code/bin/
```

### 3.4 修补 lmgrd 和 ABAQUSLM 的 ELF 解释器

Ubuntu 上 `ld-linux` 位于 `/lib64/ld-linux-x86-64.so.2`（而非 `/usr/lib/`），需要修复：

```bash
patchelf --set-interpreter /lib64/ld-linux-x86-64.so.2 \
  /home/xfusion/Workspace/abaqus/SIMULIA/linux_a64/code/bin/lmgrd

patchelf --set-interpreter /lib64/ld-linux-x86-64.so.2 \
  /home/xfusion/Workspace/abaqus/SIMULIA/linux_a64/code/bin/ABAQUSLM
```

### 3.5 创建 /usr/tmp 目录

许可证服务器会写 `/usr/tmp/.flexlm`，需要提前创建：

```bash
sudo mkdir -p /usr/tmp && sudo chmod 1777 /usr/tmp
```

### 3.6 启动许可证服务器

```bash
/home/xfusion/Workspace/abaqus/SIMULIA/linux_a64/code/bin/lmgrd \
  -c /home/xfusion/Workspace/abaqus/SIMULIA/linux_a64/code/bin/ABAQUSLM__lmgrd__SSQ.lic
```

启动成功后会输出 vendor daemon 信息，显示所有可用 feature。

## 4. 安装 Established Products（主程序）

```bash
cd DS.SIMULIA.Suite.2022.Linux64/4/SIMULIA_EstablishedProducts/Linux64/1/
./StartGUI.sh
```

**GUI 操作：**

| 项目 | 值 |
|------|-----|
| 安装目录 | `/home/xfusion/Workspace/abaqus/SIMULIA_EstProduces` |
| 组件选择 | 全选 |
| 许可证设置 | 跳过（Skip license server configuration） |
| 启动命令目录 | `/home/xfusion/Workspace/abaqus/SIMULIA_EstProduces/Commands` |
| 外部插件目录 | `/home/xfusion/Workspace/abaqus/SIMULIA_EstProduces/CAE/plugins/2022` |
| 工作目录 | `/home/xfusion/Workspace/abaqus/SIMULIA_EstProduces/temp` |

安装完成后输出：

```
The Abaqus command for this release is: abq2022
The Abaqus commands directory can be found at: .../Commands
```

目录下生成启动命令链接：

```
Commands/
├── abq -> abq2022
├── abq2022 -> .../linux_a64/code/bin/SMALauncher
├── fe-safe -> fe-safe2022
└── tosca -> tosca2022
```

## 5. 配置许可证

编辑 `custom_v6.env`：

```bash
vim SIMULIA_EstProduces/linux_a64/SMA/site/custom_v6.env
```

注释掉 `importEnv('licensing.env')`，添加 FLEXNET 配置：

```env
license_server_type=FLEXNET
abaquslm_license_file="27800@localhost"
#importEnv('licensing.env')
```

> `27800` 即 lmgrd 启动时监听的默认端口。

## 6. 启动 Abaqus CAE

```bash
cd /home/xfusion/Workspace/abaqus/SIMULIA_EstProduces/Commands
./abq2022 cae
```

## 7. 设置许可证开机自启（可选）

创建 systemd 服务：

```bash
sudo tee /etc/systemd/system/abaqus-lmgrd.service << 'EOF'
[Unit]
Description=Abaqus FLEXnet License Server
After=network.target

[Service]
Type=forking
User=xfusion
ExecStart=/home/xfusion/Workspace/abaqus/SIMULIA/linux_a64/code/bin/lmgrd \
  -c /home/xfusion/Workspace/abaqus/SIMULIA/linux_a64/code/bin/ABAQUSLM__lmgrd__SSQ.lic
ExecStop=/home/xfusion/Workspace/abaqus/SIMULIA/linux_a64/code/bin/lmdown \
  -c /home/xfusion/Workspace/abaqus/SIMULIA/linux_a64/code/bin/ABAQUSLM__lmgrd__SSQ.lic -q
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable abaqus-lmgrd.service
sudo systemctl start abaqus-lmgrd.service
```

## 8. Fortran 环境（用户子程序编译需要）

如果需要编译用户子程序（UEL、UMAT、VUMAT 等），需要安装 Intel oneAPI HPC Toolkit。

下载 `intel-oneapi-base-toolkit-2025.0.1.46_offline.sh`（约 2.2G）：

```bash
chmod +x intel-oneapi-base-toolkit-2025.0.1.46_offline.sh
./intel-oneapi-base-toolkit-2025.0.1.46_offline.sh
```

安装后配置环境变量：

```bash
source /path/to/oneapi/setvars.sh
```

新版 oneAPI 使用 `ifx` 替代了 `ifort`，需创建软链：

```bash
ln -s ./ifx ifort
```

启动 Abaqus 前加载 oneAPI 环境：

```bash
source ./setvars.sh
cd /home/xfusion/Workspace/abaqus/SIMULIA_EstProduces/Commands
./abq2022 cae
```

## 附：踩坑记录

| 问题 | 原因 | 解决 |
|------|------|------|
| `./lmgrd: No such file or directory` | ELF 解释器路径错误 | `patchelf --set-interpreter /lib64/ld-linux-x86-64.so.2` |
| `libxcb-xinerama.so.0` 缺失 | 缺少 GUI 依赖 | `sudo apt install libxcb-xinerama0` |
| `libjpeg.so.62` 缺失 | 缺少 JPEG 库 | `sudo apt install libjpeg62` |
| `Failed to continue. Cannot install in same directory` | License Server 和主程序冲突 | 分开安装目录 |
| `/usr/tmp/.flexlm: No such file or directory` | 缺少临时目录 | `sudo mkdir -p /usr/tmp && sudo chmod 1777 /usr/tmp` |

## 文件结构

```
/home/xfusion/Workspace/abaqus/
├── Abaqus_2022/                          # 原始安装包（可删除）
│   ├── ABAQUSLM__lmgrd__SSQ.lic
│   └── DS.SIMULIA.Suite.2022.Linux64/
├── SIMULIA/                              # FLEXnet License Server
│   └── linux_a64/code/bin/
│       ├── lmgrd
│       ├── ABAQUSLM
│       └── ABAQUSLM__lmgrd__SSQ.lic
├── SIMULIA_EstProduces/                  # Abaqus 主程序
│   ├── Commands/abq2022
│   ├── linux_a64/code/bin/
│   └── linux_a64/SMA/site/custom_v6.env
└── Abaqus2022_安装记录.md
```

> 参考：[Manjaro Linux 安装 Abaqus 2022 踩坑记](https://www.nekopara.uk/archives/manjaro_install_abaqus.html)
