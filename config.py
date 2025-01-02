import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    @classmethod
    def load_env_vars(cls):
        #Dynamically load all environment variables into the Config class.
        for key, value in os.environ.items():
            # Skip some unnecessary default environment variables
            if key != "PATH" and key != "PYTHONPATH":
                setattr(cls, key, value)

Config.load_env_vars()