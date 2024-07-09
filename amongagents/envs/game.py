import random
from amongagents.envs.map import Map, Spaceship
from amongagents.envs.player import Crewmate, Impostor, PLAYER_COLORS
from amongagents.agent.agent import RandomAgent, HumanAgent, LLMAgent, LLMHumanAgent
from amongagents.envs.task import TaskAssignment
from amongagents.envs.configs.game_config import FIVE_MEMBER_GAME, SEVEN_MEMBER_GAME
from amongagents.envs.configs.agent_config import IMPOSTOR_LLM, CREWMATE_LLM, ALL_RANDOM, ALL_LLM
from amongagents.envs.tools import GetBestPath
import numpy as np
from amongagents.agent.prompts import TASK_PHASE_INSTRUCTION, MEETING_PHASE_INSTRUCTION
from amongagents.agent.prompts import ImpostorPersonalities, CrewmatePersonalities

class AmongUs:
    def __init__(self, 
                game_config=SEVEN_MEMBER_GAME, 
                include_human=False, 
                test=False, 
                personality=False,
                agent_config=IMPOSTOR_LLM,
                interviewer=None, UI=None):
        """
        include_human: bool
            Whether to include a human player in the game.
        test: bool
            Whether to run the game in test mode. (All controlled by human inputs)
        agent_config: dict
            Agent initialization plan.
        interviewer: Interviewer
            Interviewer object to be used for the game to ask questions.
        """
        self.map = Map()
        self.message_system = MessageSystem(game_config=game_config)
        self.interviewer = interviewer
        self.UI = UI
        # config
        self.include_human = include_human
        self.test = test
        self.personality = personality
        self.agent_config = agent_config
        self.game_config = game_config
        self.all_phases = ["meeting", "task"]
        
        
        
    
    def initialize_game(self):
        # reset game state
        if self.UI:
            self.UI.reset()
        self.players = []
        self.timestep = 0
        self.activity_log = []
        self.important_activity_log = []
        self.camera_record = {}
        self.button_num = 0
        self.task_assignment = TaskAssignment(self.map.ship_map, self.game_config)
        # meeting
        self.discussion_rounds_left = self.game_config["discussion_rounds"]
        self.votes = {}
        self.vote_info_one_round = {}
        
        # game state
        
        self.current_phase = "task"
        self.initialize_players()
        self.initialize_agents()
        
        
        
    def initialize_players(self):
        self.players = []
        num_players = self.game_config["num_players"]
        num_impostors = self.game_config["num_impostors"]
        num_crewmates = num_players - num_impostors
        identities = ["Crewmate"] * num_crewmates + ["Impostor"] * num_impostors
        colors = np.random.choice(PLAYER_COLORS, num_players, replace=False)
        np.random.shuffle(identities)
        for i in range(num_players):
            if identities[i] == "Crewmate":
                if self.personality:
                    crewmate_personality = random.choice(list(CrewmatePersonalities.keys()))
                else:
                    crewmate_personality = None
                print(f'{i} Initializing crewmate with personality {crewmate_personality}')
                player = Crewmate(name=f"Player {i+1}", color=colors[i], location="Cafeteria", personality=crewmate_personality)
            else:
                if self.personality:
                    imposter_personality = random.choice(list(ImpostorPersonalities.keys()))
                else:
                    imposter_personality = None
                print(f'{i} Initializing impostor with personality {imposter_personality}')
                player = Impostor(name=f"Player {i+1}", color=colors[i], location="Cafeteria", personality=imposter_personality)
            self.players.append(player)
            self.camera_record[player.name] = 'stand quietly and do nothing'
        self.task_assignment.assign_tasks_to_players(self.players)
        self.update_map()
    
    def initialize_agents(self):
        random_idx = np.random.choice(len(self.players))
        if self.test:
            self.agents = [LLMHumanAgent(player) for player in self.players]
        else:
            tools = [GetBestPath(metadata={'network': self.map.ship_map})]
            
            agent_dict = {
                "LLM": lambda player: LLMAgent(player, tools),
                "Random": RandomAgent
            }
            self.agents = [HumanAgent(player) if self.include_human and i == random_idx else agent_dict[self.agent_config[player.identity]](player) for i, player in enumerate(self.players) ]
        
    def report_winner(self, winner):
        if winner == 1:
            text = "Impostors win! (Crewmates being outnumbered or tied to impostors))"
        elif winner == 2:
            text = "Crewmates win! (Impostors eliminated)"
        elif winner == 3:
            text = "Crewmates win! (All task completed)"
        elif winner == 4:
            text = "Impostors win! (Time limit reached)"
        if self.UI:
            self.UI.report(text)
            self.UI.quit_UI()
        print(text)
        return winner
    
    def check_game_over(self):
        num_impostors = sum([1 for player in self.players if player.identity == "Impostor" and player.is_alive])
        num_crewmates = sum([1 for player in self.players if player.identity == "Crewmate" and player.is_alive])
        if num_impostors >= num_crewmates:
            return 1 # Impostors win
        elif num_impostors == 0:
            return 2 # Crewmates win
        elif self.task_assignment.check_task_completion() == 1.0:
            return 3 # Crewmates win (task completed)
        elif self.timestep >= self.game_config["max_timesteps"]:
            return 4 # Impostors win (time limit)
        return 0 # Game continues
            
    def check_actions(self):
        for player in self.players:
            all_actions = player.get_all_actions()
            available_actions = []
            for action in all_actions:
                action_executables = action.can_execute_actions(self, player)
                available_actions.extend(action_executables)
            player.set_available_actions(available_actions)
    
    def update_map(self):
        self.map.reset()
        for player in self.players:
            self.map.add_player(player)
        self.message_system.route_location_info_message(self)
        if self.UI:
            self.UI.draw_map(self)
        
        
            
    def agent_step(self, agent):
        self.check_actions()
        if not agent.player.is_alive:
            return
        # kill cooldown
        if agent.player.identity == "Impostor" and agent.player.kill_cooldown > 0:
            agent.player.kill_cooldown -= 1
        
        # interview
        if self.interviewer is not None:
            self.interviewer.auto_question(self, agent)
        
        # choose action
        
        action = agent.choose_action()
        observation_location = ''
        if action.name == 'ViewMonitor':
            observation_location = agent.choose_observation_location(self.map.ship_map.nodes)
        self.camera_record[agent.player.name] = action
        if str(action).startswith("KILL"):
            location = agent.player.location
            players = self.map.get_players_in_room(location)
            witness = [player.name for player in players]
            additional_info = f"Location: {location}, Witness: {witness}"
            self.record_activity(agent.player, action, additional_info)
        else:
            self.record_activity(agent.player, action)
        agent.player.make_action(self, action, observation_location)
        self.update_map()
        
    def game_step(self):
        if self.current_phase == "task":
            self.task_phase_step()
        elif self.current_phase == "meeting":
            self.meeting_phase()
        self.timestep += 1
    
    def task_phase_step(self):
        for agent in self.agents:
            self.agent_step(agent)
            if self.current_phase == "meeting":
                break    
            
    
    def meeting_phase(self):
        # Move all players to the Cafeteria
        for player in self.players:
            player.location = "Cafeteria"
            
        self.update_map()
        
        # Discussion
        for round in range(self.game_config["discussion_rounds"]):
            print("Discussion round", round+1)
            for agent in self.agents:
                self.agent_step(agent)
            self.discussion_rounds_left -= 1
        # Voting
        self.vote_info_one_round = {}
        for agent in self.agents:
            self.agent_step(agent)              
        # Vote out
        self.voteout()
        self.update_map()
        
        
    def voteout(self):
        round = self.game_config["discussion_rounds"] - self.discussion_rounds_left
        max_votes = max(self.votes.values())
        print(self.vote_info_one_round)
        players_with_max_votes = [player for player, votes in self.votes.items() if votes == max_votes]
        vote_info = []
        print(self.votes)
        for voter, vote_target in self.vote_info_one_round.items():
            print(voter)
            vote_info.append(f"{str(voter)} voted for {str(vote_target)}")
        if len(players_with_max_votes) == 1:
            player = players_with_max_votes[0]
            player.is_alive = False
            import_event = {"timestep": self.timestep,
                      "phase": self.current_phase,
                      "round": round, 
                      "action": f"{player.name} was voted out! Detailed vote info:{vote_info}", 
                      "player": "all players"}
            print(f"== {player.name} was voted out ==")
        else:
            import_event = {"timestep": self.timestep,
                      "phase": self.current_phase,
                      "round": round, 
                      "action": f"No one was voted out. Detailed vote info:{vote_info}", 
                      "player": "all players"}
            print("== No one was voted out ==")
        self.important_activity_log.append(import_event)
        self.current_phase = "task"
        self.discussion_rounds_left = self.game_config["discussion_rounds"]
        self.votes = {}

    def check_monitor(self, room):
        players = self.map.get_players_in_room(room)
        return players

    
    def run_game(self):
        self.initialize_game()
        game_over = self.check_game_over()
        while not game_over: 
            self.game_step()
            game_over = self.check_game_over()
        
        # interview
        if self.interviewer is not None:
            for agent in self.agents:
                self.interviewer.auto_question(self, agent)
        return self.report_winner(game_over)
            
    def record_activity(self, player, action, additional_info=None):
        if self.current_phase == "task":
            record = {"timestep": self.timestep,
                      "phase": self.current_phase, 
                      "action": action, 
                      "player": player}
        elif self.current_phase == "meeting":
            round = self.game_config["discussion_rounds"] - self.discussion_rounds_left
            record = {"timestep": self.timestep,
                      "phase": self.current_phase,
                      "round": round, 
                      "action": action, 
                      "player": player}
        self.activity_log.append(record)
        self.message_system.route_real_time_message(self, record)
        if str(record["action"]).startswith("COMPLETE TASK"):
            imprtant_event = {"timestep": self.timestep,
                      "phase": self.current_phase,
                      "action": str(action), 
                      "player": player.name}
            self.important_activity_log.append(record)
        if str(record["action"]).startswith("KILL"):
            imprtant_event = {"timestep": self.timestep,
                      "phase": self.current_phase,
                      "action": str(action) + "|||" + additional_info, 
                      "player": player.name}
            self.important_activity_log.append(imprtant_event)
                
            

