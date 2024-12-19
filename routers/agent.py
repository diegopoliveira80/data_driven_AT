from langchain.tools import tool
from langchain.chains import LLMChain
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

import os
import json
import yaml
from fastapi import APIRouter

router = APIRouter()
load_dotenv()

def filter_starting_xi(line_ups: str) -> dict:
    """
    Filter the starting XI players from the provided lineups.
    
    Args:
        line_ups (str): The JSON string containing the lineups of the teams.
        
    Returns:
    
    """
    line_ups_dict = line_ups
    filter_starting_xi =  {}
    for team, team_line_up in line_ups_dict.items():
        filter_starting_xi[team] = []
        for player in sorted(team_line_up, key= lambda x: x["jersey_number"]):
            try:
                positions = player["positions"]["positions"]
                if positions[0].get("start_reason") == "Starting XI":
                    filter_starting_xi[team].append({
                        "player": player["player_name"],
                        "position": positions[0].get('position'),
                        "jersey_number": player["jersey_number"]
                    })
            except (KeyError, IndexError):
                continue
    return filter_starting_xi


def get_sport_specialist_comments_about_match(dados1: str, 
                                              dados2: str, 
                                              dados3: str, 
                                              agent_prompt: str) -> str:
    """
    Returns the comments of a sports specialist about a specific match.
    The comments are generated based on match details and lineups.
    """
    
    dados3 = filter_starting_xi(dados3)

    GEMINI_API_KEY_PRO = os.getenv("GEMINI_API_KEY_PRO")
    llm = GoogleGenerativeAI(google_api_key=GEMINI_API_KEY_PRO,
                             model="gemini-pro",
                             temperature=0.4)
    input_variables={"dados1": yaml.dump(dados1),
                     "dados2": yaml.dump(dados2),
                     "dados3": yaml.dump(dados3)}
    prompt = PromptTemplate.from_template(agent_prompt)
    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
    
    return chain.run(**input_variables)