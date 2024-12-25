from imports import *

# Define an initial simulated time
simulated_time_start = datetime.datetime.strptime(
    f"{random.randint(0, 23):02}:{random.randint(0, 59):02}", "%H:%M"
)

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

            if self.agent.time_elapsed >= 300:
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
                # num_civilians = 180 if keyword == "shelter" else 0
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
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.water_available = 5000  # Quantidade inicial de água disponível
        self.delivery_time = random.randint(10, 15)

    class SupplyDeliveryBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                if msg.metadata.get("performative") == "inform" and "Route updated" in msg.body:
                    print(f"[SupplyVehicleAgent] Route update notification: {msg.body}")
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

    class HandleNegotiationBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg and msg.metadata.get("performative") == "propose":
                try:
                    # Extraindo litros e minutos
                    requested_water, requested_time = map(int, msg.body.split())
                    # print(f"[SupplyVehicleAgent] Received proposal: {requested_water} liters in {requested_time} minutes.")

                    if requested_water <= self.agent.water_available and requested_time >= self.agent.delivery_time:
                        print(f"[SupplyVehicleAgent] Proposal accepted: {requested_water} liters in {requested_time} minutes.")
                        accept_msg = Message(to=str(msg.sender))
                        accept_msg.set_metadata("performative", "accept-proposal")
                        accept_msg.body = f"Accepted {requested_water} liters in {requested_time} minutes."
                        await self.send(accept_msg)
                        self.agent.water_available -= requested_water
                    else:
                        # Contra-proposta
                        counter_proposal_water = min(self.agent.water_available, requested_water + 200)
                        counter_proposal_time = random.randint(10, 15)  # Ajusta tempo de contra-proposta
                        print(f"[SupplyVehicleAgent] Counter-proposing {counter_proposal_water} liters in {counter_proposal_time} minutes.")
                        counter_msg = Message(to=str(msg.sender))
                        counter_msg.set_metadata("performative", "propose")
                        counter_msg.body = f"{counter_proposal_water} {counter_proposal_time}"
                        await self.send(counter_msg)
                except ValueError as e:
                    print(f"[SupplyVehicleAgent] Error parsing message: {msg.body}. Error: {e}")


    class HandleAcceptProposalBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg and msg.metadata.get("performative") == "accept-proposal":
                # Processar aceitação da proposta
                accepted_water = int(msg.body.split()[1])
                # print(f"[SupplyVehicleAgent] Proposal accepted for {accepted_water} liters of water.")

                # Atualizar a quantidade de água disponível
                self.agent.water_available -= accepted_water
                self.agent.delivery_destination = "shelter"  # Define o destino como o Shelter
                print(f"[SupplyVehicleAgent] Water remaining after delivery: {self.agent.water_available} liters.\n")


    async def setup(self):
        print("SupplyVehicleAgent started")

        # Comportamento de entrega
        delivery_behaviour = self.SupplyDeliveryBehav()
        delivery_template = Template()
        delivery_template.set_metadata("performative", "request")
        self.add_behaviour(delivery_behaviour, delivery_template)

        # Comportamento de negociação
        negotiation_behaviour = self.HandleNegotiationBehav()
        negotiation_template = Template()
        negotiation_template.set_metadata("performative", "propose")
        self.add_behaviour(negotiation_behaviour, negotiation_template)

        # Comportamento de aceitação da proposta
        accept_behaviour = self.HandleAcceptProposalBehav()
        accept_template = Template()
        accept_template.set_metadata("performative", "accept-proposal")
        self.add_behaviour(accept_behaviour, accept_template)
