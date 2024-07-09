# AmongAgents: Evaluating Language Models in Strategic Social Deduction Games


## Introduction
Strategic social deduction games are invaluable for testing the understanding and inference skills of language models. They offer critical insights into fields such as social science, artificial intelligence, and strategic gaming. This repository introduces AmongAgents, a text-based game environment inspired by the popular game Among Us. AmongAgents serves as a tool for studying simulated agent behavior, where language agents act as crew members aboard a spaceship. Their objective is to identify impostors sabotaging the ship and eliminating the crew.



## Setup

`conda create -n among-agents python=3.10`

`pip install -r requirements.txt`

`pip install -e .`

## Quick Start
`python main.py`

You can also try `notebooks/run_game.ipynb`

## Configs

- `include_human`(True/False): add a human player to the game
- `personality`(True/False): assign personas to agents
- `agent_config`(ALL_LLM/ALL_RANDOM/CREWMATE_LLM/IMPOSTOR_LLM): LLM agent assignments