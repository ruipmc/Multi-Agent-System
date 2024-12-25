from imports import *

#SFM - contract net com o shelter e supply agent, pedir 1000 litros de agua, rejeitar e negociar 500 litros em 15 minutos
                                                                                # 700 litros em 30 minutos 
                                                                                # ou outra opção - contract net

# Define an initial simulated time
simulated_time_start = datetime.datetime.strptime(
    f"{random.randint(0, 23):02}:{random.randint(0, 59):02}", "%H:%M"
)


class Environment(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.simulated_time = None
        self.stop_notifications = False  # Controle para parar notificações e comportamentos

    class UpdateRoutesBehav(PeriodicBehaviour):
        async def run(self):
            if self.agent.stop_notifications:
                print("[Environment] All requests resolved. Stopping route updates.")
                self.kill()  # Encerra o comportamento
                return

            if not self.agent.simulated_time:
                return  # Aguarda até que o tempo simulado seja definido pelo CivilianAgent

            # Escolha um evento para ocorrer no tempo simulado do Environment
            node = random.choice(list(route_graph.keys()))
            if route_graph[node]:
                connection = random.choice(route_graph[node])
                current_cost = connection[1]
                new_cost = current_cost + random.randint(5, 15)
                cause = random.choice(["roadblock", "accident", "new infected area"])

                updated_connections = [(n, new_cost if n == connection[0] else cost) for n, cost in route_graph[node]]
                route_graph[node] = updated_connections

                print(f"[{self.agent.simulated_time}] [Environment] Route cost from {node} to {connection[0]} increased due to {cause}. New cost: {new_cost}\n")

    class SyncTimeAndStopBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                if "Simulated time" in msg.body:
                    time_str = msg.body.split(": ")[1]
                    self.agent.simulated_time = time_str
                    # print(f"[Environment] Updated simulated time to: {self.agent.simulated_time}")
                elif "All requests resolved" in msg.body:
                    print("[Environment] Received stop command. Stopping all notifications.")
                    self.agent.stop_notifications = True

    async def setup(self):
        print("Environment initialized")

        # Configura o comportamento para atualizar as rotas periodicamente
        update_routes_behaviour = self.UpdateRoutesBehav(period=10)
        self.add_behaviour(update_routes_behaviour)

        # Configura o comportamento para sincronizar o tempo e verificar comandos de parada
        sync_and_stop_behaviour = self.SyncTimeAndStopBehaviour()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(sync_and_stop_behaviour, template)

class CivilianAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.time_elapsed = 0  # Contador de ciclos ou minutos
        self.active = True  # Controle para saber se o agente ainda está gerando pedidos

    class PeriodicRequestHelpBehav(PeriodicBehaviour):
        async def run(self):
            if not self.agent.active:
                # Envia mensagem para o ResponderAgent notificando que todos os pedidos foram gerados
                final_msg = Message(to="responder@localhost")
                final_msg.set_metadata("performative", "inform")
                final_msg.body = "All requests resolved"
                await self.send(final_msg)

                print("[CivilianAgent] Notified ResponderAgent that all requests are resolved. Stopping agent.")
                self.kill()  # Termina o comportamento
                return

            # Ajuste da probabilidade e quantidade de pedidos ao longo do tempo
            if self.agent.time_elapsed < 60:
                priority_distribution = [0.6, 0.3, 0.1]
                num_requests = random.randint(3, 7)
            elif 10 <= self.agent.time_elapsed < 180:
                priority_distribution = [0.3, 0.5, 0.2]
                num_requests = random.randint(2, 5)
            elif 20 <= self.agent.time_elapsed < 240:
                priority_distribution = [0.0, 0.6, 0.4]
                num_requests = random.randint(1, 3)
            else:
                priority_distribution = [0.0, 0.15, 0.85]
                num_requests = random.randint(1,2)

            if self.agent.time_elapsed >= 100:
                print("[CivilianAgent] Stoping requests generation...\n")
                self.agent.active = False  # Define que o agente terminou de gerar pedidos
                return

            # Envia o número de requests planejados para o ResponderAgent
            count_msg = Message(to="responder@localhost")
            count_msg.set_metadata("performative", "inform")
            count_msg.body = f"Expected requests count: {num_requests}"
            await self.send(count_msg)

            # Incremento do tempo simulado
            simulated_time = simulated_time_start + datetime.timedelta(minutes=self.agent.time_elapsed)
            self.agent.time_elapsed += 30  # Ajuste o incremento conforme necessário

            # Envia o tempo simulado para o Environment para sincronização
            time_msg = Message(to="environment@localhost")
            time_msg.set_metadata("performative", "inform")
            time_msg.body = f"Simulated time: {simulated_time.strftime('%H:%M')}"
            await self.send(time_msg)

            # Envia os pedidos de ajuda
            priorities = [f"{RED}HIGH{END}", f"{YELLOW}MEDIUM{END}", f"{GREEN}LOW{END}"]
            keywords = ["food and water", "medical supplies", "shelter"]
            
            for i in range(num_requests):
                if i == 0:
                    print(f"\n\n[{simulated_time.strftime('%H:%M')}]\n")
                priority = random.choices(priorities, weights=priority_distribution, k=1)[0]
                keyword = random.choice(keywords)
                num_civilians = random.randint(80, 120) if keyword == "shelter" else 0

                if keyword == "shelter":
                    print(f"[{simulated_time.strftime('%H:%M')}] [CivilianAgent] HELP! Request with priority {priority} for {keyword} involving {num_civilians} civilians.")
                    msg_body = f"{priority}:Requesting {keyword} in the affected area with {num_civilians} civilians."
                else:
                    print(f"[{simulated_time.strftime('%H:%M')}] [CivilianAgent] HELP! Request with priority {priority} for {keyword}.")
                    msg_body = f"{priority}:Requesting {keyword} in the affected area."

                msg = Message(to="responder@localhost")
                msg.set_metadata("performative", "request")
                msg.body = msg_body
                await self.send(msg)
                print(f"[{simulated_time.strftime('%H:%M')}] [CivilianAgent] Help request sent.\n")

    async def setup(self):
        print("CivilianAgent started")
        periodic_request_behaviour = self.PeriodicRequestHelpBehav(period=5, start_at=datetime.datetime.now() + datetime.timedelta(seconds=2))
        self.add_behaviour(periodic_request_behaviour)

class SupplyVehicleAgent(Agent):
    class SupplyDeliveryBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                if msg.metadata.get("performative") == "inform" and "Route updated" in msg.body:
                    print(f"[SupplyVehicleAgent] Route update notification: {msg.body}")
                    # Processa a atualização de rota recebida (simples notificação neste caso)
                else:
                    print(f"[SupplyVehicleAgent] Delivery request received for: {msg.body}")
                    destination = msg.body
                    start_location = "supply_base"
                    cost, route = dijkstra(route_graph, start_location, destination)
                    
                    if route:
                        print(f"[SupplyVehicleAgent] Optimized route to {destination}: {route} with cost {cost}")
                        
                        for location in route[1:]:
                            new_cost, new_route = dijkstra(route_graph, location, destination)
                            if new_cost < cost:
                                route = new_route
                                cost = new_cost
                                print(f"[SupplyVehicleAgent] Route updated dynamically to {route} with new cost {cost}")
                            
                            await asyncio.sleep(2)
                            print(f"[SupplyVehicleAgent] Arrived at {location}")
                    
                    delivery_confirmation = Message(to="responder@localhost")
                    delivery_confirmation.set_metadata("performative", "inform")
                    delivery_confirmation.body = f"Supplies delivered to {destination}."
                    await self.send(delivery_confirmation)
                    print(f"[SupplyVehicleAgent] Delivery confirmation sent to ResponderAgent.\n")

    async def setup(self):
        print("SupplyVehicleAgent started")
        cyclic_behaviour = self.SupplyDeliveryBehav()
        template = Template()
        template.set_metadata("performative", "request")
        self.add_behaviour(cyclic_behaviour, template)

        # Template para notificações de atualizações de rota
        template_notification = Template()
        template_notification.set_metadata("performative", "inform")
        self.add_behaviour(self.SupplyDeliveryBehav(), template_notification)


class ShelterAgent(Agent):
    total_capacity_displayed = False  # Variável de classe para controlar a exibição única da capacidade total

    def __init__(self, jid, password, capacity):
        super().__init__(jid, password)
        self.capacity = capacity
        self.current_population = 0
        self.supply_request_threshold = 0.8  # Percentual de ocupação para solicitar mais recursos
        self.min_supply_level = 20  # Nível mínimo de suprimentos para que o abrigo funcione adequadamente

    class ShelterCapacityBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                # print(f"[ShelterAgent] Message received: {msg.body}")
                if "Delivered" in msg.body:
                    # Extrai o número de civis entregues
                    num_civilians = int(msg.body.split()[1])
                    self.agent.current_population += num_civilians

                    # Atualiza a capacidade no terminal
                    print(f"[ShelterAgent] Current population: {self.agent.current_population}/{self.agent.capacity}\n")
                    if self.agent.current_population >= self.agent.capacity:
                        print("[ShelterAgent] Warning: Shelter is at full capacity!")
                else:
                    print("[ShelterAgent] Message not recognized.")

    async def setup(self):
        if not ShelterAgent.total_capacity_displayed:
            print("ShelterAgent started\n")
            print(f"Total capacity of all shelters: {self.capacity} civilians\n")
            ShelterAgent.total_capacity_displayed = True
            template = Template()
            template.set_metadata("performative", "inform")
            shelter_capacity_behaviour = self.ShelterCapacityBehav()
            self.add_behaviour(shelter_capacity_behaviour, template)


                #     # Verifica se a ocupação atual exige mais recursos
                #     if self.agent.current_population >= self.agent.capacity * self.agent.supply_request_threshold:
                #         # Calcula a quantidade de recursos adicionais necessários
                #         additional_resources_needed = max(0, self.agent.capacity - self.agent.current_population)
                        
                #         resource_request = Message(to="supply_vehicle@localhost")
                #         resource_request.set_metadata("performative", "request")
                #         resource_request.body = f"Requesting additional shelter resources for {additional_resources_needed} civilians due to high occupancy."
                #         await self.send(resource_request)
                #         print(f"[ShelterAgent] Resource request sent to SupplyVehicleAgent due to high occupancy at shelter.\n")
                    
                # else:
                #     print("[ShelterAgent] Shelter capacity exceeded, cannot accommodate more civilians.")