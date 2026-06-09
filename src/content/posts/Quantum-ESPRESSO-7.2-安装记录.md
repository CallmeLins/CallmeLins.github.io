---
title: Quantum ESPRESSO 7.2 安装记录
date: 2026-05-08
updated: 2026-06-08
categories: 运维
tags: [Ubuntu, HPC, MPI]
---

> 安装日期: 2026-05-08
> 系统环境: Ubuntu 22.04 LTS (Jammy)
> QE 版本: 7.2 (q-e-qe-7.2)

## 前提条件

系统中已预装以下环境:

- **编译器**: gcc, gfortran 11.4.0
- **MPI**: OpenMPI 4.1.2 (libopenmpi-dev, openmpi-bin)
- **BLAS/LAPACK**: OpenBLAS (libblas-dev, liblapack-dev)
- **FFTW**: 运行时库已安装 (无 dev 头文件, QE 使用内置 FFTW)

## 构建步骤

### 1. 解压源码

```bash
cd /home/xfusion/Workspace/quantum_espresso
tar xzf q-e-qe-7.2.tar.gz
```

### 2. 配置

```bash
cd q-e-qe-7.2
./configure
```

配置结果:
- BLAS: libopenblas ✓
- LAPACK: libopenblas ✓
- FFT: 内置 FFTW（未找到系统 FFTW 头文件）
- MPI: 已检测, 并行可执行程序 ✓

### 3. 解决 libmbd 依赖问题

`make pwall` 过程中, `libmbd`（多体色散库）从 GitHub 克隆失败（网络无法访问 github.com）。

**解决方案**: 使用 `-D__NOMBD` 预处理宏跳过 MBD 支持。

修改 `make.inc`:
```bash
# 修改前
DFLAGS = -D__FFTW -D__MPI

# 修改后
DFLAGS = -D__FFTW -D__MPI -D__NOMBD
```

修改 `Makefile`（移除 `libmbd` 依赖）:
```bash
# 修改前
mods : $(FOX) libutil libla libfft libupf libmbd librxc

# 修改后
mods : $(FOX) libutil libla libfft libupf librxc
```

同时从 `make.inc` 中移除了 `BASEMOD_FLAGS` 和 `BASEMODS` 中对 MBD 目录和库的引用:
- 删除 `$(MOD_FLAG)$(TOPDIR)/MBD \`
- 删除 `$(TOPDIR)/MBD/libmbd.a`

> **说明**: MBD 为可选的色散修正功能, 禁用不影响 QE 核心功能。恢复方法:
> ```bash
> make libmbd    # 在有 GitHub 访问的网络下运行
> make pwall     # 重新编译完整版本
> ```

### 4. 编译

```bash
# 核心模块 (PWscf, NEB, Phonon, PostProcessing, PWcond, ACFDT)
make pwall

# 其他常用模块
make cp     # Car-Parrinello 分子动力学
make ld1    # 赝势生成
make hp     # Hubbard U 计算
```

编译耗时约 15-20 分钟（视 CPU 核心数而定）。

## 验证

```bash
$ pw.x --version
Program PWSCF v.7.2 starts on  8May2026 at 12: 7:46
```

## 已编译的可执行程序（62 个）

| 类别 | 可执行程序 | 说明 |
|------|-----------|------|
| 核心 | `pw.x`, `cp.x`, `neb.x` | 自洽场、分子动力学、NEB |
| 声子 | `ph.x`, `phcg.x` | 声子谱计算 |
| 后处理 | `pp.x`, `dos.x`, `bands.x`, `projwfc.x`, `pw2wannier90.x` | 态密度、能带、投影、Wannier |
| 光谱 | `xspectra.x` (需额外编译) | X 射线光谱 |
| 赝势 | `ld1.x`, `upfconv.x` | 赝势生成与转换 |
| 工具 | `kpoints.x`, `ev.x`, `pwi2xsf.x` | k 点生成、晶格参数、格式转换 |

## 使用方法

```bash
# 方式一: 激活脚本（推荐）
source /home/xfusion/Workspace/quantum_espresso/activate.sh

# 方式二: 手动添加 PATH
export PATH="/home/xfusion/Workspace/quantum_espresso/q-e-qe-7.2/bin:$PATH"

# 方式三: 直接使用绝对路径
/home/xfusion/Workspace/quantum_espresso/q-e-qe-7.2/bin/pw.x < input.in > output.out
```

## 运行示例

```bash
source ~/Workspace/quantum_espresso/activate.sh

