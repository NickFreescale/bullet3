#!/usr/bin/env python3
"""
二维不规则多边形Nesting的工业应用案例
包含纺织、金属加工、皮革等行业的具体实现
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

class MaterialType(Enum):
    """材料类型枚举"""
    FABRIC = "fabric"
    METAL = "metal"
    LEATHER = "leather"
    PAPER = "paper"
    GLASS = "glass"

@dataclass
class MaterialProperties:
    """材料属性"""
    type: MaterialType
    thickness: float
    cost_per_unit: float
    grain_direction: bool = False  # 是否有纹理方向
    cutting_kerf: float = 0.0      # 切割缝隙
    min_spacing: float = 0.0       # 最小间距
    max_rotation_angles: List[float] = None  # 允许的旋转角度

@dataclass
class ProductionConstraints:
    """生产约束条件"""
    max_cutting_length: float = float('inf')  # 最大切割长度
    cutting_speed: float = 1.0                # 切割速度
    setup_time: float = 0.0                   # 设置时间
    material_waste_cost: float = 1.0          # 废料成本
    labor_cost_per_hour: float = 50.0         # 人工成本

class TextileNestingOptimizer:
    """纺织行业嵌套优化器"""
    
    def __init__(self, fabric_width: float, fabric_properties: MaterialProperties):
        self.fabric_width = fabric_width
        self.fabric_properties = fabric_properties
        self.pattern_pieces = []
        self.grain_direction_angle = 0  # 纹理方向角度
    
    def add_pattern_piece(self, vertices: List[Tuple[float, float]], 
                         quantity: int = 1, size: str = "M", 
                         grain_line_angle: float = 0.0,
                         can_rotate: bool = True, can_mirror: bool = False):
        """添加服装纸样"""
        for _ in range(quantity):
            self.pattern_pieces.append({
                'vertices': vertices,
                'size': size,
                'grain_line_angle': grain_line_angle,
                'can_rotate': can_rotate,
                'can_mirror': can_mirror,
                'placed': False,
                'priority': self._calculate_piece_priority(vertices, size)
            })
    
    def _calculate_piece_priority(self, vertices: List[Tuple[float, float]], size: str) -> int:
        """计算纸样优先级"""
        from nesting_example import GeometryUtils
        
        area = GeometryUtils.polygon_area(vertices)
        size_priority = {'XS': 1, 'S': 2, 'M': 3, 'L': 4, 'XL': 5}.get(size, 3)
        
        # 大面积、大尺码优先
        return int(area) + size_priority * 100
    
    def optimize_fabric_layout(self, fabric_length: float = None) -> Dict[str, Any]:
        """优化面料排样"""
        if fabric_length is None:
            fabric_length = self.fabric_width * 2  # 默认长度
        
        # 按优先级排序
        sorted_pieces = sorted(self.pattern_pieces, 
                             key=lambda x: x['priority'], reverse=True)
        
        # 考虑纹理方向约束
        constrained_pieces = []
        for piece in sorted_pieces:
            allowed_angles = self._get_allowed_rotations(piece)
            
            for angle in allowed_angles:
                constrained_pieces.append({
                    'original_piece': piece,
                    'polygon': self._rotate_with_grain_constraint(piece['vertices'], angle),
                    'rotation': angle,
                    'grain_deviation': abs(angle - piece['grain_line_angle'])
                })
        
        # 使用改进的BLF算法
        from nesting_example import BLFPacker
        
        packer = TextileBLFPacker(self.fabric_width, fabric_length, self.fabric_properties)
        result = packer.pack_with_constraints(constrained_pieces)
        
        # 计算成本分析
        cost_analysis = self._calculate_cost_analysis(result, fabric_length)
        
        return {
            'placed_pieces': result,
            'fabric_utilization': len(result) / len(self.pattern_pieces),
            'material_utilization': packer.calculate_utilization(),
            'cost_analysis': cost_analysis,
            'fabric_length_used': fabric_length
        }
    
    def _get_allowed_rotations(self, piece: Dict[str, Any]) -> List[float]:
        """获取允许的旋转角度"""
        base_angle = piece['grain_line_angle']
        
        if not piece['can_rotate']:
            return [base_angle]
        
        if self.fabric_properties.grain_direction:
            # 纺织品通常只允许0度和90度（考虑纹理方向）
            return [base_angle, base_angle + math.pi/2]
        else:
            # 无纹理方向限制，允许多个角度
            return [base_angle + i * math.pi/6 for i in range(12)]  # 每30度
    
    def _rotate_with_grain_constraint(self, vertices: List[Tuple[float, float]], 
                                    angle: float) -> List[Tuple[float, float]]:
        """考虑纹理约束的旋转"""
        from nesting_example import GeometryUtils
        return GeometryUtils.rotate_polygon(vertices, angle)

class TextileBLFPacker:
    """纺织行业专用BLF算法"""
    
    def __init__(self, fabric_width: float, fabric_length: float, 
                 material_props: MaterialProperties):
        self.fabric_width = fabric_width
        self.fabric_length = fabric_length
        self.material_props = material_props
        self.placed_pieces = []
        self.fabric_utilization_map = np.zeros((int(fabric_length), int(fabric_width)))
    
    def pack_with_constraints(self, constrained_pieces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """带约束的排样"""
        result = []
        
        # 按纹理偏差和面积排序
        sorted_pieces = sorted(constrained_pieces, 
                             key=lambda x: (x['grain_deviation'], 
                                           -self._get_polygon_area(x['polygon'])))
        
        for piece_data in sorted_pieces:
            polygon = piece_data['polygon']
            
            # 寻找最佳位置
            position = self._find_best_position_with_constraints(polygon, piece_data)
            
            if position:
                placed_piece = {
                    'polygon': polygon,
                    'position': position,
                    'rotation': piece_data['rotation'],
                    'original_piece': piece_data['original_piece'],
                    'grain_deviation': piece_data['grain_deviation']
                }
                result.append(placed_piece)
                self.placed_pieces.append(placed_piece)
                self._update_utilization_map(polygon, position)
        
        return result
    
    def _find_best_position_with_constraints(self, polygon: List[Tuple[float, float]], 
                                           piece_data: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """考虑约束的位置搜索"""
        from nesting_example import GeometryUtils
        
        bbox = GeometryUtils.polygon_bounding_box(polygon)
        poly_width = bbox[2] - bbox[0]
        poly_height = bbox[3] - bbox[1]
        
        # 添加材料间距
        min_spacing = self.material_props.min_spacing
        
        if (poly_width + min_spacing > self.fabric_width or 
            poly_height + min_spacing > self.fabric_length):
            return None
        
        # 搜索最佳位置
        best_position = None
        best_score = float('inf')
        
        step_size = min(poly_width, poly_height) / 5
        
        for y in np.arange(0, self.fabric_length - poly_height, step_size):
            for x in np.arange(0, self.fabric_width - poly_width, step_size):
                adjusted_x = x - bbox[0]
                adjusted_y = y - bbox[1]
                
                if self._is_valid_position_with_constraints(polygon, (adjusted_x, adjusted_y)):
                    # 评分：考虑位置、纹理偏差、紧密度
                    score = (adjusted_x + adjusted_y +  # 左下优先
                            piece_data['grain_deviation'] * 100 +  # 纹理偏差惩罚
                            self._calculate_waste_penalty(polygon, (adjusted_x, adjusted_y)))
                    
                    if score < best_score:
                        best_score = score
                        best_position = (adjusted_x, adjusted_y)
        
        return best_position
    
    def _is_valid_position_with_constraints(self, polygon: List[Tuple[float, float]], 
                                          position: Tuple[float, float]) -> bool:
        """检查位置是否满足约束"""
        from nesting_example import GeometryUtils, CollisionDetector
        
        translated_poly = GeometryUtils.translate_polygon(polygon, position[0], position[1])
        
        # 边界检查
        bbox = GeometryUtils.polygon_bounding_box(translated_poly)
        if (bbox[0] < 0 or bbox[1] < 0 or 
            bbox[2] > self.fabric_width or bbox[3] > self.fabric_length):
            return False
        
        # 碰撞检查（考虑最小间距）
        detector = CollisionDetector()
        for placed in self.placed_pieces:
            # 扩展已放置多边形以考虑最小间距
            expanded_placed = self._expand_polygon(placed['polygon'], self.material_props.min_spacing)
            if detector.polygons_intersect(translated_poly, expanded_placed):
                return False
        
        return True
    
    def _expand_polygon(self, polygon: List[Tuple[float, float]], distance: float) -> List[Tuple[float, float]]:
        """多边形向外扩展（简化实现）"""
        from nesting_example import GeometryUtils
        
        if distance <= 0:
            return polygon
        
        # 简化：使用边界框扩展
        bbox = GeometryUtils.polygon_bounding_box(polygon)
        expanded = [
            (bbox[0] - distance, bbox[1] - distance),
            (bbox[2] + distance, bbox[1] - distance),
            (bbox[2] + distance, bbox[3] + distance),
            (bbox[0] - distance, bbox[3] + distance)
        ]
        return expanded
    
    def _get_polygon_area(self, polygon: List[Tuple[float, float]]) -> float:
        """获取多边形面积"""
        from nesting_example import GeometryUtils
        return GeometryUtils.polygon_area(polygon)
    
    def _calculate_waste_penalty(self, polygon: List[Tuple[float, float]], 
                               position: Tuple[float, float]) -> float:
        """计算废料惩罚"""
        # 简化：基于位置的废料估算
        return position[0] * 0.1 + position[1] * 0.1
    
    def _update_utilization_map(self, polygon: List[Tuple[float, float]], 
                              position: Tuple[float, float]):
        """更新面料利用率地图"""
        from nesting_example import GeometryUtils
        
        translated_poly = GeometryUtils.translate_polygon(polygon, position[0], position[1])
        bbox = GeometryUtils.polygon_bounding_box(translated_poly)
        
        # 简化：在边界框区域标记为已使用
        x1, y1, x2, y2 = map(int, bbox)
        x1, y1 = max(0, x1), max(0, y1)
        x2 = min(self.fabric_utilization_map.shape[1], x2)
        y2 = min(self.fabric_utilization_map.shape[0], y2)
        
        if x1 < x2 and y1 < y2:
            self.fabric_utilization_map[y1:y2, x1:x2] = 1
    
    def calculate_utilization(self) -> float:
        """计算面料利用率"""
        total_area = self.fabric_width * self.fabric_length
        used_area = sum(self._get_polygon_area(p['polygon']) for p in self.placed_pieces)
        return used_area / total_area if total_area > 0 else 0

class MetalSheetNestingOptimizer:
    """金属板材嵌套优化器"""
    
    def __init__(self, sheet_width: float, sheet_height: float, 
                 material_props: MaterialProperties):
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.material_props = material_props
        self.parts = []
        self.cutting_paths = []
    
    def add_part(self, vertices: List[Tuple[float, float]], quantity: int = 1, 
                material_grade: str = "standard", priority: int = 1):
        """添加零件"""
        for _ in range(quantity):
            self.parts.append({
                'vertices': vertices,
                'material_grade': material_grade,
                'priority': priority,
                'cutting_time': self._estimate_cutting_time(vertices)
            })
    
    def _estimate_cutting_time(self, vertices: List[Tuple[float, float]]) -> float:
        """估算切割时间"""
        perimeter = 0
        for i in range(len(vertices)):
            j = (i + 1) % len(vertices)
            dx = vertices[j][0] - vertices[i][0]
            dy = vertices[j][1] - vertices[i][1]
            perimeter += math.sqrt(dx*dx + dy*dy)
        
        return perimeter / self.material_props.cutting_kerf if self.material_props.cutting_kerf > 0 else perimeter
    
    def optimize_with_cutting_constraints(self) -> Dict[str, Any]:
        """考虑切割约束的优化"""
        
        # 第一步：基础排样
        from nesting_example import BLFPacker
        
        # 为每个零件添加切割缝隙
        adjusted_parts = []
        for part in self.parts:
            adjusted_vertices = self._add_cutting_kerf(part['vertices'])
            adjusted_parts.append(adjusted_vertices)
        
        packer = BLFPacker(self.sheet_width, self.sheet_height)
        placed_polygons = packer.pack_polygons(adjusted_parts)
        
        # 第二步：优化切割路径
        cutting_path = self._optimize_cutting_path(placed_polygons)
        
        # 第三步：成本分析
        cost_analysis = self._calculate_manufacturing_cost(placed_polygons, cutting_path)
        
        return {
            'placed_polygons': placed_polygons,
            'cutting_path': cutting_path,
            'cost_analysis': cost_analysis,
            'material_utilization': packer.calculate_utilization()
        }
    
    def _add_cutting_kerf(self, vertices: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """添加切割缝隙"""
        # 简化实现：向外扩展多边形
        from nesting_example import GeometryUtils
        
        centroid = GeometryUtils.polygon_centroid(vertices)
        kerf_offset = self.material_props.cutting_kerf / 2
        
        expanded_vertices = []
        for x, y in vertices:
            # 向外扩展
            dx = x - centroid[0]
            dy = y - centroid[1]
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                dx_norm = dx / length
                dy_norm = dy / length
                new_x = x + dx_norm * kerf_offset
                new_y = y + dy_norm * kerf_offset
                expanded_vertices.append((new_x, new_y))
            else:
                expanded_vertices.append((x, y))
        
        return expanded_vertices
    
    def _optimize_cutting_path(self, placed_polygons: List) -> List[Tuple[float, float]]:
        """优化切割路径（TSP问题）"""
        if not placed_polygons:
            return []
        
        # 提取所有多边形的重心作为切割点
        from nesting_example import GeometryUtils
        
        cutting_points = []
        for poly_data in placed_polygons:
            if hasattr(poly_data, 'vertices'):
                centroid = GeometryUtils.polygon_centroid(poly_data.vertices)
            else:
                centroid = GeometryUtils.polygon_centroid(poly_data['polygon'])
            cutting_points.append(centroid)
        
        # 使用最近邻算法求解TSP
        path = self._nearest_neighbor_tsp(cutting_points)
        return path
    
    def _nearest_neighbor_tsp(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """最近邻TSP算法"""
        if not points:
            return []
        
        unvisited = set(range(len(points)))
        current = 0
        path = [points[current]]
        unvisited.remove(current)
        
        while unvisited:
            nearest_dist = float('inf')
            nearest_point = None
            
            for point_idx in unvisited:
                dist = self._euclidean_distance(points[current], points[point_idx])
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_point = point_idx
            
            current = nearest_point
            path.append(points[current])
            unvisited.remove(current)
        
        return path
    
    def _euclidean_distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """计算欧几里得距离"""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def _calculate_manufacturing_cost(self, placed_polygons: List, 
                                    cutting_path: List[Tuple[float, float]]) -> Dict[str, float]:
        """计算制造成本"""
        
        # 材料成本
        sheet_area = self.sheet_width * self.sheet_height
        material_cost = sheet_area * self.material_props.cost_per_unit
        
        # 切割成本
        cutting_length = sum(self._euclidean_distance(cutting_path[i], cutting_path[i+1])
                           for i in range(len(cutting_path) - 1))
        cutting_time = cutting_length / self.material_props.thickness  # 简化计算
        cutting_cost = cutting_time * 50  # 假设切割成本50元/小时
        
        # 废料成本
        utilization = len(placed_polygons) / len(self.parts) if self.parts else 0
        waste_cost = (1 - utilization) * material_cost * 0.1  # 废料处理成本
        
        total_cost = material_cost + cutting_cost + waste_cost
        
        return {
            'material_cost': material_cost,
            'cutting_cost': cutting_cost,
            'waste_cost': waste_cost,
            'total_cost': total_cost,
            'cost_per_part': total_cost / len(placed_polygons) if placed_polygons else 0
        }

class LeatherGoodsNesting:
    """皮革制品嵌套优化"""
    
    def __init__(self, hide_dimensions: Tuple[float, float]):
        self.hide_width, self.hide_height = hide_dimensions
        self.defect_areas = []  # 瑕疵区域
        self.quality_zones = {}  # 质量分区
    
    def add_defect_area(self, vertices: List[Tuple[float, float]], severity: str = "minor"):
        """添加皮革瑕疵区域"""
        self.defect_areas.append({
            'vertices': vertices,
            'severity': severity,
            'avoidance_priority': {'minor': 1, 'major': 5, 'critical': 10}.get(severity, 1)
        })
    
    def define_quality_zones(self, zones: Dict[str, List[Tuple[float, float]]]):
        """定义质量分区（如A级、B级、C级区域）"""
        self.quality_zones = zones
    
    def optimize_leather_cutting(self, leather_parts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """优化皮革切割"""
        
        # 按质量要求和优先级排序
        sorted_parts = sorted(leather_parts, 
                            key=lambda x: (x.get('quality_requirement', 'A'), 
                                         -x.get('priority', 0)))
        
        placed_parts = []
        
        for part in sorted_parts:
            best_position = self._find_best_leather_position(part)
            if best_position:
                placed_parts.append({
                    'part': part,
                    'position': best_position['position'],
                    'rotation': best_position['rotation'],
                    'quality_zone': best_position['quality_zone']
                })
        
        # 计算皮革利用率和质量匹配度
        utilization = self._calculate_leather_utilization(placed_parts)
        quality_match = self._calculate_quality_match(placed_parts)
        
        return {
            'placed_parts': placed_parts,
            'leather_utilization': utilization,
            'quality_match_score': quality_match,
            'defect_avoidance_score': self._calculate_defect_avoidance(placed_parts)
        }
    
    def _find_best_leather_position(self, part: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """寻找皮革零件的最佳位置"""
        polygon = part['vertices']
        quality_req = part.get('quality_requirement', 'A')
        
        best_position = None
        best_score = float('inf')
        
        # 在对应质量区域搜索
        target_zones = [zone for zone_name, zone in self.quality_zones.items() 
                       if zone_name.startswith(quality_req)]
        
        for zone in target_zones:
            position = self._search_in_zone(polygon, zone)
            if position:
                score = self._evaluate_leather_position(polygon, position, quality_req)
                if score < best_score:
                    best_score = score
                    best_position = {
                        'position': position,
                        'rotation': 0,  # 简化
                        'quality_zone': quality_req
                    }
        
        return best_position
    
    def _search_in_zone(self, polygon: List[Tuple[float, float]], 
                       zone: List[Tuple[float, float]]) -> Optional[Tuple[float, float]]:
        """在指定区域内搜索位置"""
        from nesting_example import GeometryUtils
        
        zone_bbox = GeometryUtils.polygon_bounding_box(zone)
        poly_bbox = GeometryUtils.polygon_bounding_box(polygon)
        
        # 简化搜索
        for y in np.arange(zone_bbox[1], zone_bbox[3] - (poly_bbox[3] - poly_bbox[1]), 5):
            for x in np.arange(zone_bbox[0], zone_bbox[2] - (poly_bbox[2] - poly_bbox[0]), 5):
                if self._point_in_zone((x, y), zone):
                    return (x - poly_bbox[0], y - poly_bbox[1])
        
        return None
    
    def _point_in_zone(self, point: Tuple[float, float], 
                      zone: List[Tuple[float, float]]) -> bool:
        """判断点是否在区域内"""
        from nesting_example import GeometryUtils
        return GeometryUtils.point_in_polygon(point, zone)
    
    def _evaluate_leather_position(self, polygon: List[Tuple[float, float]], 
                                 position: Tuple[float, float], quality_req: str) -> float:
        """评估皮革位置质量"""
        # 简化评分：位置 + 瑕疵避免 + 质量匹配
        position_score = position[0] + position[1]
        defect_penalty = self._calculate_defect_proximity(polygon, position)
        quality_bonus = {'A': 0, 'B': 10, 'C': 20}.get(quality_req, 0)
        
        return position_score + defect_penalty - quality_bonus
    
    def _calculate_defect_proximity(self, polygon: List[Tuple[float, float]], 
                                  position: Tuple[float, float]) -> float:
        """计算与瑕疵的接近程度"""
        penalty = 0
        for defect in self.defect_areas:
            # 简化：计算重心距离
            from nesting_example import GeometryUtils
            
            poly_centroid = GeometryUtils.polygon_centroid(
                GeometryUtils.translate_polygon(polygon, position[0], position[1])
            )
            defect_centroid = GeometryUtils.polygon_centroid(defect['vertices'])
            
            distance = math.sqrt((poly_centroid[0] - defect_centroid[0])**2 + 
                               (poly_centroid[1] - defect_centroid[1])**2)
            
            # 距离越近惩罚越大
            if distance < 50:  # 50单位内的瑕疵影响
                penalty += defect['avoidance_priority'] * (50 - distance)
        
        return penalty
    
    def _calculate_leather_utilization(self, placed_parts: List[Dict[str, Any]]) -> float:
        """计算皮革利用率"""
        total_area = self.hide_width * self.hide_height
        used_area = sum(self._get_polygon_area(part['part']['vertices']) 
                       for part in placed_parts)
        return used_area / total_area
    
    def _calculate_quality_match(self, placed_parts: List[Dict[str, Any]]) -> float:
        """计算质量匹配度"""
        if not placed_parts:
            return 0
        
        perfect_matches = sum(1 for part in placed_parts 
                            if part['quality_zone'] == part['part'].get('quality_requirement', 'A'))
        return perfect_matches / len(placed_parts)
    
    def _calculate_defect_avoidance(self, placed_parts: List[Dict[str, Any]]) -> float:
        """计算瑕疵避免得分"""
        if not placed_parts or not self.defect_areas:
            return 1.0
        
        total_penalty = 0
        for part in placed_parts:
            penalty = self._calculate_defect_proximity(
                part['part']['vertices'], part['position']
            )
            total_penalty += penalty
        
        # 归一化得分
        max_possible_penalty = len(placed_parts) * len(self.defect_areas) * 500
        return max(0, 1 - total_penalty / max_possible_penalty)
    
    def _get_polygon_area(self, polygon: List[Tuple[float, float]]) -> float:
        """获取多边形面积"""
        from nesting_example import GeometryUtils
        return GeometryUtils.polygon_area(polygon)

class CostOptimizationAnalyzer:
    """成本优化分析器"""
    
    @staticmethod
    def analyze_material_efficiency(nesting_results: List[Dict[str, Any]], 
                                  material_props: MaterialProperties) -> Dict[str, Any]:
        """分析材料效率"""
        
        total_material_cost = 0
        total_waste_cost = 0
        total_cutting_cost = 0
        
        for result in nesting_results:
            utilization = result.get('material_utilization', 0)
            sheet_area = result.get('sheet_area', 1000)
            
            # 材料成本
            material_cost = sheet_area * material_props.cost_per_unit
            total_material_cost += material_cost
            
            # 废料成本
            waste_area = sheet_area * (1 - utilization)
            waste_cost = waste_area * material_props.cost_per_unit * 0.1
            total_waste_cost += waste_cost
            
            # 切割成本（简化）
            cutting_cost = sheet_area * 0.01  # 假设切割成本
            total_cutting_cost += cutting_cost
        
        return {
            'total_material_cost': total_material_cost,
            'total_waste_cost': total_waste_cost,
            'total_cutting_cost': total_cutting_cost,
            'total_cost': total_material_cost + total_waste_cost + total_cutting_cost,
            'average_utilization': np.mean([r.get('material_utilization', 0) for r in nesting_results]),
            'cost_per_unit_area': (total_material_cost + total_waste_cost + total_cutting_cost) / 
                                sum(r.get('sheet_area', 1000) for r in nesting_results)
        }
    
    @staticmethod
    def optimize_batch_production(parts_demand: Dict[str, int], 
                                material_props: MaterialProperties,
                                sheet_dimensions: Tuple[float, float]) -> Dict[str, Any]:
        """优化批量生产"""
        
        sheet_width, sheet_height = sheet_dimensions
        sheet_area = sheet_width * sheet_height
        
        # 计算所需板材数量
        total_parts_area = sum(area * quantity for area, quantity in parts_demand.items())
        estimated_sheets = math.ceil(total_parts_area / (sheet_area * 0.8))  # 假设80%利用率
        
        # 批次优化策略
        batch_strategies = {
            'same_size_batching': {
                'description': '相同尺寸分批',
                'efficiency': 0.85,
                'setup_time_factor': 0.5
            },
            'mixed_size_batching': {
                'description': '混合尺寸分批',
                'efficiency': 0.75,
                'setup_time_factor': 1.0
            },
            'priority_batching': {
                'description': '优先级分批',
                'efficiency': 0.80,
                'setup_time_factor': 0.8
            }
        }
        
        best_strategy = None
        best_cost = float('inf')
        
        for strategy_name, strategy in batch_strategies.items():
            # 计算总成本
            material_cost = estimated_sheets * sheet_area * material_props.cost_per_unit
            processing_cost = estimated_sheets * strategy['setup_time_factor'] * 100
            efficiency_bonus = strategy['efficiency'] * material_cost * 0.1
            
            total_cost = material_cost + processing_cost - efficiency_bonus
            
            if total_cost < best_cost:
                best_cost = total_cost
                best_strategy = strategy_name
        
        return {
            'recommended_strategy': best_strategy,
            'estimated_sheets': estimated_sheets,
            'estimated_cost': best_cost,
            'cost_breakdown': {
                'material': estimated_sheets * sheet_area * material_props.cost_per_unit,
                'processing': estimated_sheets * batch_strategies[best_strategy]['setup_time_factor'] * 100,
                'efficiency_saving': batch_strategies[best_strategy]['efficiency'] * 
                                   estimated_sheets * sheet_area * material_props.cost_per_unit * 0.1
            }
        }

def demonstrate_textile_application():
    """演示纺织行业应用"""
    print("=== 纺织行业应用演示 ===")
    
    # 定义面料属性
    fabric_props = MaterialProperties(
        type=MaterialType.FABRIC,
        thickness=1.0,
        cost_per_unit=0.05,  # 5分/平方厘米
        grain_direction=True,
        min_spacing=2.0
    )
    
    # 创建纺织优化器
    fabric_width = 150  # 面料幅宽150cm
    optimizer = TextileNestingOptimizer(fabric_width, fabric_props)
    
    # 添加服装纸样（T恤的前片、后片、袖子等）
    # T恤前片
    front_panel = [(0, 0), (40, 0), (45, 10), (45, 50), (35, 60), 
                   (5, 60), (-5, 50), (-5, 10)]
    optimizer.add_pattern_piece(front_panel, quantity=2, size="M")
    
    # T恤后片
    back_panel = [(0, 0), (40, 0), (40, 55), (0, 55)]
    optimizer.add_pattern_piece(back_panel, quantity=2, size="M")
    
    # 袖子
    sleeve = [(0, 0), (25, 0), (30, 5), (30, 35), (25, 40), (0, 40), (-5, 35), (-5, 5)]
    optimizer.add_pattern_piece(sleeve, quantity=4, size="M")
    
    # 优化排样
    result = optimizer.optimize_fabric_layout(fabric_length=200)
    
    print(f"面料利用率: {result['material_utilization']:.2%}")
    print(f"纸样放置成功率: {result['fabric_utilization']:.2%}")
    print(f"成本分析: {result['cost_analysis']}")
    
    return result

def demonstrate_metal_application():
    """演示金属加工应用"""
    print("\n=== 金属加工应用演示 ===")
    
    # 定义金属板材属性
    metal_props = MaterialProperties(
        type=MaterialType.METAL,
        thickness=3.0,
        cost_per_unit=0.8,  # 8毛/平方厘米
        cutting_kerf=2.0,   # 2mm切割缝隙
        min_spacing=5.0     # 5mm最小间距
    )
    
    # 创建金属嵌套优化器
    sheet_width, sheet_height = 200, 100  # 2m x 1m板材
    optimizer = MetalSheetNestingOptimizer(sheet_width, sheet_height, metal_props)
    
    # 添加金属零件
    # 支架
    bracket = [(0, 0), (30, 0), (30, 20), (25, 25), (5, 25), (0, 20)]
    optimizer.add_part(bracket, quantity=10, priority=1)
    
    # 连接板
    plate = [(0, 0), (50, 0), (50, 15), (0, 15)]
    optimizer.add_part(plate, quantity=6, priority=2)
    
    # 角铁
    angle_iron = [(0, 0), (20, 0), (20, 5), (5, 5), (5, 20), (0, 20)]
    optimizer.add_part(angle_iron, quantity=8, priority=1)
    
    # 优化排样
    result = optimizer.optimize_with_cutting_constraints()
    
    print(f"板材利用率: {result['material_utilization']:.2%}")
    print(f"切割路径长度: {len(result['cutting_path'])} 个切割点")
    print(f"制造成本分析:")
    for cost_type, cost_value in result['cost_analysis'].items():
        print(f"  {cost_type}: {cost_value:.2f} 元")
    
    return result

def demonstrate_leather_application():
    """演示皮革制品应用"""
    print("\n=== 皮革制品应用演示 ===")
    
    # 创建皮革嵌套优化器
    hide_dimensions = (180, 120)  # 皮革尺寸
    optimizer = LeatherGoodsNesting(hide_dimensions)
    
    # 定义质量分区
    quality_zones = {
        'A': [(20, 20), (160, 20), (160, 100), (20, 100)],  # 中心A级区域
        'B': [(10, 10), (170, 10), (170, 110), (10, 110)],  # B级区域
        'C': [(0, 0), (180, 0), (180, 120), (0, 120)]       # 整个皮革C级区域
    }
    optimizer.define_quality_zones(quality_zones)
    
    # 添加瑕疵区域
    defect1 = [(50, 50), (60, 50), (60, 60), (50, 60)]
    optimizer.add_defect_area(defect1, severity="major")
    
    defect2 = [(100, 80), (110, 80), (110, 90), (100, 90)]
    optimizer.add_defect_area(defect2, severity="minor")
    
    # 定义皮革制品零件
    leather_parts = [
        {
            'vertices': [(0, 0), (30, 0), (30, 40), (0, 40)],  # 钱包主体
            'quality_requirement': 'A',
            'priority': 5
        },
        {
            'vertices': [(0, 0), (15, 0), (15, 20), (0, 20)],  # 卡位
            'quality_requirement': 'B',
            'priority': 3
        },
        {
            'vertices': [(0, 0), (25, 0), (25, 8), (0, 8)],   # 拉链片
            'quality_requirement': 'A',
            'priority': 4
        }
    ]
    
    # 优化皮革切割
    result = optimizer.optimize_leather_cutting(leather_parts * 3)  # 3套制品
    
    print(f"皮革利用率: {result['leather_utilization']:.2%}")
    print(f"质量匹配度: {result['quality_match_score']:.2%}")
    print(f"瑕疵避免得分: {result['defect_avoidance_score']:.2%}")
    
    return result

def create_industry_comparison():
    """创建行业应用对比"""
    print("\n=== 行业应用对比分析 ===")
    
    industries = {
        'textile': {
            'name': '纺织行业',
            'typical_utilization': 0.85,
            'main_constraints': ['纹理方向', '尺码配比', '面料节约'],
            'cost_factors': ['面料成本', '人工成本', '废料处理'],
            'optimization_focus': '材料利用率'
        },
        'metal': {
            'name': '金属加工',
            'typical_utilization': 0.75,
            'main_constraints': ['切割缝隙', '热变形', '切割路径'],
            'cost_factors': ['原材料', '切割成本', '后处理'],
            'optimization_focus': '总成本最小'
        },
        'leather': {
            'name': '皮革制品',
            'typical_utilization': 0.70,
            'main_constraints': ['质量分区', '瑕疵避免', '纹理方向'],
            'cost_factors': ['皮革成本', '质量损失', '手工成本'],
            'optimization_focus': '质量匹配'
        }
    }
    
    # 可视化对比
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 利用率对比
    industry_names = [info['name'] for info in industries.values()]
    utilizations = [info['typical_utilization'] for info in industries.values()]
    
    bars = ax1.bar(industry_names, utilizations, color=['lightblue', 'lightcoral', 'lightgreen'])
    ax1.set_ylabel('典型材料利用率')
    ax1.set_title('不同行业的材料利用率对比')
    ax1.set_ylim(0, 1)
    
    for bar, util in zip(bars, utilizations):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{util:.1%}', ha='center', va='bottom')
    
    # 约束复杂度对比
    constraint_counts = [len(info['main_constraints']) for info in industries.values()]
    ax2.bar(industry_names, constraint_counts, color=['lightblue', 'lightcoral', 'lightgreen'])
    ax2.set_ylabel('主要约束数量')
    ax2.set_title('约束复杂度对比')
    
    # 成本因素分析
    cost_factor_counts = [len(info['cost_factors']) for info in industries.values()]
    ax3.bar(industry_names, cost_factor_counts, color=['lightblue', 'lightcoral', 'lightgreen'])
    ax3.set_ylabel('成本因素数量')
    ax3.set_title('成本因素复杂度')
    
    # 优化重点分布
    focus_types = {}
    for info in industries.values():
        focus = info['optimization_focus']
        focus_types[focus] = focus_types.get(focus, 0) + 1
    
    ax4.pie(focus_types.values(), labels=focus_types.keys(), autopct='%1.1f%%',
           colors=['gold', 'lightcoral', 'lightblue'])
    ax4.set_title('优化重点分布')
    
    plt.tight_layout()
    plt.savefig('/workspace/industry_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    return industries

def generate_performance_report(textile_result: Dict[str, Any], 
                              metal_result: Dict[str, Any], 
                              leather_result: Dict[str, Any]) -> str:
    """生成性能报告"""
    
    report = f"""
