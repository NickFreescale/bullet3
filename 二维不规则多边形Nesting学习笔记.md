# 二维不规则多边形Nesting学习笔记

## 1. 问题概述

### 1.1 定义
二维不规则多边形嵌套（Nesting/Packing）问题是指在给定的平面区域内，将多个形状各异的不规则多边形高效地排列和放置，以最大化材料利用率或最小化废料的组合优化问题。

### 1.2 应用领域
- **纺织工业**：服装裁剪中的面料排样
- **金属加工**：钣金件的下料排样
- **造船工业**：船体零件的钢板排样
- **造纸工业**：纸张的切割优化
- **玻璃工业**：玻璃制品的切割排样

### 1.3 问题特点
- **NP难问题**：计算复杂度随多边形数量指数增长
- **多约束条件**：需要考虑形状、尺寸、旋转、镜像等多种约束
- **实时性要求**：工业应用中需要快速生成可行方案
- **多目标优化**：材料利用率、切割成本、生产效率等多重目标

## 2. 核心算法理论

### 2.1 No-Fit Polygon (NFP) 算法

NFP算法是多边形嵌套问题的核心算法之一，用于计算两个多边形之间的相对位置关系。

**基本概念：**
- **NFP定义**：给定两个多边形A和B，NFP是多边形B的参考点可以放置的所有位置的集合，使得A和B恰好相切但不重叠
- **数学表示**：NFP(A,B) = {p | A ∩ (B + p) = ∅, ∂A ∩ ∂(B + p) ≠ ∅}

**计算步骤：**
1. 选择多边形B的参考点（通常是重心或顶点）
2. 将B沿着A的边界滑动，记录参考点的轨迹
3. 处理凹多边形的特殊情况
4. 生成完整的NFP边界

### 2.2 Bottom-Left-Fill (BLF) 算法

BLF算法是一种贪心启发式算法，按照"左下优先"的原则放置多边形。

**算法流程：**
1. 对待排样的多边形按照某种规则排序（如面积、周长等）
2. 对于每个多边形：
   - 计算所有可能的放置位置
   - 选择最左下的可行位置
   - 更新已占用区域
3. 重复直到所有多边形都被放置

### 2.3 碰撞检测算法

**分离轴定理（SAT）：**
- 适用于凸多边形的快速碰撞检测
- 时间复杂度：O(n+m)，其中n、m为多边形顶点数

**光线投射算法：**
- 适用于复杂多边形的点在多边形内判断
- 从点发射水平射线，统计与多边形边的交点数

## 3. 现代求解方法

### 3.1 传统元启发式算法

#### 3.1.1 遗传算法（GA）
```
基本流程：
1. 初始化种群（随机生成多边形排列序列）
2. 评估适应度（材料利用率）
3. 选择操作（轮盘赌、锦标赛选择等）
4. 交叉操作（部分映射交叉、顺序交叉等）
5. 变异操作（交换、插入、逆转等）
6. 迭代直到收敛
```

**优点：**
- 全局搜索能力强
- 适用于多目标优化
- 易于并行化

**缺点：**
- 收敛速度慢
- 参数调节复杂
- 容易早熟收敛

#### 3.1.2 模拟退火算法（SA）
```
基本流程：
1. 初始化当前解和温度
2. 生成邻域解
3. 计算目标函数差值
4. 根据Metropolis准则接受或拒绝新解
5. 降低温度
6. 重复直到温度足够低
```

### 3.2 深度强化学习方法

#### 3.2.1 问题建模
- **状态空间**：当前板材状态、待放置多边形序列
- **动作空间**：多边形的位置、旋转角度
- **奖励函数**：材料利用率、放置成功率等

#### 3.2.2 网络架构
```
输入层：多边形特征向量（形状描述符）
隐藏层：全连接层 + LSTM/GRU（处理序列信息）
输出层：位置预测 + 角度预测（多任务学习）
```

#### 3.2.3 特征提取
- **质心到轮廓距离**：以固定角度间隔采样
- **傅里叶描述符**：频域特征表示
- **几何不变量**：面积、周长、凸包面积等

## 4. 关键技术细节

### 4.1 多边形表示方法

#### 4.1.1 顶点表示
```python
# 多边形顶点坐标列表（逆时针顺序）
polygon = [(x1, y1), (x2, y2), ..., (xn, yn)]
```

#### 4.1.2 边表示
```python
# 多边形边的集合
edges = [((x1, y1), (x2, y2)), ((x2, y2), (x3, y3)), ...]
```

### 4.2 几何运算

