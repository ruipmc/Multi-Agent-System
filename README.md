# Multi-Agent Disaster Response and Coordination System

## Overview

Assignment for "Introduction to Intelligent Autonomous Systems" 3rd year Artificial Intelligence and Data Science Bachelor's course.

This project simulates a multi-agent disaster response and coordination system designed to optimize the delivery of resources and evacuation efforts during emergencies. The simulation leverages SPADE to model and manage agent interactions, providing a realistic environment for studying disaster management.

## Features

1. **Multi-Agent System**: Agents representing civilians, responders, shelters, and supply vehicles interact dynamically in a simulated environment.
2. **Priority Management**: Requests for help are prioritized based on urgency, ensuring the most critical needs are addressed first.
3. **Resource Delivery**: Supply Vehicle Agents negotiate and deliver resources such as food, water, and medical supplies to affected areas and shelters.
4. **Evacuation Coordination**: Responder Agents manage the transportation of civilians from affected areas to shelters.
5. **Dynamic Route Updates**: Routes between nodes are adjusted dynamically based on simulated events such as roadblocks or accidents.

## Project Structure

- **`main.py`**: Entry point for the simulation. Initializes and starts all agents.
- **`imports.py`**: Contains common imports and dependencies.
- **`agents.py`**: Defines core agents such as Civilian, and Supply Vehicle Agents.
- **`responder.py`**: Implements the Responder Agent, which handles request prioritization and dispatching.
- **`shelter.py`**: Defines the Shelter Agent, managing resource requests and population updates.
- **`route.py`**: Provides the graph-based route system used for navigation and cost calculations.
- **`dijkstra.py`**: Implements the Dijkstra algorithm for finding the shortest path between nodes.
- **`colors.py`**: Defines color codes for terminal output for better readability.
- **`environment.py`**: Defines the Environment, which is responsible for route updates and comms.


## Requirements

- **Python** 3.9.7 or higher
- **SPADE** library

## Installation

1. Clone the repository:
   ```bash
   git clone "respository's url"
   cd "repository's name"
   ```

2. Install required dependencies:
   ```bash
   pip install spade
   ```

3. Run the simulation:
   ```bash
   python main.py
   ```

## Usage

1. **Starting the Simulation**:
   Run the `main.py` file to initialize the environment and agents.

2. **Simulated Time and Events**:
   The Environment Agent periodically updates routes and synchronizes time with other agents. Civilians generate requests based on simulated disaster scenarios.

3. **Monitoring**:
   Agents print their actions and decisions to the console, allowing you to monitor the system's performance and behavior.

## Key Components

### Environment
- Updates routes dynamically based on simulated events.
- Synchronizes simulated time across agents.

### Civilian Agent
- Generates requests for resources or evacuation.
- Adjusts request priority based on disaster intensity.

### Responder Agent
- Prioritizes and processes requests.
- Coordinates with shelters and supply vehicles to fulfill needs.

### Shelter Agent
- Manages population and resource levels.
- Requests additional supplies when thresholds are reached.

### Supply Vehicle Agent
- Delivers resources to affected areas and shelters.
- Negotiates supply terms with shelters.

## Communication Mechanisms

### Finite State Machine (FSM)
FSM is used to handle complex workflows within agents. For example, the Shelter Agent uses an FSM to manage resource negotiations with Supply Vehicle Agents, transitioning through states like proposing resources, waiting for counter-proposals, and accepting or rejecting terms.

### Periodic Behavior
Periodic behaviors allow agents to perform tasks at regular intervals. For instance, the Environment Agent periodically updates routes to simulate dynamic changes like roadblocks or new affected areas.

### Cyclic Behavior
Cyclic behaviors are used for tasks that require continuous monitoring or handling, such as the Responder Agent's ability to process incoming requests or the Civilian Agent's generation of help requests during the simulation.

## Customization

- **Route Configuration**: Modify `route.py` to add or update routes and costs.
- **Simulation Parameters**: Adjust thresholds, capacities, and probabilities in agent files to explore different scenarios.
- **Agent Behaviors**: Extend or modify behaviors to implement additional logic or features.

## Developers

- Rui Coelho, up202106772
- Nuno Moreira, up202104873
- Ricardo Ribeiro, up202104806