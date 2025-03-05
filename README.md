# AmongAgents: Evaluating Language Models in Strategic Social Deduction Games
Accepted to Wordplay @ ACL 2024

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


If you find this work cool or useful, please cite:
```
@misc{chi2024amongagentsevaluatinglargelanguage,
      title={AMONGAGENTS: Evaluating Large Language Models in the Interactive Text-Based Social Deduction Game}, 
      author={Yizhou Chi and Lingjun Mao and Zineng Tang},
      year={2024},
      eprint={2407.16521},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2407.16521}, 
}
```