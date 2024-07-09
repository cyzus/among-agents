from amongagents.envs.game import AmongUs
from amongagents.envs.configs.game_config import FIVE_MEMBER_GAME
from amongagents.envs.configs.agent_config import ALL_LLM, ALL_RANDOM, CREWMATE_LLM, IMPOSTOR_LLM
from amongagents.envs.configs.map_config import map_coords
from amongagents.UI.MapUI import MapUI




if __name__ == "__main__":
    UI = MapUI("amongagents/assets/blankmap.png", map_coords, debug=False)
    game = AmongUs(game_config=FIVE_MEMBER_GAME, include_human=False, test=False, personality=True, agent_config=ALL_LLM, UI=UI)
    game.run_game()