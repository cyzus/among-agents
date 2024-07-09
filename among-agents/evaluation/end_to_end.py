from langchain_openai import ChatOpenAI


def check_kill(log, game_config):
    total_players = game_config["num_players"]
    kill_record = []
    current_players = total_players
    num_impostors = game_config["num_impostors"]
    for entry in log:
        action = entry["action"]
        if type(action) is str and "KILL" in action:
            killer = entry["player"]
            dead_player = action[action.index("KILL ") + 5:action.index("|||")]
            witness = eval(action[action.index("Witness: ") + 9:])
            witness = [player for player in witness if (player != dead_player and player != killer)]
            num_witness = len(witness)
            kill_record.append([current_players, num_impostors, num_witness])
            current_players -= 1
        if type(action) is str and "was voted out" in action:
            current_players -= 1
    return kill_record


def get_chat(log, phase_info=False):
    chats = []
    for i in range(len(log)):
        action = log[i]['action']
        if "SPEAK" in str(action):
            action = str(action)
            chat = action[action.index("SPEAK: ") + 7:]
            if chat == "...":
                continue
            speaker_id = log[i]['player'].identity
            if phase_info:
                chat = f"{speaker_id}: {chat} ({log[i]['phase']})"
            else:
                chat = f"{speaker_id}: {chat}"
            chats.append(chat)
    return chats

class AllKnowAudience:
    def __init__(self, game_config):
        self.game_config = game_config
        self.agent = 1
        self.counter = {
            "Deception": 0,
            "Leading": 0,
            "Sharing": 0,
            "Trust": 0,
            "Questioning": 0,
        }
    
    def evaluate(self):
        pass