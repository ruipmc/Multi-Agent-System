import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template


class ResponderAgent(Agent):
    class ResponderBehav(OneShotBehaviour):
        async def run(self):
            print("ResponderBehav running\n")

            # Listen for civilian requests
            msg = await self.receive(timeout=10)
            if msg:
                print("Responder received a request from Civilian: {}".format(msg.body))
                # Simulate providing assistance
                response_msg = Message(to="civilian@localhost")
                response_msg.set_metadata("performative", "inform")
                response_msg.body = "Assistance on the way!"
                await self.send(response_msg)
                print("Assistance response sent!\n")
            else:
                print("No requests received.")

            await self.agent.stop()

    async def setup(self):
        print("ResponderAgent started")
        b = self.ResponderBehav()
        template = Template()
        template.set_metadata("performative", "request")
        self.add_behaviour(b, template)


class CivilianAgent(Agent):
    class RequestHelpBehav(OneShotBehaviour):
        async def run(self):
            print("RequestHelpBehav running\n")
            msg = Message(to="responder@localhost")  # Change to the responder's address
            msg.set_metadata("performative", "request")  # Use a request performative
            msg.body = "I NEED HELP!"  # Customize the message
            await self.send(msg)
            print("Help request sent!\n")

            await self.agent.stop()

    async def setup(self):
        print("CivilianAgent started")
        b = self.RequestHelpBehav()
        self.add_behaviour(b)


async def main():
    # Initialize agents
    responderagent = ResponderAgent("responder@localhost", "password")
    await responderagent.start(auto_register=True)
    # print("Responder started")

    civilianagent = CivilianAgent("civilian@localhost", "password")
    await civilianagent.start(auto_register=True)
    # print("Civilian started")

    await spade.wait_until_finished(responderagent)
    print("Agents finished")


if __name__ == "__main__":
    spade.run(main())