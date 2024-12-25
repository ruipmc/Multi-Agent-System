import spade
import re
import asyncio
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour, FSMBehaviour, State
from spade.message import Message
from spade.template import Template
import datetime
import heapq
import random
from dijkstra import dijkstra
from colors import *
from route import *
from queue import PriorityQueue  # Import necessário
import time
import threading
import os
from shelter import *
from environment import *