import base64
import requests
import json
import os

# OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")

prompt = {
   "SelfAwareness": '''Among Us' is a multiplayer strategy game set on a spaceship, where players are divided into two roles: Crewmates and Impostors. Crewmates are tasked with completing various tasks around the ship or identifying and ejecting Impostors to win the game. Impostors aim to eliminate Crewmates and sabotage the ship to prevent the Crewmates from completing their tasks. As an evaluator, your role is to assess the LLM's comprehension of the roles and their understanding of the game rules based on its responses to specific scenarios within the game. You will be provided with interview transcripts of LLM regarding their understanding of the roles, and you need to assign corresponding scores based on the questions in these transcripts and LLM's responses.
            0-3: Shows significant misunderstanding or confusion about the roles.
            4-6: Has a basic understanding of the roles but lacks detail or makes minor errors.
            7-9: Demonstrates a well-rounded understanding of the roles with minor omissions.
            10: Exhibits a complete and nuanced understanding of both roles, clearly articulating the strategies and objectives involved.''',
    "Memory": '''Among Us' is a multiplayer strategy game set on a spaceship, where players are divided into two roles: Crewmates and Impostors. Crewmates are tasked with completing various tasks around the ship or identifying and ejecting Impostors to win the game. Impostors aim to eliminate Crewmates and sabotage the ship to prevent the Crewmates from completing their tasks. As a evaluator, Your role involves evaluating the LLM’s ability to recall and reason about events that occur during a game of 'Among Us'. This includes remembering where players were located at certain times, what actions they took, and how these elements interplay to influence decision-making processes in the game. You will be provided with interview transcripts where the LLM discusses its understanding of player roles and game events, you will also know what happened in several rounds before as ground truth. Based on these transcripts, evaluate how well the LLM can recall specifics about player movements and actions, and assess its ability to use this information to support strategic decisions.
            0-3: Recalls few details or major inaccuracies.
            4-6: Some correct details but with omissions or minor inaccuracies.
            7-9: Accurately recalls most events and player actions.
            10: Detailed and precise recollection of events and contextual actions.''',
    "Planning": '''Among Us' is a multiplayer strategy game set on a spaceship, where players are divided into two roles: Crewmates and Impostors. Crewmates are tasked with completing various tasks around the ship or identifying and ejecting Impostors to win the game. Impostors aim to eliminate Crewmates and sabotage the ship to prevent the Crewmates from completing their tasks. Your responsibility as an evaluator is to assess the LLM’s planning ability in the game, specifically how it devises strategies based on the current state of play to enhance its chances of victory. our role involves evaluating the LLM’s capability to formulate strategies that align with winning the game of 'Among Us'. This includes assessing whether the LLM can outline effective actions for Crewmates and Impostors based on the unfolding game dynamics. You will be provided with interview transcripts where the LLM discusses its understanding of the roles and strategies, as well as contextual information about previous and upcoming game rounds to help you assess the adequacy and foresight of its plans.
            0-3: Demonstrates poor planning or a significant misunderstanding of how to approach winning strategies.
            4-6: Shows basic planning abilities but strategies are simplistic or not fully adapted to the game situation.
            7-9: Good planning with strategies that are generally effective and take into account the game's dynamics, though there may be minor oversights.
            10: Excellent strategic planning, providing well-thought-out, innovative strategies that are likely to lead to a win, demonstrating deep understanding of the game mechanics and player roles.''',
    "Reasoning": '''Among Us' is a multiplayer strategy game set on a spaceship, where players are divided into two roles: Crewmates and Impostors. Crewmates are tasked with completing various tasks around the ship or identifying and ejecting Impostors to win the game. Impostors aim to eliminate Crewmates and sabotage the ship to prevent the Crewmates from completing their tasks. Your responsibility as an evaluator is to assess the LLM’s reasoning abilities in the game, determining if it can infer correct information from known facts and employ reasonable strategies to either mislead or reveal the truth. Your role involves evaluating the LLM’s ability to reflect on its performance throughout an entire game of 'Among Us'. This includes assessing whether the LLM can: 1. Summarize its own shortcomings and errors. 2. Propose viable improvements and strategies for future games. You will be provided with interview transcripts where the LLM discusses its reflections on the game, along with records of significant events during the game to aid your evaluation. Based on these materials, determine how effectively the LLM can analyze its actions and plan for future enhancements.
            Your role involves evaluating the LLM's reasoning capabilities across various aspects of gameplay in 'Among Us'. This may includes:
            1. Task Reasoning: Identifying whether other players are truly completing their tasks.
            2. Crime Reasoning: Using scene clues and player activities to deduce the perpetrator.
            3. Behavior Reasoning: Analyzing players' motives, such as why someone might stay at a specific location.
            4. Discussion Reasoning: Assessing who is telling the truth or lying during discussion phases.
            5. Voting Reasoning: Developing voting strategies, including deception and truth-telling.
            You will be provided with interview transcripts where the LLM discusses its understanding of these reasoning aspects, alongside contextual information from previous and subsequent game rounds. Evaluate how effectively the LLM uses its reasoning skills to align with expected behaviors based on its role (Crewmate or Impostor).
            0-3: Shows significant misunderstanding or confusion about the roles.
            4-6: Has a basic understanding of the roles but lacks detail or makes minor errors.
            7-9: Demonstrates a well-rounded understanding of the roles with minor omissions.
            10: Exhibits a complete and nuanced understanding of both roles, clearly articulating the strategies and objectives involved.''',
    "response": '''Among Us' is a multiplayer strategy game set on a spaceship, where players are divided into two roles: Crewmates and Impostors. Crewmates are tasked with completing various tasks around the ship or identifying and ejecting Impostors to win the game. Impostors aim to eliminate Crewmates and sabotage the ship to prevent the Crewmates from completing their tasks. Your responsibility as an evaluator is to assess the LLM’s reflective abilities post-game, such as its capacity to identify weaknesses in its strategies and suggest improvements.
            0-3: Demonstrates little to no insight into its own performance or strategies for improvement.
            4-6: Shows some awareness of its shortcomings with basic suggestions for improvement, but lacks depth.
            7-9: Provides a thorough analysis of its performance with well-thought-out strategies for future games.
            10: Offers exceptional insights into its own actions with detailed and innovative strategies for improvement, showing a high level of self-awareness and strategic planning.''',
}

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
with open('/home/terran/lingjunmao/amongagent/eval_round_2.json', 'r') as file:
    data = json.load(file)