#### 4.2.1 多边形旋转
```python
def rotate_polygon(polygon, angle, center):
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    cx, cy = center
    rotated = []
    for x, y in polygon:
        x_new = cos_a * (x - cx) - sin_a * (y - cy) + cx
        y_new = sin_a * (x - cx) + cos_a * (y - cy) + cy
        rotated.append((x_new, y_new))
    return rotated
```

#### 4.2.2 多边形平移
```python
def translate_polygon(polygon, dx, dy):
    return [(x + dx, y + dy) for x, y in polygon]
```

### 4.3 碰撞检测实现

#### 4.3.1 点在多边形内判断
```python
def point_in_polygon(point, polygon):
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside
```

#### 4.3.2 多边形相交检测
```python
def polygons_intersect(poly1, poly2):
    # 使用分离轴定理（SAT）
    def get_axes(polygon):
        axes = []
        for i in range(len(polygon)):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % len(polygon)]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            normal = (-edge[1], edge[0])  # 垂直向量
            axes.append(normal)
        return axes
    
    def project_polygon(polygon, axis):
        dots = [vertex[0] * axis[0] + vertex[1] * axis[1] for vertex in polygon]
        return min(dots), max(dots)
    
    axes = get_axes(poly1) + get_axes(poly2)
    
    for axis in axes:
        proj1 = project_polygon(poly1, axis)
        proj2 = project_polygon(poly2, axis)
        
        if proj1[1] < proj2[0] or proj2[1] < proj1[0]:
            return False  # 分离轴存在，多边形不相交
    
    return True  # 所有轴上都有重叠，多边形相交
```

## 5. 高级优化策略

### 5.1 多层次优化

#### 5.1.1 全局优化层
- 多边形排序策略优化
- 板材利用率全局评估
- 多板材分配策略

#### 5.1.2 局部优化层
- 单个多边形的最佳位置搜索
- 局部调整和微调
- 空隙填充优化

### 5.2 自适应策略

#### 5.2.1 动态排序
根据当前板材状态动态调整多边形的放置顺序：
- 大多边形优先策略
- 形状匹配优先策略
- 空隙填充优先策略

#### 5.2.2 多角度尝试
```python
def find_best_rotation(polygon, container, placed_polygons):
    best_position = None
    best_utilization = 0
    
    # 尝试不同角度（如每15度一个角度）
    for angle in range(0, 360, 15):
        rotated_poly = rotate_polygon(polygon, math.radians(angle), get_centroid(polygon))
        position = find_best_position(rotated_poly, container, placed_polygons)
        
        if position:
            utilization = calculate_utilization(container, placed_polygons + [rotated_poly])
            if utilization > best_utilization:
                best_utilization = utilization
                best_position = (position, angle)
    
    return best_position
```

## 6. 深度强化学习实现

### 6.1 环境设计

#### 6.1.1 状态表示
```python
class NestingEnvironment:
    def __init__(self, container_size, polygons):
        self.container = container_size
        self.polygons = polygons
        self.placed_polygons = []
        self.current_polygon_idx = 0
    
    def get_state(self):
        # 容器状态 + 当前多边形特征 + 剩余多边形信息
        container_state = self.encode_container_state()
        current_poly_features = self.extract_polygon_features(
            self.polygons[self.current_polygon_idx]
        )
        remaining_info = self.encode_remaining_polygons()
        
        return np.concatenate([container_state, current_poly_features, remaining_info])
```

#### 6.1.2 动作空间
```python
def get_action_space(self):
    # 离散化的位置和角度空间
    position_actions = self.discretize_positions()  # 网格化位置
    rotation_actions = list(range(0, 360, 15))      # 15度间隔旋转
    
    return {
        'position': position_actions,
        'rotation': rotation_actions
    }
```

### 6.2 奖励函数设计

```python
def calculate_reward(self, action, success):
    if not success:
        return -1.0  # 放置失败的惩罚
    
    # 基础奖励：材料利用率
    utilization = self.calculate_utilization()
    base_reward = utilization
    
    # 紧密度奖励：鼓励紧密排列
    compactness = self.calculate_compactness()
    compactness_reward = 0.2 * compactness
    
    # 边界奖励：鼓励靠近边界放置
    boundary_reward = 0.1 * self.calculate_boundary_proximity()
    
    # 完成奖励：成功放置所有多边形
    completion_bonus = 1.0 if self.is_complete() else 0.0
    
    return base_reward + compactness_reward + boundary_reward + completion_bonus
```

### 6.3 网络架构

