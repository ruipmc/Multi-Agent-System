from plus.imports import *

route_graph = {
    "supply_base": [("shelter1", 10), ("shelter2", 15), ("affected_area1", 20), ("affected_area2", 25)],
    "shelter1": [("affected_area1", 5), ("affected_area3", 10)],
    "shelter2": [("affected_area2", 10), ("affected_area4", 10)],
    "affected_area1": [("supply_base", 20), ("shelter1", 5), ("affected_area3", 15)],
    "affected_area2": [("supply_base", 25), ("shelter2", 10), ("affected_area4", 20)],
    "affected_area3": [("affected_area1", 15), ("affected_area5", 10)],
    "affected_area4": [("affected_area2", 20), ("affected_area5", 10)],
    "affected_area5": [("affected_area3", 10), ("affected_area4", 10)],
}


# Define an initial simulated time
simulated_time_start = datetime.datetime.strptime(
    f"{random.randint(0, 23):02}:{random.randint(0, 59):02}", "%H:%M"
)

class ResponderAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.requests = PriorityQueue()  # Substituímos a lista por uma PriorityQueue
        self.total_requests = 0  # Número total de pedidos esperados
        self.received_requests = 0  # Contador de pedidos recebidos
        self.active_requests = True
        self.processing_times = []

    def get_priority_value(self, priority):
        valid_priorities = {
            f"{RED}HIGH{END}": 1,
            f"{YELLOW}MEDIUM{END}": 2,
            f"{GREEN}LOW{END}": 3
        }
        return valid_priorities.get(priority.strip(), 3)
    
    def get_priority_string(self, priority_value):
        # Converte valores numéricos de prioridade para strings.
        priority_map = {
            1: f"{RED}HIGH{END}",
            2: f"{YELLOW}MEDIUM{END}",
            3: f"{GREEN}LOW{END}"
        }
        return priority_map.get(priority_value, "UNKNOWN")

    class ReceiveAndQueueRequestsBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                if msg.metadata.get("performative") == "inform" and "Expected requests count" in msg.body:
                    # Atualiza o número total de pedidos esperados
                    self.agent.total_requests = int(msg.body.split(":")[-1].strip())
                    print(f"[ResponderAgent] Total requests expected: {self.agent.total_requests}")
                    self.agent.received_requests = 0

                elif msg.metadata.get("performative") == "inform" and "All requests resolved" in msg.body:
                    print("[ResponderAgent] CivilianAgent has finished generating requests.")
                    self.agent.active_requests = False
                
                elif msg.metadata.get("performative") == "request":
                    priority, request = msg.body.split(":")
                    priority_value = self.agent.get_priority_value(priority)

                    # Adiciona o pedido à fila com timestamp
                    self.agent.requests.put((priority_value, time.time(), msg.sender, request.strip()))
                    self.agent.received_requests += 1

                    if self.agent.received_requests >= self.agent.total_requests:
                        print("\n[ResponderAgent] Sorted requests by priority and time:")
                        sorted_requests = list(self.agent.requests.queue)
                        sorted_requests.sort(key=lambda x: (x[0], x[1]))  # Ordena para exibir
                        for priority_value, timestamp, sender, request in sorted_requests:
                            priority_string = self.agent.get_priority_string(priority_value)
                            print(f"Priority: {priority_string}, From: {sender}, Request: {request}")
                        print("\n")

    class ProcessRequestsBehaviour(PeriodicBehaviour):
        async def run(self):
            if not self.agent.requests.empty():
                # Processa o próximo pedido com maior prioridade e menor timestamp
                priority_value, timestamp, sender, request = self.agent.requests.get()
                print(f"[ResponderAgent] Processing request: {request}")

                if "shelter" in request.lower():
                    # Processar pedidos relacionados a shelter
                    num_civilians = int(request.split("with")[1].split("civilians")[0].strip())
                    affected_areas = ["affected_area1", "affected_area2", "affected_area3", "affected_area4", "affected_area5"]
                    affected_area = random.choice(affected_areas)           
                    print(f"[ResponderAgent] Transporting {num_civilians} civilians from {affected_area}.\n")
                    
                    # Lógica para encontrar o melhor abrigo e transportar civis
                    best_shelter, route, cost = self.find_best_shelter(affected_area, num_civilians)
                    if best_shelter:
                        for location in route[1:]:
                            await asyncio.sleep(1)
                            # print(f"[ResponderAgent] Moving to {location}.")
                        print("[ResponderAgent] Civilians delivered to shelter\n")

                        # Notifica o ShelterAgent da entrega
                        delivery_msg = Message(to="shelter@localhost")
                        delivery_msg.set_metadata("performative", "inform")
                        delivery_msg.body = f"Delivered {num_civilians} civilians to shelter.\n"
                        await self.send(delivery_msg)
                    else:
                        print("[ResponderAgent] No available shelter found for the request.")
                else:
                    # Processar pedidos de suprimentos
                    supply_msg = Message(to="supply_vehicle@localhost")
                    supply_msg.set_metadata("performative", "request")
                    supply_msg.body = request
                    await self.send(supply_msg)
                    print(f"[ResponderAgent] Request forwarded to SupplyVehicleAgent: {request}")

            if not self.agent.active_requests and self.agent.requests.empty():
                # print("[ResponderAgent] All requests resolved. Notifying Environment.")
                stop_msg = Message(to="environment@localhost")
                stop_msg.set_metadata("performative", "inform")
                stop_msg.body = "All requests resolved"
                await self.send(stop_msg)
                await self.agent.stop()

        def find_best_shelter(self, start, num_civilians):
            best_shelter = None
            best_cost = float('inf')
            best_route = []

            for shelter in ["shelter1", "shelter2"]:
                cost, route = dijkstra(route_graph, start, shelter)
                if cost < best_cost:
                    best_shelter = shelter
                    best_cost = cost
                    best_route = route

            return best_shelter, best_route, best_cost

    async def setup(self):
        print("ResponderAgent started")
        self.add_behaviour(self.ReceiveAndQueueRequestsBehaviour())
        self.add_behaviour(self.ProcessRequestsBehaviour(period=2))