from coding_agent import agent_loop
import os 
from dotenv import load_dotenv

load_dotenv()

model = os.getenv("MODEL","")
api_key = os.getenv("API_KEY","")



def main():
    agent_loop(model,api_key)


if __name__ == "__main__":
    main()
