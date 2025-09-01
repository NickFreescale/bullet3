#!/usr/bin/env python3
"""
高级多边形Nesting算法实现
包含遗传算法、模拟退火算法和深度强化学习框架
"""

import random
import math
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import copy

@dataclass
class Individual:
    """遗传算法个体"""
    sequence: List[int]  # 多边形放置序列
    rotations: List[float]  # 对应的旋转角度
    fitness: float = 0.0
    placed_polygons: List = field(default_factory=list)

class NestingAlgorithm(ABC):
    """嵌套算法基类"""
    
    @abstractmethod
    def solve(self, polygons: List[List[Tuple[float, float]]], 
              container_width: float, container_height: float) -> Dict[str, Any]:
        pass

class GeneticAlgorithmNesting(NestingAlgorithm):
    """遗传算法实现"""
    
    def __init__(self, population_size: int = 50, generations: int = 100, 
                 mutation_rate: float = 0.1, crossover_rate: float = 0.8):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.best_fitness_history = []
    
    def solve(self, polygons: List[List[Tuple[float, float]]], 
              container_width: float, container_height: float) -> Dict[str, Any]:
        """使用遗传算法求解嵌套问题"""
        
        self.polygons = polygons
        self.container_width = container_width
        self.container_height = container_height
        self.num_polygons = len(polygons)
        
        # 初始化种群
        population = self._initialize_population()
        
        # 进化过程
        for generation in range(self.generations):
            # 评估适应度
            for individual in population:
                individual.fitness = self._evaluate_fitness(individual)
            
            # 记录最佳适应度
            best_fitness = max(ind.fitness for ind in population)
            self.best_fitness_history.append(best_fitness)
            
            print(f"Generation {generation + 1}: Best fitness = {best_fitness:.4f}")
            
            # 选择、交叉、变异
            new_population = []
            
            # 精英保留
            population.sort(key=lambda x: x.fitness, reverse=True)
            elite_size = max(1, self.population_size // 10)
            new_population.extend(population[:elite_size])
            
            # 生成新个体
            while len(new_population) < self.population_size:
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)
                
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
                
                if random.random() < self.mutation_rate:
                    self._mutate(child1)
                if random.random() < self.mutation_rate:
                    self._mutate(child2)
                
                new_population.extend([child1, child2])
            
            population = new_population[:self.population_size]
        
        # 返回最佳解
        best_individual = max(population, key=lambda x: x.fitness)
        return {
            'best_individual': best_individual,
            'best_fitness': best_individual.fitness,
            'fitness_history': self.best_fitness_history,
            'placed_polygons': best_individual.placed_polygons
        }
    
    def _initialize_population(self) -> List[Individual]:
        """初始化种群"""
        population = []
        
        for _ in range(self.population_size):
            sequence = list(range(self.num_polygons))
            random.shuffle(sequence)
            
            rotations = [random.uniform(0, 2 * math.pi) for _ in range(self.num_polygons)]
            
            individual = Individual(sequence=sequence, rotations=rotations)
            population.append(individual)
        
        return population
    
    def _evaluate_fitness(self, individual: Individual) -> float:
        """评估个体适应度"""
        from nesting_example import BLFPacker, GeometryUtils
        
        # 使用BLF算法按照个体的序列和旋转角度放置多边形
        packer = BLFPacker(self.container_width, self.container_height)
        placed_polygons = []
        
        for i, poly_idx in enumerate(individual.sequence):
            polygon = self.polygons[poly_idx]
            rotation = individual.rotations[i]
            
            # 旋转多边形
            rotated_poly = GeometryUtils.rotate_polygon(polygon, rotation)
            
            # 尝试放置
            position = packer._find_leftmost_bottom_position(rotated_poly)
            if position and packer._is_valid_placement(rotated_poly, position):
                translated_poly = GeometryUtils.translate_polygon(
                    rotated_poly, position[0], position[1]
                )
                placed_polygon = {
                    'vertices': translated_poly,
                    'position': position,
                    'rotation': rotation,
                    'original_id': poly_idx
                }
                placed_polygons.append(placed_polygon)
                packer.placed_polygons.append(type('PlacedPolygon', (), placed_polygon)())
        
        individual.placed_polygons = placed_polygons
        
        # 适应度 = 材料利用率 + 放置成功率
        utilization = len(placed_polygons) / self.num_polygons
        if len(placed_polygons) > 0:
            material_efficiency = packer.calculate_utilization()
        else:
            material_efficiency = 0
        
        fitness = 0.6 * utilization + 0.4 * material_efficiency
        return fitness
    
    def _tournament_selection(self, population: List[Individual], tournament_size: int = 3) -> Individual:
        """锦标赛选择"""
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness)
    
    def _crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """部分映射交叉（PMX）"""
        size = len(parent1.sequence)
        
        # 选择交叉点
        start = random.randint(0, size - 2)
        end = random.randint(start + 1, size - 1)
        
        # 创建子代
        child1_seq = [-1] * size
        child2_seq = [-1] * size
        
        # 复制交叉段
        child1_seq[start:end+1] = parent1.sequence[start:end+1]
        child2_seq[start:end+1] = parent2.sequence[start:end+1]
        
        # 填充剩余位置
        self._fill_remaining_pmx(child1_seq, parent2.sequence, start, end)
        self._fill_remaining_pmx(child2_seq, parent1.sequence, start, end)
        
        # 交叉旋转角度
        child1_rot = parent1.rotations[:]
        child2_rot = parent2.rotations[:]
        
        for i in range(start, end + 1):
            child1_rot[i], child2_rot[i] = child2_rot[i], child1_rot[i]
        
        return (Individual(sequence=child1_seq, rotations=child1_rot),
                Individual(sequence=child2_seq, rotations=child2_rot))
    
    def _fill_remaining_pmx(self, child_seq: List[int], parent_seq: List[int], 
                           start: int, end: int):
        """PMX交叉的剩余位置填充"""
        for i in range(len(parent_seq)):
            if i < start or i > end:
                value = parent_seq[i]
                if value not in child_seq[start:end+1]:
                    child_seq[i] = value
                else:
                    # 找到映射值
                    pos = child_seq[start:end+1].index(value) + start
                    mapped_value = parent_seq[pos]
                    while mapped_value in child_seq[start:end+1]:
                        pos = child_seq[start:end+1].index(mapped_value) + start
                        mapped_value = parent_seq[pos]
                    child_seq[i] = mapped_value
    
    def _mutate(self, individual: Individual):
        """变异操作"""
        # 序列变异：交换两个位置
        if random.random() < 0.5:
            i, j = random.sample(range(len(individual.sequence)), 2)
            individual.sequence[i], individual.sequence[j] = individual.sequence[j], individual.sequence[i]
        
        # 旋转变异：随机调整旋转角度
        for i in range(len(individual.rotations)):
            if random.random() < 0.3:
                individual.rotations[i] += random.uniform(-0.5, 0.5)
                individual.rotations[i] = individual.rotations[i] % (2 * math.pi)

