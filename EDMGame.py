import random
import heapq

class EdgeServer:
    def __init__(self, id, capacity):
        self.id = id  # 边缘服务器的ID
        self.capacity = capacity  # 最大处理能力
        self.current_load = 0  # 当前负载

    def is_available(self):
        """ 检查边缘服务器是否可用 """
        return self.current_load < self.capacity

    def add_request(self, request):
        """ 向服务器添加请求 """
        if self.is_available():
            self.current_load += request.intensity  # 按照请求强度增加负载
            return True
        return False

    def remove_request(self):
        """ 移除已处理的请求 """
        if self.current_load > 0:
            self.current_load -= 1  # 每次处理一个单位负载

    def process_request(self):
        """ 模拟服务器处理请求 """
        if self.current_load > 0:
            self.remove_request()  # 每次处理一个请求

    def cost(self):
        """ 计算服务器的缓解成本，这里假设是当前负载的成本 """
        return self.current_load

    def __lt__(self, other):
        """ 比较两个服务器的负载，按负载升序排列 """
        return self.current_load < other.current_load

class Request:
    def __init__(self, id, attack=False, intensity=1):
        self.id = id  # 请求ID
        self.attack = attack  # 是否为攻击请求
        self.intensity = intensity  # 攻击强度（如果是攻击请求）

    def increase_intensity(self):
        """ 增加攻击请求的强度 """
        self.intensity += 1


class EDMGame:
    def __init__(self, edge_servers, hmax, attack_requests, verbose=True):
        self.edge_servers = edge_servers
        self.hmax = hmax
        self.attack_requests = attack_requests
        self.mitigation_cost = 0
        self.extra_service_latency = 0
        self.verbose = verbose  # 控制日志输出
        self.total_processed_requests = 0  # 新增：记录处理的总请求数量

    def log(self, message):
        """ 根据日志级别输出信息 """
        if self.verbose:
            print(message)

    def allocate_requests(self):
        """ 分配攻击请求到负载最小的服务器 """
        # 获取可用服务器，并维护一个最小堆
        available_servers = [server for server in self.edge_servers if server.is_available()]
        heapq.heapify(available_servers)  # 将服务器列表转换为最小堆（按负载排序）

        # 按照攻击请求强度进行排序，优先处理强度高的请求
        self.attack_requests.sort(key=lambda x: x.intensity, reverse=True)

        # 打印分配请求的详细信息
        self.log(f"\nAllocating {len(self.attack_requests)} requests...")
        for request in self.attack_requests:
            if available_servers:
                # 从堆中取出负载最小的服务器
                min_load_server = heapq.heappop(available_servers)
                if min_load_server.add_request(request):
                    self.mitigation_cost += request.intensity  # 增加缓解成本
                    self.log(f"Request {request.id} allocated to Server {min_load_server.id} with load {min_load_server.current_load}.")
                else:
                    self.extra_service_latency += 1  # 如果没有可用服务器，增加服务延迟

                # 将更新后的服务器重新放回堆中
                heapq.heappush(available_servers, min_load_server)
            else:
                # 如果所有服务器都已满，增加额外的服务延迟
                self.extra_service_latency += 1

    def process_requests(self):
        """ 处理所有请求 """
        for server in self.edge_servers:
            if server.current_load > 0:
                self.total_processed_requests += 1  # 累计处理请求数量
                server.process_request()

    def calculate_metrics(self, num_requests, iterations):
        """ 计算吞吐率、平均延迟和负载 """
        throughput = self.total_processed_requests / iterations
        avg_latency = self.extra_service_latency / num_requests
        load = sum(server.current_load for server in self.edge_servers) / (len(self.edge_servers) * max(server.capacity for server in self.edge_servers))

        print(f"Throughput: {throughput:.2f}")
        print(f"Average Latency: {avg_latency:.2f}")
        print(f"Load: {load:.2f}")

    def find_nash_equilibrium(self):
        """ 模拟博弈过程，找到纳什均衡 """
        iteration = 0
        while iteration < 1000:
            iteration += 1
            nash_equilibrium_reached = True

            for server in self.edge_servers:
                best_cost = server.cost()
                best_request = None

                for request in self.attack_requests:
                    # 尝试分配请求
                    if server.add_request(request):
                        cost = server.cost()
                        if cost < best_cost:
                            best_cost = cost
                            best_request = request
                        # 撤销请求
                        server.remove_request()

                # 如果找到更优的分配策略，更新分配状态
                if best_request:
                    server.add_request(best_request)
                    nash_equilibrium_reached = False

            # 如果没有任何服务器更新了状态，退出循环
            if nash_equilibrium_reached:
                break

        print(f"Nash Equilibrium reached in {iteration} iterations.")


# 设置实验参数，创建服务器和请求
def setup_experiment(num_servers, hmax, num_requests, attack_ratio=0.9, max_attack_intensity=10):
    edge_servers = [EdgeServer(id=i, capacity=random.randint(3, 5)) for i in range(num_servers)]  # 降低服务器容量
    requests = []
    for i in range(num_requests):
        attack = random.random() < attack_ratio  # 增加攻击请求的比例
        intensity = random.randint(1, max_attack_intensity) if attack else 0  # 攻击请求的强度
        requests.append(Request(id=i, attack=attack, intensity=intensity))

    return edge_servers, requests


# 主函数：模拟实验
if __name__ == "__main__":
    num_servers = 10  # 边缘服务器数量
    hmax = 3  # 最大跳数限制
    num_requests = 100  # 请求数量
    iterations = 100  # 增加迭代次数

    # 设置实验
    edge_servers, attack_requests = setup_experiment(num_servers, hmax, num_requests)

    # 创建 EDMGame 实例
    edm_game = EDMGame(edge_servers, hmax, attack_requests)

    # 运行 EDMGame 算法
    edm_game.allocate_requests()
    edm_game.process_requests()

    # 输出实验结果
    print(f"Mitigation Cost: {edm_game.mitigation_cost}")
    print(f"Extra Service Latency: {edm_game.extra_service_latency}")

    # 输出纳什均衡分配结果
    edm_game.find_nash_equilibrium()

    # 计算吞吐率、平均延迟、负载
    throughput = sum(server.current_load for server in edge_servers) / iterations
    avg_latency = edm_game.extra_service_latency / num_requests
    load = sum(server.current_load for server in edge_servers) / (len(edge_servers) * max(server.capacity for server in edge_servers))

    print(f"Throughput: {throughput:.2f}")
    print(f"Average Latency: {avg_latency:.2f}")
    print(f"Load: {load:.2f}")