```python
import torch
import torch.nn as nn

class NestingNet(nn.Module):
    def __init__(self, state_dim, hidden_dim=256):
        super(NestingNet, self).__init__()
        
        # 特征提取层
        self.feature_extractor = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # LSTM层处理序列信息
        self.lstm = nn.LSTM(hidden_dim, hidden_dim, batch_first=True)
        
        # 多任务输出层
        self.position_head = nn.Linear(hidden_dim, 100)  # 位置预测
        self.rotation_head = nn.Linear(hidden_dim, 24)   # 角度预测（15度间隔）
        
    def forward(self, state):
        features = self.feature_extractor(state)
        lstm_out, _ = self.lstm(features.unsqueeze(1))
        lstm_features = lstm_out.squeeze(1)
        
        position_logits = self.position_head(lstm_features)
        rotation_logits = self.rotation_head(lstm_features)
        
        return position_logits, rotation_logits
```

## 7. 实用算法实现

### 7.1 基础几何工具

```python
import math
import numpy as np
from typing import List, Tuple, Optional

class GeometryUtils:
    @staticmethod
    def polygon_area(vertices: List[Tuple[float, float]]) -> float:
        """计算多边形面积（使用鞋带公式）"""
        n = len(vertices)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i][0] * vertices[j][1]
            area -= vertices[j][0] * vertices[i][1]
        return abs(area) / 2.0
    
    @staticmethod
    def polygon_centroid(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
        """计算多边形重心"""
        area = GeometryUtils.polygon_area(vertices)
        cx = cy = 0.0
        n = len(vertices)
        
        for i in range(n):
            j = (i + 1) % n
            cross = vertices[i][0] * vertices[j][1] - vertices[j][0] * vertices[i][1]
            cx += (vertices[i][0] + vertices[j][0]) * cross
            cy += (vertices[i][1] + vertices[j][1]) * cross
        
        factor = 1.0 / (6.0 * area)
        return (cx * factor, cy * factor)
    
    @staticmethod
    def polygon_bounding_box(vertices: List[Tuple[float, float]]) -> Tuple[float, float, float, float]:
        """计算多边形边界框"""
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        return (min(xs), min(ys), max(xs), max(ys))
```

### 7.2 NFP计算实现

```python
class NFPCalculator:
    def __init__(self):
        self.tolerance = 1e-10
    
    def calculate_nfp(self, stationary_poly: List[Tuple[float, float]], 
                     moving_poly: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """计算两个多边形的NFP"""
        nfp_points = []
        
        # 处理每条边
        for i in range(len(stationary_poly)):
            # 获取静止多边形的当前边
            start_point = stationary_poly[i]
            end_point = stationary_poly[(i + 1) % len(stationary_poly)]
            
            # 计算移动多边形沿此边滑动的轨迹
            edge_nfp = self._slide_along_edge(moving_poly, start_point, end_point)
            nfp_points.extend(edge_nfp)
        
        # 去重并排序
        nfp_points = self._remove_duplicates(nfp_points)
        nfp_points = self._sort_points(nfp_points)
        
        return nfp_points
    
    def _slide_along_edge(self, moving_poly, edge_start, edge_end):
        """计算多边形沿边滑动的NFP部分"""
        # 实现细节：计算移动多边形各顶点与静止边的接触轨迹
        trajectories = []
        
        for vertex in moving_poly:
            # 计算顶点沿边滑动的轨迹
            trajectory = self._vertex_trajectory(vertex, edge_start, edge_end, moving_poly)
            trajectories.extend(trajectory)
        
        return trajectories
```

### 7.3 BLF算法实现

```python
class BLFPacker:
    def __init__(self, container_width: float, container_height: float):
        self.container_width = container_width
        self.container_height = container_height
        self.placed_polygons = []
    
    def pack_polygons(self, polygons: List[List[Tuple[float, float]]]) -> List[dict]:
        """使用BLF算法排列多边形"""
        results = []
        
        # 按面积降序排序
        sorted_polygons = sorted(polygons, 
                               key=lambda p: GeometryUtils.polygon_area(p), 
                               reverse=True)
        
        for polygon in sorted_polygons:
            best_position = self._find_best_position(polygon)
            
            if best_position:
                placed_polygon = {
                    'polygon': polygon,
                    'position': best_position['position'],
                    'rotation': best_position['rotation']
                }
                results.append(placed_polygon)
                self.placed_polygons.append(placed_polygon)
        
        return results
    
    def _find_best_position(self, polygon: List[Tuple[float, float]]) -> Optional[dict]:
        """寻找多边形的最佳放置位置"""
        best_position = None
        best_score = float('inf')
        
        # 尝试不同旋转角度
        for angle in range(0, 360, 15):
            rotated_poly = self._rotate_polygon(polygon, angle)
            
            # 寻找左下角最优位置
            position = self._find_leftmost_bottom_position(rotated_poly)
            
            if position and self._is_valid_placement(rotated_poly, position):
                score = position[0] + position[1]  # 左下优先评分
                if score < best_score:
                    best_score = score
                    best_position = {
                        'position': position,
                        'rotation': angle
                    }
        
        return best_position
```

