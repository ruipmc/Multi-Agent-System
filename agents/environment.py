from plus.imports import *


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
        update_routes_behaviour = self.UpdateRoutesBehav(period=5)
        self.add_behaviour(update_routes_behaviour)

        # Configura o comportamento para sincronizar o tempo e verificar comandos de parada
        sync_and_stop_behaviour = self.SyncTimeAndStopBehaviour()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(sync_and_stop_behaviour, template)