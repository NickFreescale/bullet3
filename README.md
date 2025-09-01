# 二维不规则多边形Nesting学习资源

本仓库包含了关于二维不规则多边形嵌套（Nesting/Packing）问题的完整学习资源，包括理论知识、算法实现和工业应用案例。

## 📚 文件说明

### 核心学习资料
- **`二维不规则多边形Nesting学习笔记.md`** - 完整的理论学习笔记
  - 问题定义和应用领域
  - 核心算法理论（NFP、BLF等）
  - 现代求解方法（遗传算法、强化学习等）
  - 性能优化技巧
  - 学习资源推荐

### 代码实现
- **`nesting_example.py`** - 基础算法实现
  - 几何工具类
  - NFP计算器（简化版）
  - BLF算法实现
  - 碰撞检测
  - 结果可视化

- **`advanced_nesting_algorithms.py`** - 高级算法实现
  - 遗传算法
  - 模拟退火算法
  - 深度强化学习框架
  - 算法性能对比
  - 收敛分析

- **`industrial_applications.py`** - 工业应用案例
  - 纺织行业应用
  - 金属加工应用
  - 皮革制品应用
  - 成本优化分析
  - 行业对比

## 🚀 快速开始

### 环境要求
```bash
pip install numpy matplotlib scipy
```

### 运行基础演示
```bash
python nesting_example.py
```

### 运行高级算法演示
```bash
python advanced_nesting_algorithms.py
```

### 运行工业应用演示
```bash
python industrial_applications.py
```

## 📊 生成的可视化文件

运行代码后会生成以下图片文件：

- `nfp_demo.png` - NFP算法演示
- `blf_packing_result.png` - BLF算法结果
- `algorithm_comparison.png` - 算法性能对比
- `convergence_analysis.png` - 算法收敛分析
- `scalability_analysis.png` - 可扩展性分析
- `industry_comparison.png` - 行业应用对比
- `performance_report.md` - 详细性能报告

## 🎯 学习路径建议

### 初学者
1. 阅读 `二维不规则多边形Nesting学习笔记.md` 了解基本概念
2. 运行 `nesting_example.py` 理解核心算法
3. 学习NFP和BLF算法的实现细节

### 进阶学习
1. 研究 `advanced_nesting_algorithms.py` 中的元启发式算法
2. 了解深度强化学习在nesting问题中的应用
3. 分析算法收敛性和可扩展性

### 实际应用
1. 学习 `industrial_applications.py` 中的行业案例
2. 了解不同行业的约束条件和优化目标
3. 掌握成本分析和性能评估方法

## 🔧 核心算法概览

### NFP (No-Fit Polygon)
- 计算两个多边形的相对位置关系
- 确定可行的放置区域
- 是多边形嵌套的基础算法

### BLF (Bottom-Left-Fill)
- 贪心策略，优先放置在左下角
- 简单高效，适合实时应用
- 常作为其他算法的基础

### 遗传算法
- 全局优化能力强
- 适合多目标优化
- 参数调节需要经验

### 模拟退火
- 能跳出局部最优
- 收敛性能稳定
- 适合中等规模问题

### 深度强化学习
- 自适应学习能力
- 处理复杂约束
- 需要大量训练数据

## 🏭 工业应用特点

### 纺织行业
- **主要约束**: 纹理方向、尺码配比
- **优化目标**: 材料利用率最大化
- **典型利用率**: 85%+

### 金属加工
- **主要约束**: 切割缝隙、热变形
- **优化目标**: 总成本最小化
- **典型利用率**: 75%+

### 皮革制品
- **主要约束**: 质量分区、瑕疵避免
- **优化目标**: 质量匹配度
- **典型利用率**: 70%+

## 📈 性能指标

### 算法性能
- **计算时间**: BLF < SA < GA < DRL
- **解质量**: DRL > GA > SA > BLF
- **稳定性**: BLF > SA > GA > DRL

### 工业指标
- **材料利用率**: 已用面积 / 总面积
- **放置成功率**: 成功放置数量 / 总数量
- **成本效率**: 单位产品成本
- **质量匹配度**: 质量要求满足程度

## 🔗 相关资源

### 开源项目
- [SVGNest](https://github.com/Jack000/SVGnest) - JavaScript实现
- [Libnest2D](https://github.com/tamasmeszaros/libnest2d) - C++实现
- [Deepnest](https://deepnest.io/) - 开源嵌套软件

### 学术论文
- Bennell, J. A., & Oliveira, J. F. (2008). The geometry of nesting problems
- Burke, E. K., et al. (2013). A new bottom-left-fill heuristic algorithm
- 曾焕荣, 商慧亮 (2022). 基于深度强化学习的二维不规则多边形排样方法

## 🤝 贡献

欢迎提交问题和改进建议！

## 📄 许可证

本项目仅供学习研究使用。

---

*最后更新: 2024年12月*