## 8. 性能优化技巧

### 8.1 空间数据结构

#### 8.1.1 R-tree索引
```python
from rtree import index

class SpatialIndex:
    def __init__(self):
        self.idx = index.Index()
        self.polygon_id = 0
    
    def insert_polygon(self, polygon, polygon_data):
        bbox = GeometryUtils.polygon_bounding_box(polygon)
        self.idx.insert(self.polygon_id, bbox, obj=polygon_data)
        self.polygon_id += 1
    
    def query_intersections(self, polygon):
        bbox = GeometryUtils.polygon_bounding_box(polygon)
        return list(self.idx.intersection(bbox, objects=True))
```

#### 8.1.2 网格化加速
```python
class GridAccelerator:
    def __init__(self, width, height, grid_size=50):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.grid_cols = int(width / grid_size) + 1
        self.grid_rows = int(height / grid_size) + 1
        self.grid = [[[] for _ in range(self.grid_cols)] for _ in range(self.grid_rows)]
    
    def add_polygon(self, polygon, polygon_id):
        bbox = GeometryUtils.polygon_bounding_box(polygon)
        start_col = max(0, int(bbox[0] / self.grid_size))
        end_col = min(self.grid_cols - 1, int(bbox[2] / self.grid_size))
        start_row = max(0, int(bbox[1] / self.grid_size))
        end_row = min(self.grid_rows - 1, int(bbox[3] / self.grid_size))
        
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                self.grid[row][col].append(polygon_id)
```

### 8.2 并行计算

```python
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

class ParallelNesting:
    def __init__(self, num_processes=None):
        self.num_processes = num_processes or mp.cpu_count()
    
    def parallel_nfp_calculation(self, polygon_pairs):
        """并行计算多个多边形对的NFP"""
        with ProcessPoolExecutor(max_workers=self.num_processes) as executor:
            futures = [executor.submit(self._calculate_single_nfp, pair) 
                      for pair in polygon_pairs]
            results = [future.result() for future in futures]
        return results
    
    def _calculate_single_nfp(self, polygon_pair):
        """单个NFP计算任务"""
        poly1, poly2 = polygon_pair
        calculator = NFPCalculator()
        return calculator.calculate_nfp(poly1, poly2)
```

## 9. 评估指标

### 9.1 材料利用率
```python
def material_utilization(placed_polygons, container_area):
    total_polygon_area = sum(GeometryUtils.polygon_area(p['polygon']) 
                           for p in placed_polygons)
    return total_polygon_area / container_area
```

### 9.2 紧密度指标
```python
def compactness_metric(placed_polygons, container):
    # 计算凸包面积与实际占用面积的比值
    all_points = []
    for poly_data in placed_polygons:
        polygon = poly_data['polygon']
        position = poly_data['position']
        translated_poly = [(x + position[0], y + position[1]) for x, y in polygon]
        all_points.extend(translated_poly)
    
    convex_hull = self._compute_convex_hull(all_points)
    convex_area = GeometryUtils.polygon_area(convex_hull)
    actual_area = sum(GeometryUtils.polygon_area(p['polygon']) for p in placed_polygons)
    
    return actual_area / convex_area if convex_area > 0 else 0
```

## 10. 实际应用案例

### 10.1 服装裁剪优化
```python
class ClothingNesting:
    def __init__(self, fabric_width, fabric_length):
        self.fabric_width = fabric_width
        self.fabric_length = fabric_length
        self.pattern_pieces = []
    
    def add_pattern_piece(self, vertices, quantity=1, can_rotate=True, can_mirror=False):
        """添加服装纸样"""
        for _ in range(quantity):
            self.pattern_pieces.append({
                'vertices': vertices,
                'can_rotate': can_rotate,
                'can_mirror': can_mirror,
                'placed': False
            })
    
    def optimize_layout(self):
        """优化排样布局"""
        packer = BLFPacker(self.fabric_width, self.fabric_length)
        
        # 考虑纺织品的纤维方向约束
        constrained_polygons = []
        for piece in self.pattern_pieces:
            if piece['can_rotate']:
                # 只允许0度和90度旋转（考虑纤维方向）
                angles = [0, 90]
            else:
                angles = [0]
            
            for angle in angles:
                rotated = self._rotate_pattern(piece['vertices'], angle)
                constrained_polygons.append({
                    'polygon': rotated,
                    'original_piece': piece,
                    'rotation': angle
                })
        
        return packer.pack_polygons([p['polygon'] for p in constrained_polygons])
```

