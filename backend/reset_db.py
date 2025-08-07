from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL)

# Drop all tables including alembic_version
with engine.connect() as connection:
    connection.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS tasks CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS users CASCADE"))
    connection.execute(text("DROP TABLE IF EXISTS task_files CASCADE"))
    connection.commit()

print("All tables dropped successfully!") 