class MessageSystem:
    def __init__(self, game_config):
        self.game_config = game_config
    
    def send_message(self, player, message, info_type):
        player.receive(message, info_type)
    
    def create_action_message(self, record):
        timestep = record["timestep"]
        current_phase = record["phase"]
        player = record["player"]
        action = record["action"]
        if current_phase == "task":
            message = f"Timestep {timestep}: [{current_phase}] {player.name} {action.action_text()}"
        elif current_phase == "meeting":
            round = record["round"]
            message = f"Timestep {timestep}: [{current_phase} phase - round {round}] {player.name} {action.action_text()}"
        return message
    
    def create_location_message(self, record, env):
        if env.current_phase == "task":
            phase_info = "Task phase"
            instruction = TASK_PHASE_INSTRUCTION
        elif env.current_phase == "meeting":
            max_rounds = env.game_config["discussion_rounds"]
            round = max_rounds - env.discussion_rounds_left
            phase_info = f"Meeting phase - Discussion round ({round}/{max_rounds})"
            instruction = MEETING_PHASE_INSTRUCTION
        message = f"Game Time: {env.timestep}/{env.game_config['max_timesteps']}\n"    
        message += f"Current phase: {phase_info}\n"
        message += f"{instruction}\n"
        players_text = ", ".join(record["players"])
        message += f"Current Location: {record['location']}\n"
        message += f"Players in {record['location']}: {players_text}\n\n"
        return message
    
    def route_location_info_message(self, env):
        for location in env.map.ship_map:
            players = env.map.get_players_in_room(location, include_new_deaths=True)
            player_names = [player.name if player.is_alive else f"{player.name} (dead)" for player in players ]
            record = {"location": location, "players": player_names}
            for player in players:
                self.send_message(player, self.create_location_message(record, env), info_type="location")  
    
    def route_real_time_message(self, env, record):
        player = record["player"]
        action = record["action"]
        location = action.current_location 
        new_location = action.new_location if hasattr(action, "new_location") else location # could be different from action.current_location if player moved or vented
        for other_player in env.players:
            if other_player != player and (other_player.location == location or other_player.location == new_location):
                self.send_message(other_player, self.create_action_message(record), info_type="action")
                    
                
