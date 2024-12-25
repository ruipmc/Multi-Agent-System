import spade
import asyncio
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
END = '\033[0m'

class ResponderAgent(Agent):
    class ResponderCyclicBehav(CyclicBehaviour):
        async def run(self):
            print("ResponderCyclicBehav running\n")

            # Ouve por novos pedidos de ajuda
            msg = await self.receive(timeout=10)
            if msg:
                print("Request received from civilian: {}".format(msg.body))
                
                # Criar um comportamento pontual para responder ao pedido
                prioritize_help_behaviour = self.agent.PrioritizeHelpBehav(msg.body)
                self.agent.add_behaviour(prioritize_help_behaviour)
            else:
                print("No more requests received.\n")
                await self.agent.stop()


    class PrioritizeHelpBehav(OneShotBehaviour):
        def __init__(self, request_body):
            super().__init__()
            self.request_body = request_body  # Captura a mensagem recebida

        async def run(self):
            # print("PrioritizeHelpBehav running to process: {} \n".format(self.request_body))

            # Simular priorização (aqui está um exemplo simples de lógica)
            priority_level = self.prioritize_rescue(self.request_body)
            
            # Enviar uma resposta com base na priorização
            response_msg = Message(to="civilian@localhost")
            response_msg.set_metadata("performative", "inform")
            response_msg.body = f"Your request has been prioritized. Priority Level: {priority_level}. Help is on the way!"
            await self.send(response_msg)
            print(f"Priority level: {priority_level} \n")
        
        # Método fictício para definir a prioridade do resgate
        def prioritize_rescue(self, request_body):
            if "URGENT!" in request_body:
                return (f"{RED}HIGH{END}")
            elif "IMPORTANT!" in request_body:
                return (f"{YELLOW}MEDIUM{END}")
            else:
                return (f"{GREEN}LOW{END}")

    async def setup(self):
        print("ResponderAgent started")
        cyclic_behaviour = self.ResponderCyclicBehav()
        template = Template()
        template.set_metadata("performative", "request")
        self.add_behaviour(cyclic_behaviour, template)

class CivilianAgent(Agent):
    class RequestHelpBehav(OneShotBehaviour):
        async def run(self):
            print("RequestHelpOneShotBehav running\n")

            await asyncio.sleep(2)

            
            # Pedido 1: Baixa prioridade
            msg1 = Message(to="responder@localhost") 
            msg1.set_metadata("performative", "request")  
            msg1.body = "Running low on food and water, supplies needed soon."
            await self.send(msg1)
            # print("Help request sent for LOW priority.\n")
            
            await asyncio.sleep(3)

            # Pedido 2: Prioridade moderada
            msg2 = Message(to="responder@localhost") 
            msg2.set_metadata("performative", "request")  
            msg2.body = "IMPORTANT! Moderate injuries, we need transportation of civillians to shelters."
            await self.send(msg2)
            # print("Help request sent for MODERATE priority.\n")
            
            await asyncio.sleep(3)

            # Pedido 3: Prioridade crítica
            msg3 = Message(to="responder@localhost") 
            msg3.set_metadata("performative", "request")  
            msg3.body = "URGENT! Multiple injuries, collapsed building, people trapped!"
            await self.send(msg3)
            # print("Help request sent for CRITICAL priority.\n")


            await self.agent.stop()

    async def setup(self):
        print("CivilianAgent started")
        b = self.RequestHelpBehav()
        self.add_behaviour(b)

class ShelterAgent(Agent):
    class ShelterCyclicBehav(CyclicBehaviour):
        async def run(self):
            print("ShelterCyclicBehav running\n")
            
            # Ouve por mensagens dos ResponderAgents sobre civis que precisam de transporte
            msg = await self.receive(timeout=10)
            if msg:
                print(f"Message received from ResponderAgent: {msg.body}")
                
                # Caso a mensagem tenha o pedido de transporte de civis
                if "transportation of civillians to shelters" in msg.body:
                    # Criar um comportamento pontual para coordenar o transporte
                    coordinate_transport_behaviour = self.agent.CoordinateTransportBehav(msg.body)
                    self.agent.add_behaviour(coordinate_transport_behaviour)
                else:
                    print("No relevant messages for transportation coordination.\n")
            else:
                print("No new messages from responders.\n")
                await self.agent.stop()


    
    class CoordinateTransportBehav(OneShotBehaviour):
        def __init__(self, request_body):
            super().__init__()
            self.request_body = request_body  # Captura a mensagem de solicitação do ResponderAgent

        async def run(self):
            print(f"Coordinating transport for civilians based on message: {self.request_body}")
            
            # Simulação de coordenação de transporte
            transport_confirmation_msg = Message(to="responder@localhost")
            transport_confirmation_msg.set_metadata("performative", "inform")
            transport_confirmation_msg.body = f"Transport arranged for civilians based on request: {self.request_body}."
            await self.send(transport_confirmation_msg)
            print(f"Transport confirmation sent to ResponderAgent.\n")
    
    async def setup(self):
        print("ShelterAgent started")
        cyclic_behaviour = self.ShelterCyclicBehav()
        template = Template()
        template.set_metadata("performative", "request")
        self.add_behaviour(cyclic_behaviour, template)



async def main():
    # Initialize agents
    civilianagent = CivilianAgent("civilian@localhost", "password")
    await civilianagent.start(auto_register=True)
    # print("Civilian started")

    responderagent = ResponderAgent("responder@localhost", "password")
    await responderagent.start(auto_register=True)
    # print("Responder started")

    shelteragent = ShelterAgent("shelter@localhost", "password")
    await shelteragent.start(auto_register=True)

    await spade.wait_until_finished(responderagent)
    print("Agents finished.")


if __name__ == "__main__":
    spade.run(main())


#shelter a responder a pedidos e à procura de pedidos de ajuda pelo environment
#tempo simulado - para ter pedidos de ajuda ordenados
#associado a uma timeline, e a uma matriz de environment ter diferentes pedidos ao longo do tempo

# class ShelterAgent(Agent):
    
#class shelter
#ciclic e one shot behav

#shelter medico 
#comunicação entre civilian -> responder -> shelter /medico