# 多边形Nesting工业应用性能报告

## 执行摘要
本报告分析了三个主要工业领域中二维不规则多边形嵌套算法的应用效果。

## 纺织行业结果
- **材料利用率**: {textile_result['material_utilization']:.2%}
- **纸样放置成功率**: {textile_result['fabric_utilization']:.2%}
- **面料长度使用**: {textile_result['fabric_length_used']:.1f} cm
- **主要优势**: 考虑纹理方向，适合大批量生产

## 金属加工结果  
- **板材利用率**: {metal_result['material_utilization']:.2%}
- **切割路径优化**: {len(metal_result['cutting_path'])} 个切割点
- **总制造成本**: {metal_result['cost_analysis']['total_cost']:.2f} 元
- **单件成本**: {metal_result['cost_analysis']['cost_per_part']:.2f} 元/件
- **主要优势**: 综合考虑切割成本和材料成本

## 皮革制品结果
- **皮革利用率**: {leather_result['leather_utilization']:.2%}
- **质量匹配度**: {leather_result['quality_match_score']:.2%}
- **瑕疵避免得分**: {leather_result['defect_avoidance_score']:.2%}
- **主要优势**: 质量分区管理，瑕疵智能避免

## 关键发现
1. **纺织行业**具有最高的材料利用率潜力，但受纹理方向约束较大
2. **金属加工**需要平衡材料利用率和切割成本
3. **皮革制品**的质量匹配比单纯的利用率更重要

