---
title: Quantum ESPRESSO 7.2 安装记录
date: 2026-05-08
categories: 运维
tags: [Ubuntu, HPC]
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

## 已知问题

1. **MBD 未编译**: 无 GitHub 访问导致 `libmbd` 未编译, 已使用 `-D__NOMBD` 跳过。有网络时可通过 `make libmbd` 补装。
2. **FFTW 系统库未使用**: 系统未安装 `libfftw3-dev`, 使用 QE 内置 FFTW（不影响功能）。
3. **Scalapack 未使用**: 未安装 `libscalapack-openmpi-dev`, 大体系计算推荐安装后重新编译。
