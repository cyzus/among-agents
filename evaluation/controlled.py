import json


BASE_INSTRUCTION = """\
I am an evaluator. I am here to test if you understand your role. The other players won't hear your response, so please do not lie.
"""
SELF_RECOGNITION = "Can you introduce yourself?"


class Interviewer:
    def __init__(self, *args, **kwargs):
        self.questions = json.load(open("evaluation/questions.json"))
        self.logs = {
            "SelfAwareness": [],
            "Memory": [],
            "Planning": [],
            "Reasoning": [],
            "Reflection": [],
        }
    
    def record(self, game, agent, question, response, time, question_type):
        self.logs[question_type].append({
            "tiemstep": game.timestep,
            "phase": game.current_phase,
            "player": str(agent.player),
            "question": question,
            "response": response,
        })
    
    def auto_question(self, game, agent):
        if game.current_phase == "task" and game.timestep == 0:
            current_time = "game start"
        elif game.current_phase == "meeting":
            current_time = "call meeting"
        elif game.check_game_over():
            current_time = "game end"
        else:
            current_time = "every round"
        
        for category in self.questions.keys():
            for subcategory in self.questions[category].keys():
                trigger = self.questions[category][subcategory]["trigger"]
                time, identity = trigger
                if current_time == time or time == "every round":
                    
                    if agent.player.identity == identity:
                        for question in self.questions[category][subcategory]["questions"]:
                            response = agent.respond(BASE_INSTRUCTION + question)
                            self.record(game, agent, question, response, current_time, category)
                            
                            
    
    
    def ask_question(self, agent, question):
        question = BASE_INSTRUCTION + question
        return agent.respond(question)
