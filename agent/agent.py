from typing import Any
from envs.tools import AgentResponseOutputParser
import numpy as np
import random
import os

from langchain_openai import ChatOpenAI

from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
import re
from .prompts import *



class Agent():
    def __init__(self, player):
        self.player = player
    
    def respond(self, message):
        return "..."
    
    def choose_action(self):
        return None
        

class LLMAgent(Agent):
    def __init__(self, player, tools):
        super().__init__(player)
        if player.identity == 'Crewmate':
            system_prompt = CREWMATE_PROMPT.format(name=player.name)
            if player.personality is not None:
                system_prompt += PERSONALITY_PROMPT.format(personality=CrewmatePersonalities[player.personality])
            system_prompt += CREWMATE_EXAMPLE
        elif player.identity == 'Impostor':
            system_prompt = IMPOSTOR_PROMPT.format(name=player.name)
            if player.personality is not None:
                system_prompt += PERSONALITY_PROMPT.format(personality=ImpostorPersonalities[player.personality])
            system_prompt += IMPOSTOR_EXAMPLE
            
        chat_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=["all_info", "summarization", "memory"], template=LLM_ACTION_TEMPLATE)),
                MessagesPlaceholder(variable_name="agent_scratchpad"),

            ]
        )
            
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.tools = tools
            
        self.openai_agent = create_openai_functions_agent(llm, tools, chat_template)
        self.executor = AgentExecutor(agent=self.openai_agent, tools=tools, verbose=False)
        self.executor.name = player.name 
        self.summarization = 'no thought process has been made'
        self.processed_memory = 'no memory has been processed'
    
    def respond(self, message):
        all_info = self.player.all_info_prompt()
        prompt = f"{all_info}\n{message}"
        results = self.executor.invoke({"all_info": prompt})
        return results['output']
        
    def choose_action(self):
        available_actions = self.player.get_available_actions()
        all_info = self.player.all_info_prompt()
        phase = 'Meeting phase' if len(available_actions) == 1 else 'Task phase'
        results = self.executor.invoke({"summarization": self.summarization,
                                        "all_info": all_info,
                                        "memory": self.processed_memory,})
        
        pattern = r"^\[Condensed Memory\]((.|\n)*)\[Thinking Process\]((.|\n)*)\[Action\]((.|\n)*)$"
        match = re.search(pattern, results['output'])
        if match:
            # print(results['output'].split('|||'))
            memory = match.group(1)
            summarization = match.group(3)
            output_action = match.group(5)
            output_action = output_action.strip()
            summarization = summarization.strip()
            memory = memory.strip()
            self.summarization = summarization
            self.processed_memory = memory
        else:
            output_action = results['output']
        
        for action in available_actions:
            if repr(action) in output_action:
                return action
            elif 'SPEAK: ' in repr(action) and 'SPEAK: ' in output_action:                
                message = output_action.split('SPEAK: ')[1]
                action.message = message
                return action
        return action
    
    def choose_observation_location(self, map):
        return random.sample(map, 1)[0]



class RandomAgent(Agent):
    def __init__(self, player):
        super().__init__(player)
    
    def choose_action(self):
        available_actions = self.player.get_available_actions()
        action = np.random.choice(available_actions)
        if action.name == "speak":
            message = "Hello, I am a crewmate."
            action.provide_message(message)
        return action
    
    def choose_observation_location(self, map):
        return random.sample(map, 1)[0]

            
class HumanAgent(Agent):
    def __init__(self, player):
        super().__init__(player)
    
    def choose_action(self):
        print(f"{str(self.player)}")
        
        available_actions = self.player.get_available_actions()
        print(self.player.all_info_prompt())
        stop_triggered = False
        valid_input = False
        while (not stop_triggered) and (not valid_input):
            print("Choose an action:")
            try:
                action_idx = int(input())
                if action_idx == 0:
                    stop_triggered = True
                elif action_idx < 1 or action_idx > len(available_actions):
                    raise ValueError(f"Invalid input. Please enter a number between 1 and {len(available_actions)}.")
                else:
                    valid_input = True
                   
            except:
                print("Invalid input. Please enter a number.")
                continue
        if stop_triggered:
            raise ValueError("Game stopped by user.")
        action = available_actions[action_idx-1]
        if action.name == "SPEAK":
            message = self.speak()
            action.provide_message(message)
        if action.name == "SPEAK":
            action.provide_message(message)
        return action
    
    def respond(self, message):
        print(message)
        response = input()
        return response
    
    def speak(self):
        print("Enter your response:")
        message = input()
        return message
    
    def choose_observation_location(self, map):
        map = list(map)
        print("Please select the room you wish to observe:")
        for i, room in enumerate(map):
            print(f"{i}: " + room)
        while True:
            index = int(input())
            if index < 0 or index >= len(map):
                print(f"Invalid input. Please enter a number between 0 and {len(map) - 1}.")
            else:
                print(map)
                print('index', index)
                print('map[index]', map[index])
                return map[index]

class LLMHumanAgent(HumanAgent, LLMAgent):
    def __init__(self, player):
        super(LLMHumanAgent, self).__init__(player)
    
    def choose_action(self):
        return HumanAgent.choose_action(self)
    
    def respond(self, message):
        return LLMAgent.respond(self, message)