### 10.2 钣金下料优化
```python
class SheetMetalNesting:
    def __init__(self, sheet_dimensions):
        self.sheet_width, self.sheet_height = sheet_dimensions
        self.kerf_width = 2.0  # 切割缝隙宽度
        self.min_distance = 5.0  # 最小间距
    
    def add_cutting_constraints(self, polygon):
        """添加切割约束（考虑切割缝隙）"""
        # 将多边形向外扩展，考虑切割缝隙
        expanded_polygon = self._expand_polygon(polygon, self.kerf_width / 2)
        return expanded_polygon
    
    def optimize_cutting_path(self, placed_polygons):
        """优化切割路径"""
        # 使用最近邻算法优化切割顺序
        cutting_order = self._nearest_neighbor_tsp(placed_polygons)
        return cutting_order
```

## 11. 开源工具和库

### 11.1 Libnest2D
- **语言**：C++
- **特点**：高性能、可定制、基于Boost.Geometry
- **适用场景**：工业级应用

### 11.2 SVGNest
- **语言**：JavaScript
- **特点**：Web友好、可视化好、易于集成
- **适用场景**：原型开发、在线工具

### 11.3 Python实现
```python
# 推荐的Python库
import shapely  # 几何计算
import matplotlib.pyplot as plt  # 可视化
import numpy as np  # 数值计算
from scipy.spatial import ConvexHull  # 凸包计算
```

## 12. 性能优化建议

### 12.1 算法层面
1. **预计算NFP**：对常用多边形对预计算NFP，建立缓存
2. **分层优化**：先粗排再精排，多层次优化
3. **启发式剪枝**：使用几何启发式规则提前排除不可行解

### 12.2 工程层面
1. **内存管理**：使用对象池避免频繁内存分配
2. **并行计算**：充分利用多核CPU进行并行NFP计算
3. **GPU加速**：对于大规模问题，考虑GPU并行计算

### 12.3 数据结构优化
```python
class OptimizedPolygon:
    def __init__(self, vertices):
        self.vertices = vertices
        self.area = GeometryUtils.polygon_area(vertices)
        self.centroid = GeometryUtils.polygon_centroid(vertices)
        self.bbox = GeometryUtils.polygon_bounding_box(vertices)
        self.convex_hull = self._compute_convex_hull()
        
        # 预计算常用几何属性
        self.perimeter = self._calculate_perimeter()
        self.moment_of_inertia = self._calculate_moment_of_inertia()
```

## 13. 未来发展方向

### 13.1 技术趋势
1. **深度学习融合**：结合CNN处理形状特征，RNN处理序列决策
2. **强化学习进阶**：多智能体强化学习、分层强化学习
3. **量子计算**：利用量子算法解决组合优化问题

### 13.2 应用扩展
1. **3D嵌套**：扩展到三维空间的装箱问题
2. **动态嵌套**：处理实时变化的需求和约束
3. **多材料优化**：考虑不同材料特性的综合优化

### 13.3 工业4.0集成
1. **IoT集成**：与生产设备实时通信
2. **数字孪生**：建立虚拟仿真环境
3. **自适应优化**：根据生产反馈自动调整策略

## 14. 学习资源推荐

### 14.1 经典论文
1. Bennell, J. A., & Oliveira, J. F. (2008). The geometry of nesting problems
2. Burke, E. K., et al. (2013). A new bottom-left-fill heuristic algorithm
3. Gomes, A. M., & Oliveira, J. F. (2006). Solving irregular strip packing problems

### 14.2 开源项目
1. **SVGNest**：https://github.com/Jack000/SVGnest
2. **Libnest2D**：https://github.com/tamasmeszaros/libnest2d
3. **nest2D**：https://github.com/markfink/nest2D

### 14.3 在线工具
1. **Deepnest**：开源的嵌套软件
2. **True Shape Nesting**：商业嵌套解决方案

---

## 总结

二维不规则多边形nesting是一个集计算几何、组合优化、人工智能于一体的复杂问题。从传统的启发式算法到现代的深度强化学习方法，该领域正在快速发展。掌握核心算法（如NFP、BLF）的同时，结合现代AI技术，可以在实际应用中取得显著的效果提升。

在实际应用中，需要根据具体场景选择合适的算法和优化策略，平衡计算效率和求解质量，以达到最佳的工程效果。