class SimulatedAnnealingNesting(NestingAlgorithm):
    """模拟退火算法实现"""
    
    def __init__(self, initial_temp: float = 1000, final_temp: float = 1, 
                 cooling_rate: float = 0.95, max_iterations: int = 1000):
        self.initial_temp = initial_temp
        self.final_temp = final_temp
        self.cooling_rate = cooling_rate
        self.max_iterations = max_iterations
        self.temp_history = []
        self.fitness_history = []
    
    def solve(self, polygons: List[List[Tuple[float, float]]], 
              container_width: float, container_height: float) -> Dict[str, Any]:
        """使用模拟退火算法求解"""
        
        self.polygons = polygons
        self.container_width = container_width
        self.container_height = container_height
        
        # 初始解
        current_solution = self._generate_initial_solution()
        current_fitness = self._evaluate_solution(current_solution)
        
        best_solution = copy.deepcopy(current_solution)
        best_fitness = current_fitness
        
        temperature = self.initial_temp
        
        for iteration in range(self.max_iterations):
            # 生成邻域解
            new_solution = self._generate_neighbor(current_solution)
            new_fitness = self._evaluate_solution(new_solution)
            
            # 计算接受概率
            if new_fitness > current_fitness:
                # 更好的解直接接受
                current_solution = new_solution
                current_fitness = new_fitness
            else:
                # 较差的解以一定概率接受
                delta = new_fitness - current_fitness
                probability = math.exp(delta / temperature)
                if random.random() < probability:
                    current_solution = new_solution
                    current_fitness = new_fitness
            
            # 更新最佳解
            if current_fitness > best_fitness:
                best_solution = copy.deepcopy(current_solution)
                best_fitness = current_fitness
            
            # 降温
            temperature *= self.cooling_rate
            temperature = max(temperature, self.final_temp)
            
            # 记录历史
            self.temp_history.append(temperature)
            self.fitness_history.append(current_fitness)
            
            if iteration % 100 == 0:
                print(f"Iteration {iteration}: T={temperature:.2f}, "
                      f"Current={current_fitness:.4f}, Best={best_fitness:.4f}")
        
        return {
            'best_solution': best_solution,
            'best_fitness': best_fitness,
            'fitness_history': self.fitness_history,
            'temp_history': self.temp_history
        }
    
    def _generate_initial_solution(self) -> Dict[str, Any]:
        """生成初始解"""
        sequence = list(range(len(self.polygons)))
        random.shuffle(sequence)
        rotations = [random.uniform(0, 2 * math.pi) for _ in range(len(self.polygons))]
        
        return {
            'sequence': sequence,
            'rotations': rotations
        }
    
    def _generate_neighbor(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """生成邻域解"""
        new_solution = copy.deepcopy(solution)
        
        # 随机选择邻域操作
        operation = random.choice(['swap', 'insert', 'rotate'])
        
        if operation == 'swap':
            # 交换两个多边形的位置
            i, j = random.sample(range(len(new_solution['sequence'])), 2)
            new_solution['sequence'][i], new_solution['sequence'][j] = \
                new_solution['sequence'][j], new_solution['sequence'][i]
        
        elif operation == 'insert':
            # 将一个多边形插入到新位置
            old_pos = random.randint(0, len(new_solution['sequence']) - 1)
            new_pos = random.randint(0, len(new_solution['sequence']) - 1)
            
            item = new_solution['sequence'].pop(old_pos)
            new_solution['sequence'].insert(new_pos, item)
        
        elif operation == 'rotate':
            # 调整旋转角度
            idx = random.randint(0, len(new_solution['rotations']) - 1)
            new_solution['rotations'][idx] += random.uniform(-0.5, 0.5)
            new_solution['rotations'][idx] %= (2 * math.pi)
        
        return new_solution
    
    def _evaluate_solution(self, solution: Dict[str, Any]) -> float:
        """评估解的质量"""
        from nesting_example import BLFPacker, GeometryUtils
        
        packer = BLFPacker(self.container_width, self.container_height)
        placed_count = 0
        
        for i, poly_idx in enumerate(solution['sequence']):
            polygon = self.polygons[poly_idx]
            rotation = solution['rotations'][i]
            
            rotated_poly = GeometryUtils.rotate_polygon(polygon, rotation)
            position = packer._find_leftmost_bottom_position(rotated_poly)
            
            if position and packer._is_valid_placement(rotated_poly, position):
                placed_count += 1
                translated_poly = GeometryUtils.translate_polygon(
                    rotated_poly, position[0], position[1]
                )
                packer.placed_polygons.append(
                    type('PlacedPolygon', (), {
                        'vertices': translated_poly,
                        'position': position,
                        'rotation': rotation,
                        'original_id': poly_idx
                    })()
                )
        
        # 适应度 = 放置成功率 * 材料利用率
        success_rate = placed_count / len(self.polygons)
        material_utilization = packer.calculate_utilization() if placed_count > 0 else 0
        
        return success_rate * 0.6 + material_utilization * 0.4

class DeepRLNestingFramework:
    """深度强化学习框架（简化版）"""
    
    def __init__(self, state_dim: int = 64, action_dim: int = 100, 
                 learning_rate: float = 0.001):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = learning_rate
        
        # 简化的神经网络（实际应用中使用PyTorch/TensorFlow）
        self.policy_net = self._create_simple_network()
        self.value_net = self._create_simple_network()
        
        # 经验回放缓冲区
        self.experience_buffer = []
        self.max_buffer_size = 10000
    
    def _create_simple_network(self) -> Dict[str, np.ndarray]:
        """创建简化的神经网络权重"""
        return {
            'W1': np.random.normal(0, 0.1, (self.state_dim, 128)),
            'b1': np.zeros(128),
            'W2': np.random.normal(0, 0.1, (128, 64)),
            'b2': np.zeros(64),
            'W3': np.random.normal(0, 0.1, (64, self.action_dim)),
            'b3': np.zeros(self.action_dim)
        }
    
    def _forward_pass(self, network: Dict[str, np.ndarray], state: np.ndarray) -> np.ndarray:
        """前向传播"""
        h1 = np.maximum(0, np.dot(state, network['W1']) + network['b1'])  # ReLU
        h2 = np.maximum(0, np.dot(h1, network['W2']) + network['b2'])     # ReLU
        output = np.dot(h2, network['W3']) + network['b3']
        return output
    
    def extract_polygon_features(self, polygon: List[Tuple[float, float]]) -> np.ndarray:
        """提取多边形特征向量"""
        from nesting_example import GeometryUtils
        
        # 基础几何特征
        area = GeometryUtils.polygon_area(polygon)
        centroid = GeometryUtils.polygon_centroid(polygon)
        bbox = GeometryUtils.polygon_bounding_box(polygon)
        
        # 形状描述符：质心到轮廓的距离（极坐标描述）
        num_samples = 32
        angles = np.linspace(0, 2 * math.pi, num_samples, endpoint=False)
        distances = []
        
        for angle in angles:
            # 从质心发射射线，计算到边界的距离
            ray_end_x = centroid[0] + 100 * math.cos(angle)
            ray_end_y = centroid[1] + 100 * math.sin(angle)
            
            # 简化：使用边界框距离作为近似
            if angle < math.pi / 2:  # 第一象限
                dist = min(bbox[2] - centroid[0], bbox[3] - centroid[1])
            elif angle < math.pi:  # 第二象限
                dist = min(centroid[0] - bbox[0], bbox[3] - centroid[1])
            elif angle < 3 * math.pi / 2:  # 第三象限
                dist = min(centroid[0] - bbox[0], centroid[1] - bbox[1])
            else:  # 第四象限
                dist = min(bbox[2] - centroid[0], centroid[1] - bbox[1])
            
            distances.append(dist)
        
        # 归一化特征
        distances = np.array(distances)
        distances = distances / np.max(distances) if np.max(distances) > 0 else distances
        
        # 组合特征向量
        features = np.concatenate([
            [area / 1000],  # 归一化面积
            [centroid[0] / 100, centroid[1] / 100],  # 归一化重心
            [(bbox[2] - bbox[0]) / 100, (bbox[3] - bbox[1]) / 100],  # 归一化尺寸
            distances  # 形状描述符
        ])
        
        # 填充到固定维度
        if len(features) < self.state_dim:
            features = np.pad(features, (0, self.state_dim - len(features)))
        else:
            features = features[:self.state_dim]
        
        return features
    
    def train_episode(self, polygons: List[List[Tuple[float, float]]], 
                     container_width: float, container_height: float) -> float:
        """训练一个episode"""
        total_reward = 0
        states = []
        actions = []
        rewards = []
        
        # 模拟一个episode
        for i, polygon in enumerate(polygons):
            # 提取状态特征
            state = self.extract_polygon_features(polygon)
            states.append(state)
            
            # 选择动作（简化：随机选择位置和角度）
            action_probs = self._forward_pass(self.policy_net, state)
            action = np.random.choice(len(action_probs), p=self._softmax(action_probs))
            actions.append(action)
            
            # 计算奖励（简化）
            reward = random.uniform(0, 1)  # 实际应用中基于放置结果计算
            rewards.append(reward)
            total_reward += reward
        
        # 存储经验
        experience = {
            'states': states,
            'actions': actions,
            'rewards': rewards
        }
        self._store_experience(experience)
        
        return total_reward
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Softmax激活函数"""
        exp_x = np.exp(x - np.max(x))
        return exp_x / np.sum(exp_x)
    
    def _store_experience(self, experience: Dict[str, Any]):
        """存储经验到回放缓冲区"""
        self.experience_buffer.append(experience)
        if len(self.experience_buffer) > self.max_buffer_size:
            self.experience_buffer.pop(0)

class AdvancedNestingOptimizer:
    """高级嵌套优化器"""
    
    def __init__(self):
        self.algorithms = {
            'genetic': GeneticAlgorithmNesting(),
            'simulated_annealing': SimulatedAnnealingNesting(),
            'deep_rl': DeepRLNestingFramework()
        }
    
    def benchmark_algorithms(self, polygons: List[List[Tuple[float, float]]], 
                           container_width: float, container_height: float) -> Dict[str, Any]:
        """基准测试不同算法"""
        results = {}
        
        print("开始算法基准测试...")
        
        # 测试遗传算法
        print("\n测试遗传算法...")
        ga_result = self.algorithms['genetic'].solve(polygons, container_width, container_height)
        results['genetic'] = {
            'fitness': ga_result['best_fitness'],
            'placed_count': len(ga_result['placed_polygons']),
            'algorithm': 'Genetic Algorithm'
        }
        
        # 测试模拟退火
        print("\n测试模拟退火算法...")
        sa_result = self.algorithms['simulated_annealing'].solve(polygons, container_width, container_height)
        results['simulated_annealing'] = {
            'fitness': sa_result['best_fitness'],
            'placed_count': 0,  # 简化版本
            'algorithm': 'Simulated Annealing'
        }
        
        return results
    
    def visualize_algorithm_comparison(self, results: Dict[str, Any]):
        """可视化算法比较结果"""
        algorithms = list(results.keys())
        fitness_scores = [results[alg]['fitness'] for alg in algorithms]
        algorithm_names = [results[alg]['algorithm'] for alg in algorithms]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 适应度比较
        bars1 = ax1.bar(algorithm_names, fitness_scores, 
                       color=['skyblue', 'lightcoral', 'lightgreen'])
        ax1.set_ylabel('Fitness Score')
        ax1.set_title('Algorithm Fitness Comparison')
        ax1.set_ylim(0, 1)
        
        # 添加数值标签
        for bar, score in zip(bars1, fitness_scores):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{score:.3f}', ha='center', va='bottom')
        
        # 放置成功数量比较
        placed_counts = [results[alg]['placed_count'] for alg in algorithms]
        bars2 = ax2.bar(algorithm_names, placed_counts,
                       color=['skyblue', 'lightcoral', 'lightgreen'])
        ax2.set_ylabel('Placed Polygons Count')
        ax2.set_title('Placement Success Comparison')
        
        for bar, count in zip(bars2, placed_counts):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{count}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('/workspace/algorithm_comparison.png', dpi=150, bbox_inches='tight')
        plt.show()

def demonstrate_advanced_algorithms():
    """演示高级算法"""
    print("=== 高级算法演示 ===")
    
    # 创建测试数据
    from nesting_example import create_sample_polygons
    
    polygons = create_sample_polygons()
    container_width, container_height = 150, 120
    
    print(f"测试数据: {len(polygons)} 个多边形")
    print(f"容器尺寸: {container_width} x {container_height}")
    
    # 创建优化器并运行基准测试
    optimizer = AdvancedNestingOptimizer()
    results = optimizer.benchmark_algorithms(polygons, container_width, container_height)
    
    # 显示结果
    print(f"\n=== 算法性能对比 ===")
    print(f"{'算法':<20} {'适应度':<10} {'放置数量':<10}")
    print("-" * 45)
    
    for alg_name, result in results.items():
        print(f"{result['algorithm']:<20} {result['fitness']:<10.4f} {result['placed_count']:<10}")
    
    # 可视化比较结果
    optimizer.visualize_algorithm_comparison(results)
    
    return results

def demonstrate_feature_extraction():
    """演示特征提取"""
    print("\n=== 特征提取演示 ===")
    
    from nesting_example import create_sample_polygons
    
    polygons = create_sample_polygons()
    rl_framework = DeepRLNestingFramework()
    
    print("多边形特征提取结果:")
    for i, polygon in enumerate(polygons):
        features = rl_framework.extract_polygon_features(polygon)
        print(f"多边形 {i}: 特征维度 = {len(features)}")
        print(f"  前5个特征值: {features[:5]}")
        print(f"  特征值范围: [{np.min(features):.3f}, {np.max(features):.3f}]")

def plot_optimization_convergence():
    """绘制优化收敛曲线"""
    print("\n=== 优化收敛分析 ===")
    
    # 模拟收敛数据
    generations = range(1, 101)
    ga_fitness = [0.3 + 0.4 * (1 - math.exp(-i/20)) + 0.1 * random.random() 
                  for i in generations]
    sa_fitness = [0.2 + 0.5 * (1 - math.exp(-i/30)) + 0.15 * random.random() 
                  for i in generations]
    
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(generations, ga_fitness, 'b-', label='Genetic Algorithm', linewidth=2)
    plt.plot(generations, sa_fitness, 'r-', label='Simulated Annealing', linewidth=2)
    plt.xlabel('Generation/Iteration')
    plt.ylabel('Fitness Score')
    plt.title('Algorithm Convergence Comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 温度变化曲线（模拟退火）
    plt.subplot(2, 1, 2)
    temperatures = [1000 * (0.95 ** i) for i in range(100)]
    plt.plot(range(100), temperatures, 'orange', linewidth=2)
    plt.xlabel('Iteration')
    plt.ylabel('Temperature')
    plt.title('Simulated Annealing Temperature Schedule')
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    
    plt.tight_layout()
    plt.savefig('/workspace/convergence_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()

def analyze_complexity():
    """分析算法复杂度"""
    print("\n=== 算法复杂度分析 ===")
    
    # 模拟不同规模问题的计算时间
    polygon_counts = [5, 10, 15, 20, 25, 30]
    
    # 模拟计算时间（秒）
    blf_times = [0.1 * n for n in polygon_counts]
    ga_times = [0.5 * n**1.5 for n in polygon_counts]
    sa_times = [0.3 * n**1.2 for n in polygon_counts]
    
    plt.figure(figsize=(10, 6))
    plt.plot(polygon_counts, blf_times, 'g-o', label='BLF Algorithm', linewidth=2)
    plt.plot(polygon_counts, ga_times, 'b-s', label='Genetic Algorithm', linewidth=2)
    plt.plot(polygon_counts, sa_times, 'r-^', label='Simulated Annealing', linewidth=2)
    
    plt.xlabel('Number of Polygons')
    plt.ylabel('Computation Time (seconds)')
    plt.title('Algorithm Scalability Analysis')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    
    plt.tight_layout()
    plt.savefig('/workspace/scalability_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # 打印复杂度分析
    print("时间复杂度分析:")
    print("- BLF算法: O(n²) - n为多边形数量")
    print("- 遗传算法: O(g·p·n²) - g为代数，p为种群大小")
    print("- 模拟退火: O(i·n²) - i为迭代次数")
    print("- NFP计算: O(m·n) - m,n为多边形顶点数")

def main():
    """主函数"""
    print("高级多边形Nesting算法演示")
    print("=" * 50)
    
    # 1. 高级算法演示
    results = demonstrate_advanced_algorithms()
    
    # 2. 特征提取演示
    demonstrate_feature_extraction()
    
    # 3. 收敛分析
    plot_optimization_convergence()
    
    # 4. 复杂度分析
    analyze_complexity()
    
    print(f"\n=== 演示完成 ===")
    print(f"生成的分析图片:")
    print(f"- algorithm_comparison.png: 算法性能对比")
    print(f"- convergence_analysis.png: 收敛曲线分析")
    print(f"- scalability_analysis.png: 可扩展性分析")

if __name__ == "__main__":
    main()