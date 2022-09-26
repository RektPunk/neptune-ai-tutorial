import os
from dotenv import load_dotenv


class NeptuneToken:
    def __init__(self):
        load_dotenv()
        self.neptune_api_token = os.environ["NEPTUNE_API_TOKEN"]
