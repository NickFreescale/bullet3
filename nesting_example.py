#!/usr/bin/env python3
"""
二维不规则多边形Nesting算法示例实现
演示NFP计算、BLF算法和基础几何运算
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class PlacedPolygon:
    """已放置的多边形数据结构"""
    vertices: List[Tuple[float, float]]
    position: Tuple[float, float]
    rotation: float
    original_id: int

class GeometryUtils:
    """几何工具类"""
    
    @staticmethod
    def polygon_area(vertices: List[Tuple[float, float]]) -> float:
        """使用鞋带公式计算多边形面积"""
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
        if area == 0:
            return (0, 0)
        
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
        """计算多边形边界框 (min_x, min_y, max_x, max_y)"""
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        return (min(xs), min(ys), max(xs), max(ys))
    
    @staticmethod
    def rotate_polygon(vertices: List[Tuple[float, float]], angle: float, 
                      center: Tuple[float, float] = None) -> List[Tuple[float, float]]:
        """旋转多边形"""
        if center is None:
            center = GeometryUtils.polygon_centroid(vertices)
        
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        cx, cy = center
        
        rotated = []
        for x, y in vertices:
            x_new = cos_a * (x - cx) - sin_a * (y - cy) + cx
            y_new = sin_a * (x - cx) + cos_a * (y - cy) + cy
            rotated.append((x_new, y_new))
        
        return rotated
    
    @staticmethod
    def translate_polygon(vertices: List[Tuple[float, float]], 
                         dx: float, dy: float) -> List[Tuple[float, float]]:
        """平移多边形"""
        return [(x + dx, y + dy) for x, y in vertices]
    
    @staticmethod
    def point_in_polygon(point: Tuple[float, float], 
                        polygon: List[Tuple[float, float]]) -> bool:
        """判断点是否在多边形内（射线法）"""
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

class CollisionDetector:
    """碰撞检测类"""
    
    @staticmethod
    def polygons_intersect(poly1: List[Tuple[float, float]], 
                          poly2: List[Tuple[float, float]]) -> bool:
        """使用分离轴定理检测两个多边形是否相交"""
        
        def get_axes(polygon):
            """获取多边形的所有法向量（分离轴）"""
            axes = []
            for i in range(len(polygon)):
                p1 = polygon[i]
                p2 = polygon[(i + 1) % len(polygon)]
                edge = (p2[0] - p1[0], p2[1] - p1[1])
                # 计算边的法向量
                normal = (-edge[1], edge[0])
                # 归一化
                length = math.sqrt(normal[0]**2 + normal[1]**2)
                if length > 0:
                    axes.append((normal[0]/length, normal[1]/length))
            return axes
        
        def project_polygon(polygon, axis):
            """将多边形投影到轴上"""
            dots = [vertex[0] * axis[0] + vertex[1] * axis[1] for vertex in polygon]
            return min(dots), max(dots)
        
        # 获取所有分离轴
        axes = get_axes(poly1) + get_axes(poly2)
        
        # 检查每个轴上的投影是否分离
        for axis in axes:
            proj1 = project_polygon(poly1, axis)
            proj2 = project_polygon(poly2, axis)
            
            # 如果在某个轴上投影分离，则多边形不相交
            if proj1[1] < proj2[0] or proj2[1] < proj1[0]:
                return False
        
        return True  # 所有轴上都有重叠，多边形相交

class NFPCalculator:
    """No-Fit Polygon计算器"""
    
    def __init__(self, tolerance: float = 1e-10):
        self.tolerance = tolerance
    
    def calculate_nfp_simplified(self, stationary_poly: List[Tuple[float, float]], 
                                moving_poly: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """简化的NFP计算（仅用于演示）"""
        # 这是一个简化版本，实际NFP计算非常复杂
        # 实际应用中建议使用专业几何库如Clipper或Boost.Geometry
        
        nfp_points = []
        
        # 获取静止多边形的边界框
        bbox = GeometryUtils.polygon_bounding_box(stationary_poly)
        moving_bbox = GeometryUtils.polygon_bounding_box(moving_poly)
        
        # 简化计算：基于边界框的NFP近似
        # 实际NFP需要考虑多边形的精确形状
        offset_x = moving_bbox[0] - moving_bbox[2]  # 负的宽度
        offset_y = moving_bbox[1] - moving_bbox[3]  # 负的高度
        
        # 构造简化的NFP（矩形近似）
        nfp_points = [
            (bbox[0] + offset_x, bbox[1] + offset_y),  # 左下
            (bbox[2] - offset_x, bbox[1] + offset_y),  # 右下
            (bbox[2] - offset_x, bbox[3] - offset_y),  # 右上
            (bbox[0] + offset_x, bbox[3] - offset_y)   # 左上
        ]
        
        return nfp_points

class BLFPacker:
    """Bottom-Left-Fill算法实现"""
    
    def __init__(self, container_width: float, container_height: float):
        self.container_width = container_width
        self.container_height = container_height
        self.placed_polygons: List[PlacedPolygon] = []
        self.collision_detector = CollisionDetector()
    
    def pack_polygons(self, polygons: List[List[Tuple[float, float]]]) -> List[PlacedPolygon]:
        """使用BLF算法排列多边形"""
        results = []
        
        # 按面积降序排序（大的先放）
        indexed_polygons = [(i, poly) for i, poly in enumerate(polygons)]
        indexed_polygons.sort(key=lambda x: GeometryUtils.polygon_area(x[1]), reverse=True)
        
        for original_id, polygon in indexed_polygons:
            best_placement = self._find_best_placement(polygon, original_id)
            
            if best_placement:
                results.append(best_placement)
                self.placed_polygons.append(best_placement)
        
        return results
    
    def _find_best_placement(self, polygon: List[Tuple[float, float]], 
                           original_id: int) -> Optional[PlacedPolygon]:
        """寻找多边形的最佳放置位置"""
        best_placement = None
        best_score = float('inf')
        
        # 尝试不同旋转角度
        for angle_deg in range(0, 360, 30):  # 每30度尝试一次
            angle_rad = math.radians(angle_deg)
            rotated_poly = GeometryUtils.rotate_polygon(polygon, angle_rad)
            
            # 寻找左下角最优位置
            position = self._find_leftmost_bottom_position(rotated_poly)
            
            if position and self._is_valid_placement(rotated_poly, position):
                # 评分：左下优先（x坐标 + y坐标越小越好）
                score = position[0] + position[1]
                if score < best_score:
                    best_score = score
                    translated_poly = GeometryUtils.translate_polygon(
                        rotated_poly, position[0], position[1]
                    )
                    best_placement = PlacedPolygon(
                        vertices=translated_poly,
                        position=position,
                        rotation=angle_deg,
                        original_id=original_id
                    )
        
        return best_placement
    
    def _find_leftmost_bottom_position(self, polygon: List[Tuple[float, float]]) -> Optional[Tuple[float, float]]:
        """寻找最左下角的可行位置"""
        bbox = GeometryUtils.polygon_bounding_box(polygon)
        poly_width = bbox[2] - bbox[0]
        poly_height = bbox[3] - bbox[1]
        
        # 确保多边形能放入容器
        if poly_width > self.container_width or poly_height > self.container_height:
            return None
        
        # 网格搜索（实际应用中可以使用更高效的算法）
        step_size = min(poly_width, poly_height) / 10
        
        for y in np.arange(0, self.container_height - poly_height + step_size, step_size):
            for x in np.arange(0, self.container_width - poly_width + step_size, step_size):
                # 调整位置使多边形边界框的左下角对齐
                adjusted_x = x - bbox[0]
                adjusted_y = y - bbox[1]
                
                if self._is_valid_placement(polygon, (adjusted_x, adjusted_y)):
                    return (adjusted_x, adjusted_y)
        
        return None
    
    def _is_valid_placement(self, polygon: List[Tuple[float, float]], 
                          position: Tuple[float, float]) -> bool:
        """检查放置位置是否有效"""
        # 平移多边形到指定位置
        translated_poly = GeometryUtils.translate_polygon(polygon, position[0], position[1])
        
        # 检查是否超出容器边界
        bbox = GeometryUtils.polygon_bounding_box(translated_poly)
        if (bbox[0] < 0 or bbox[1] < 0 or 
            bbox[2] > self.container_width or bbox[3] > self.container_height):
            return False
        
        # 检查与已放置多边形的碰撞
        for placed in self.placed_polygons:
            if self.collision_detector.polygons_intersect(translated_poly, placed.vertices):
                return False
        
        return True
    
    def calculate_utilization(self) -> float:
        """计算材料利用率"""
        total_area = sum(GeometryUtils.polygon_area(p.vertices) for p in self.placed_polygons)
        container_area = self.container_width * self.container_height
        return total_area / container_area if container_area > 0 else 0

class NestingVisualizer:
    """嵌套结果可视化"""
    
    @staticmethod
    def plot_nesting_result(container_width: float, container_height: float, 
                           placed_polygons: List[PlacedPolygon], 
                           title: str = "Polygon Nesting Result"):
        """绘制嵌套结果"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        # 绘制容器边界
        container = [(0, 0), (container_width, 0), 
                    (container_width, container_height), (0, container_height)]
        container_x = [p[0] for p in container] + [container[0][0]]
        container_y = [p[1] for p in container] + [container[0][1]]
        ax.plot(container_x, container_y, 'k-', linewidth=2, label='Container')
        
        # 绘制已放置的多边形
        colors = plt.cm.Set3(np.linspace(0, 1, len(placed_polygons)))
        
        for i, placed_poly in enumerate(placed_polygons):
            vertices = placed_poly.vertices
            x_coords = [v[0] for v in vertices] + [vertices[0][0]]
            y_coords = [v[1] for v in vertices] + [vertices[0][1]]
            
            ax.fill(x_coords, y_coords, color=colors[i], alpha=0.7, 
                   label=f'Polygon {placed_poly.original_id}')
            ax.plot(x_coords, y_coords, 'k-', linewidth=1)
            
            # 标记重心
            centroid = GeometryUtils.polygon_centroid(vertices)
            ax.plot(centroid[0], centroid[1], 'ko', markersize=3)
        
        ax.set_xlim(-5, container_width + 5)
        ax.set_ylim(-5, container_height + 5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.set_title(title)
        
        plt.tight_layout()
        return fig, ax

def create_sample_polygons() -> List[List[Tuple[float, float]]]:
    """创建示例多边形"""
    polygons = []
    
    # 三角形
    triangle = [(0, 0), (30, 0), (15, 25)]
    polygons.append(triangle)
    
    # 矩形
    rectangle = [(0, 0), (40, 0), (40, 20), (0, 20)]
    polygons.append(rectangle)
    
    # L形多边形
    l_shape = [(0, 0), (25, 0), (25, 15), (10, 15), (10, 30), (0, 30)]
    polygons.append(l_shape)
    
    # 五边形
    pentagon = []
    for i in range(5):
        angle = 2 * math.pi * i / 5
        x = 15 * math.cos(angle) + 15
        y = 15 * math.sin(angle) + 15
        pentagon.append((x, y))
    polygons.append(pentagon)
    
    # 不规则六边形
    hexagon = [(0, 0), (20, 0), (25, 10), (20, 20), (5, 25), (-5, 10)]
    polygons.append(hexagon)
    
    return polygons

def demonstrate_nfp_calculation():
    """演示NFP计算"""
    print("=== NFP计算演示 ===")
    
    # 创建两个简单多边形
    poly1 = [(0, 0), (20, 0), (20, 20), (0, 20)]  # 正方形
    poly2 = [(0, 0), (10, 0), (10, 10), (0, 10)]  # 小正方形
    
    calculator = NFPCalculator()
    nfp = calculator.calculate_nfp_simplified(poly1, poly2)
    
    print(f"多边形1: {poly1}")
    print(f"多边形2: {poly2}")
    print(f"NFP (简化): {nfp}")
    
    # 可视化NFP
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    # 绘制原始多边形
    poly1_x = [p[0] for p in poly1] + [poly1[0][0]]
    poly1_y = [p[1] for p in poly1] + [poly1[0][1]]
    ax.plot(poly1_x, poly1_y, 'b-', linewidth=2, label='Stationary Polygon')
    ax.fill(poly1_x, poly1_y, 'blue', alpha=0.3)
    
    poly2_x = [p[0] for p in poly2] + [poly2[0][0]]
    poly2_y = [p[1] for p in poly2] + [poly2[0][1]]
    ax.plot(poly2_x, poly2_y, 'r-', linewidth=2, label='Moving Polygon')
    ax.fill(poly2_x, poly2_y, 'red', alpha=0.3)
    
    # 绘制NFP
    nfp_x = [p[0] for p in nfp] + [nfp[0][0]]
    nfp_y = [p[1] for p in nfp] + [nfp[0][1]]
    ax.plot(nfp_x, nfp_y, 'g--', linewidth=2, label='NFP (Simplified)')
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_title('No-Fit Polygon (NFP) Demonstration')
    
    plt.tight_layout()
    plt.savefig('/workspace/nfp_demo.png', dpi=150, bbox_inches='tight')
    plt.show()

def demonstrate_blf_packing():
    """演示BLF算法"""
    print("\n=== BLF算法演示 ===")
    
    # 创建容器和多边形
    container_width, container_height = 100, 80
    polygons = create_sample_polygons()
    
    print(f"容器尺寸: {container_width} x {container_height}")
    print(f"多边形数量: {len(polygons)}")
    
    # 执行BLF算法
    packer = BLFPacker(container_width, container_height)
    placed_polygons = packer.pack_polygons(polygons)
    
    # 计算结果
    utilization = packer.calculate_utilization()
    placed_count = len(placed_polygons)
    
    print(f"成功放置: {placed_count}/{len(polygons)} 个多边形")
    print(f"材料利用率: {utilization:.2%}")
    
    # 可视化结果
    visualizer = NestingVisualizer()
    fig, ax = visualizer.plot_nesting_result(
        container_width, container_height, placed_polygons,
        f"BLF Packing Result (Utilization: {utilization:.2%})"
    )
    
    plt.savefig('/workspace/blf_packing_result.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return placed_polygons, utilization

def compare_algorithms():
    """比较不同算法的性能"""
    print("\n=== 算法性能比较 ===")
    
    container_width, container_height = 120, 100
    polygons = create_sample_polygons() * 2  # 增加多边形数量
    
    results = {}
    
    # BLF算法
    packer_blf = BLFPacker(container_width, container_height)
    placed_blf = packer_blf.pack_polygons(polygons)
    utilization_blf = packer_blf.calculate_utilization()
    
    results['BLF'] = {
        'placed_count': len(placed_blf),
        'utilization': utilization_blf,
        'total_polygons': len(polygons)
    }
    
    print("算法性能对比:")
    print(f"{'算法':<10} {'放置数量':<10} {'利用率':<10} {'成功率':<10}")
    print("-" * 45)
    
    for alg_name, result in results.items():
        success_rate = result['placed_count'] / result['total_polygons']
        print(f"{alg_name:<10} {result['placed_count']:<10} {result['utilization']:<10.2%} {success_rate:<10.2%}")

def main():
    """主函数：运行所有演示"""
    print("二维不规则多边形Nesting算法演示")
    print("=" * 50)
    
    # 1. NFP计算演示
    demonstrate_nfp_calculation()
    
    # 2. BLF算法演示
    placed_polygons, utilization = demonstrate_blf_packing()
    
    # 3. 算法比较
    compare_algorithms()
    
    # 4. 输出总结
    print(f"\n=== 演示总结 ===")
    print(f"本演示展示了多边形nesting的核心算法:")
    print(f"1. NFP (No-Fit Polygon) 计算")
    print(f"2. BLF (Bottom-Left-Fill) 排样算法")
    print(f"3. 碰撞检测和几何运算")
    print(f"4. 结果可视化")
    print(f"\n生成的图片文件:")
    print(f"- nfp_demo.png: NFP计算演示")
    print(f"- blf_packing_result.png: BLF算法结果")

if __name__ == "__main__":
    main()