# 串行运行
mpirun -np 1 pw.x < input.in > output.out

# 并行运行
mpirun -np 4 pw.x < input.in > output.out
```

## 多节点 MPI 并行配置

当前集群由两台节点构成, 通过 NFS + OpenMPI 实现跨节点并行计算。

### 集群节点信息

| 节点 | IP 地址 | CPU 核心数 | 角色 |
|------|---------|-----------|------|
| node1 | 10.0.0.1 | 152 | QE 安装 + NFS 服务端 |
| node2 | 10.0.0.2 | 152 | NFS 客户端 |

### 前置条件: SSH 免密登录

OpenMPI 依赖 SSH 在远程节点启动进程:

```bash
# 在 node1 生成密钥（如无）
ssh-keygen -t rsa -b 4096

# 将公钥复制到 node2（需输入 node2 用户密码）
ssh-copy-id 10.0.0.2

# 验证免密登录
ssh 10.0.0.2 "hostname"
```

### NFS 共享 QE 目录

QE 只需在一台机器编译, 通过 NFS 共享给其他节点。

#### 服务端配置（node1）

```bash
# 安装 NFS 服务端
sudo apt install -y nfs-kernel-server

# 配置共享目录
echo "/home/xfusion/Workspace/quantum_espresso/q-e-qe-7.2 10.0.0.0/24(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports

# 重启服务
sudo exportfs -a && sudo systemctl restart nfs-kernel-server
```

#### 客户端配置（node2）

```bash
# 安装 NFS 客户端
sudo apt install -y nfs-common

# 创建挂载点
sudo mkdir -p /home/xfusion/Workspace/quantum_espresso/q-e-qe-7.2

# 挂载 NFS 共享
sudo mount -t nfs 10.0.0.1:/home/xfusion/Workspace/quantum_espresso/q-e-qe-7.2 /home/xfusion/Workspace/quantum_espresso/q-e-qe-7.2

# 配置开机自动挂载
echo "10.0.0.1:/home/xfusion/Workspace/quantum_espresso/q-e-qe-7.2 /home/xfusion/Workspace/quantum_espresso/q-e-qe-7.2 nfs defaults,_netdev 0 0" | sudo tee -a /etc/fstab
```

#### 客户端安装 OpenMPI（node2）

```bash
sudo apt install -y openmpi-bin
```

> **注意**: 所有节点需安装相同版本的 OpenMPI, 否则可能导致运行时错误。

### 多节点运行

```bash
# 方式一: 指定 host 和核心数
mpirun --host 10.0.0.1:152,10.0.0.2:152 -np 16 pw.x -i input.in

# 方式二: 使用 hostfile（主机名冲突时优先使用 IP）
echo -e "10.0.0.1 slots=152\n10.0.0.2 slots=152" > hostfile
mpirun --hostfile hostfile -np 16 pw.x -i input.in
```

建议设置别名简化命令:
```bash
alias mpirun-qe='mpirun --host 10.0.0.1:152,10.0.0.2:152'
mpirun-qe -np 16 pw.x -i input.in
```

### 验证跨节点并行

运行以下测试确认跨节点 MPI 通信正常:

```bash
# 测试 MPI 跨节点通信
mpirun --host 10.0.0.1,10.0.0.2 -np 2 hostname -I
# 应输出:
# 10.0.0.1
# 10.0.0.2

# 测试 QE 双节点计算（先准备好赝势文件）
mpirun --host 10.0.0.1:152,10.0.0.2:152 -np 4 pw.x -i test.in
# 输出结尾应有 "JOB DONE."
```

### 说明

- **单机运行**: 仍可使用 `mpirun -np N pw.x -i input.in`, 不受影响。
- **网络协议**: 当前基于 TCP 通信（无 InfiniBand）, 跨节点延迟较高, 计算密集场景下使用效率较好。
- **扩展性**: 添加新节点时, 重复客户端配置步骤即可。

## 已知问题

1. **MBD 未编译**: 无 GitHub 访问导致 `libmbd` 未编译, 已使用 `-D__NOMBD` 跳过。有网络时可通过 `make libmbd` 补装。
2. **FFTW 系统库未使用**: 系统未安装 `libfftw3-dev`, 使用 QE 内置 FFTW（不影响功能）。
3. **Scalapack 未使用**: 未安装 `libscalapack-openmpi-dev`, 大体系计算推荐安装后重新编译。