## 建议
1. 根据行业特点选择合适的优化目标
2. 充分考虑材料特性和生产约束
3. 建立完整的成本模型进行综合优化
"""
    
    return report

def main():
    """主函数"""
    print("二维不规则多边形Nesting工业应用演示")
    print("=" * 60)
    
    # 1. 纺织行业应用
    textile_result = demonstrate_textile_application()
    
    # 2. 金属加工应用
    metal_result = demonstrate_metal_application()
    
    # 3. 皮革制品应用
    leather_result = demonstrate_leather_application()
    
    # 4. 行业对比分析
    industry_comparison = create_industry_comparison()
    
    # 5. 生成性能报告
    report = generate_performance_report(textile_result, metal_result, leather_result)
    
    # 保存报告
    with open('/workspace/performance_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n=== 工业应用演示完成 ===")
    print(f"生成的文件:")
    print(f"- industry_comparison.png: 行业对比分析图")
    print(f"- performance_report.md: 详细性能报告")
    
    # 输出关键指标总结
    print(f"\n关键指标总结:")
    print(f"纺织行业 - 材料利用率: {textile_result['material_utilization']:.2%}")
    print(f"金属加工 - 板材利用率: {metal_result['material_utilization']:.2%}")
    print(f"皮革制品 - 质量匹配度: {leather_result['quality_match_score']:.2%}")

if __name__ == "__main__":
    main()