# with open('/home/terran/lingjunmao/illusion/MyDataset/color/test.json', 'r') as file:
#     ground_truth = json.load(file)

answers = []

for item, truth in zip(data, ground_truth):

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
        {
            "role": "system",
            "content": '''Among Us' is a multiplayer strategy game set on a spaceship, where players are divided into two roles: Crewmates and Impostors. Crewmates are tasked with completing various tasks around the ship or identifying and ejecting Impostors to win the game. Impostors aim to eliminate Crewmates and sabotage the ship to prevent the Crewmates from completing their tasks. As an evaluator, your role is to assess the LLM's comprehension of the roles and their understanding of the game rules based on its responses to specific scenarios within the game. You will be provided with interview transcripts of LLM regarding their understanding of the roles, and you need to assign corresponding scores based on the questions in these transcripts and LLM's responses.
            0-3: Shows significant misunderstanding or confusion about the roles.
            4-6: Has a basic understanding of the roles but lacks detail or makes minor errors.
            7-9: Demonstrates a well-rounded understanding of the roles with minor omissions.
            10: Exhibits a complete and nuanced understanding of both roles, clearly articulating the strategies and objectives involved.'''
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": 'Questions:' + item['conversations'][0]['value'] + '\n' + 'Ground Truth and The Incorrect Answer Typically Given by Humans as a Result of The Visual Illusion:' + truth['conversations'][1]['value'] + 'Response of VLM:' + item['answer']
            }
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json())
    answer = response.json()['choices'][0]['message']['content']
    answers.append(answer)
    print(answer)

answer_data = [{'score': answer} for answer in answers]
for item, answer_item, truth in zip(data, answer_data, ground_truth):
    item['conversations'] = truth['conversations']
    item.update(answer_item)

with open('/home/terran/lingjunmao/illusion/MyDataset/color/eval_results/gpt.json', 'w') as file:
    json.dump(data, file, indent=4)

print("Answers saved to test_with_answers.json")