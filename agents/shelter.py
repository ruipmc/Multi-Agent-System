from plus.imports import *

class ShelterAgent(Agent):
    async def setup_shelter_fsm(self):
        fsm = self.SupplyRequestFSM()
        fsm.add_state(name="PROPOSE_WATER", state=self.ProposeWater(), initial=True)
        fsm.add_state(name="WAIT_FOR_COUNTER_PROPOSAL", state=self.WaitForCounterProposal())
        fsm.add_state(name="SEND_ACCEPT", state=self.SendAccept())
        fsm.add_state(name="END", state=self.EndState())  # Substituí State() por EndState()
        fsm.add_transition("PROPOSE_WATER", "WAIT_FOR_COUNTER_PROPOSAL")
        fsm.add_transition("WAIT_FOR_COUNTER_PROPOSAL", "SEND_ACCEPT")
        fsm.add_transition("SEND_ACCEPT", "END")
        fsm.add_transition("WAIT_FOR_COUNTER_PROPOSAL", "END")
        self.add_behaviour(fsm)



    # Adicionando FSM ao ShelterAgent
    class SupplyRequestFSM(FSMBehaviour):
        async def on_start(self):
            print("[ShelterAgent] Starting FSM for water request negotiation.")

        async def on_end(self):
            print("[ShelterAgent] Negotiation ended.\n")
            print(f"[ShelterAgent] Population reduced to {self.agent.current_population}/{self.agent.capacity}.\n")


    class ProposeWater(State):
        async def run(self):
            if self.agent.current_population >= self.agent.capacity * self.agent.supply_request_threshold:
                # Calcula litros necessários com base nos recém-chegados
                recent_civilians = self.agent.recent_civilians  # Civilians que acabaram de entrar
                self.agent.water_needed = recent_civilians * 2  # 2 litros por civil recém-chegado
                self.agent.requested_water = self.agent.water_needed + 200  # Adiciona margem para a proposta inicial
                print(f"[ShelterAgent] Proposing {self.agent.requested_water} liters of water in {self.agent.max_delivery_time} minutes.")

                # Envia mensagem corretamente formatada (somente números separados por espaço)
                proposal_msg = Message(to="supply_vehicle@localhost")
                proposal_msg.set_metadata("performative", "propose")
                proposal_msg.body = f"{self.agent.requested_water} {self.agent.max_delivery_time}"
                await self.send(proposal_msg)
                self.set_next_state("WAIT_FOR_COUNTER_PROPOSAL")
            else:
                print("[ShelterAgent] Supply request threshold not met. FSM will end.")
                self.set_next_state("END")

    class WaitForCounterProposal(State):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg and msg.metadata.get("performative") == "propose":
                try:
                    # Extraindo valores da contra-proposta
                    counter_proposal_water, counter_proposal_time = map(int, msg.body.split())
                    # print(f"[ShelterAgent] Counter-proposal received: {counter_proposal_water} liters in {counter_proposal_time} minutes.")

                    # Aceita a contra-proposta
                    self.agent.accepted_water = counter_proposal_water
                    self.agent.accepted_time = counter_proposal_time
                    self.set_next_state("SEND_ACCEPT")
                except ValueError as e:
                    print(f"[ShelterAgent] Error parsing counter-proposal: {msg.body}. Error: {e}")
                    self.set_next_state("END")
            else:
                # print("[ShelterAgent] No valid counter-proposal received. Ending FSM.")
                self.set_next_state("END")

    class SendAccept(State):
        async def run(self):
            print(f"[ShelterAgent] Accepting {self.agent.accepted_water} liters in {self.agent.accepted_time} minutes.")
            accept_msg = Message(to="supply_vehicle@localhost")
            accept_msg.set_metadata("performative", "accept-proposal")
            accept_msg.body = f"Accepted {self.agent.accepted_water} liters in {self.agent.accepted_time} minutes."
            await self.send(accept_msg)
            self.set_next_state("END")


    # Adicionando FSM ao SupplyVehicleAgent
    class SupplyDeliveryFSM(FSMBehaviour):
        async def on_start(self):
            print("[SupplyVehicleAgent] Starting FSM for water delivery.")

        async def on_end(self):
            print("[SupplyVehicleAgent] FSM delivery completed.")

    class RejectProposal(State):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg and msg.metadata.get("performative") == "propose":
                print(f"[SupplyVehicleAgent] Proposal received: {msg.body}")
                # Contra-proposta com base em 2 litros por civil
                num_civilians = self.agent.current_population
                counter_proposal = num_civilians * 2
                if counter_proposal <= self.agent.water_available:
                    print(f"[SupplyVehicleAgent] Counter-proposing {counter_proposal} liters of water.")
                    counter_msg = Message(to="shelter@localhost")
                    counter_msg.set_metadata("performative", "propose")
                    counter_msg.body = f"Counter-proposal: {counter_proposal} liters of water."
                    await self.send(counter_msg)
                    self.set_next_state("WAIT_FOR_ACCEPT")
                else:
                    print("[SupplyVehicleAgent] Not enough water available. Ending negotiation.")
                    self.set_next_state("END")

    class WaitForAccept(State):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg and msg.metadata.get("performative") == "accept-proposal":
                print(f"[SupplyVehicleAgent] Proposal accepted: {msg.body}. Starting delivery.")
                self.agent.water_to_deliver = int(msg.body.split()[1])  # Quantidade aceita
                self.set_next_state("DELIVER_WATER")
            else:
                print("[SupplyVehicleAgent] No acceptance received. Ending delivery process.")
                self.set_next_state("END")

    class EndState(State):
        async def run(self):
            self.set_next_state(None)  # Termina o FSM
            self.agent.current_population = int(self.agent.capacity * 0.5)
            # print(f"[ShelterAgent] Population reduced to {self.agent.current_population}/{self.agent.capacity}.\n")



    async def setup_supply_fsm(supply_agent):
        fsm = supply_agent.SupplyDeliveryFSM()
        fsm.add_state(name="REJECT_PROPOSAL", state=supply_agent.RejectProposal(), initial=True)
        fsm.add_state(name="WAIT_FOR_ACCEPT", state=supply_agent.WaitForAccept())
        fsm.add_state(name="DELIVER_WATER", state=supply_agent.DeliverWater())
        fsm.add_state(name="END", state=State())

        fsm.add_transition("REJECT_PROPOSAL", "WAIT_FOR_ACCEPT")
        fsm.add_transition("WAIT_FOR_ACCEPT", "DELIVER_WATER")
        fsm.add_transition("WAIT_FOR_ACCEPT", "END")
        fsm.add_transition("DELIVER_WATER", "END")
        supply_agent.add_behaviour(fsm)

    total_capacity_displayed = False  # Variável de classe para controlar a exibição única da capacidade total

    def __init__(self, jid, password, capacity):
        super().__init__(jid, password)
        self.capacity = capacity
        self.current_population = 0
        self.recent_civilians = 0  # Armazena o número de civilians recém-chegados
        self.supply_request_threshold = 0.8  # Percentual de ocupação para solicitar mais recursos
        self.water_needed = 0  # Inicializa o supply_available
        self.max_delivery_time = random.randint(5, 9)
        self.total_civilians_rescued = 0

    class ShelterCapacityBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                if "Delivered" in msg.body:
                        if "civilians" in msg.body:
                            # Extrai o número de civis entregues
                            num_civilians = int(msg.body.split()[1])
                            self.agent.recent_civilians = num_civilians  # Atualiza os recém-chegados
                            self.agent.current_population += num_civilians
                            self.agent.total_civilians_rescued += num_civilians
                            print(f"[ShelterAgent] Received {num_civilians} civilians. Current population: {self.agent.current_population}/{self.agent.capacity}.\n")
                            print(f"[ShelterAgent] Total of Civilians rescued {self.agent.total_civilians_rescued}.\n")

                        # Verifica se a capacidade atingiu o limite para disparar o FSM
                        if self.agent.current_population >= self.agent.capacity * self.agent.supply_request_threshold:
                            # self.agent.water_needed = self.agent.current_population * 2  # 2 litros por civil
                            await self.agent.setup_shelter_fsm()
                else:
                    print("[ShelterAgent] Message not recognized.")

    async def setup(self):
        if not ShelterAgent.total_capacity_displayed:
            print("ShelterAgent started\n")
            print(f"Total capacity of all shelters: {self.capacity} civilians\n")
            ShelterAgent.total_capacity_displayed = True
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(self.ShelterCapacityBehav(), template)
