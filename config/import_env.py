from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('GOOGLE_API_KEY')
if not API_KEY:
    raise ValueError('API não encontrada')