import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    NOTION_TOKEN = os.getenv('NOTION_TOKEN')
    NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
    
    # SQLAlchemy 설정 추가
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///calendar.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def validate_config():
    required_vars = ['NOTION_TOKEN', 'NOTION_DATABASE_ID']
    missing = [var for var in required_vars if not getattr(Config, var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")