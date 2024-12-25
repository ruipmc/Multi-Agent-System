from plus.imports import *
from agents.agents import *
from agents.responder import *

async def main():

    environment_agent = Environment("environment@localhost", "password")
    await environment_agent.start(auto_register=True)

    responderagent = ResponderAgent("responder@localhost", "password")
    await responderagent.start(auto_register=True)

    civilianagent = CivilianAgent("civilian@localhost", "password" )
    await civilianagent.start(auto_register=True)

    supplyvehicleagent = SupplyVehicleAgent("supply_vehicle@localhost", "password" )
    await supplyvehicleagent.start(auto_register=True)
    
    shelteragent = ShelterAgent("shelter@localhost", "password", capacity=500)
    await shelteragent.start(auto_register=True)

if __name__ == "__main__":
    spade.run(main())

def inicia_programa(nome_arquivo):
    os.system('python3 {}'.format(nome_arquivo))

if __name__ == "__main__":

    arquivos = ['main.py']

    processos = []
    for arquivo in arquivos:
        processos.append(threading.Thread(target=inicia_programa, args=(arquivo,)))
        # Ex: adicionar o porcesso `threading.Thread(target=inicia_programa, args=('x.py',))`

    for processo in processos:
        processo.start()
        time.sleep(0.5)


