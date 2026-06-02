import os
import sqlite3
from flask import Flask
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def init_db():
    """
    初始化資料庫。
    讀取 database/schema.sql 並在 instance/database.db 中建立資料表。
    """
    os.makedirs('instance', exist_ok=True)
    db_path = 'instance/database.db'
    schema_path = 'database/schema.sql'
    
    if not os.path.exists(schema_path):
        print(f"Error: Schema file not found at {schema_path}")
        return
        
    conn = sqlite3.connect(db_path)
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def create_app():
    """
    Flask 應用程式工廠函式。
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # 確保 instance 資料夾存在
    os.makedirs(app.instance_path, exist_ok=True)
    
    # 設定 Flask 全域組態
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev_key_for_personalized_route_system'),
        DATABASE=os.path.join(app.instance_path, 'database.db'),
    )
    
    # 註冊 Blueprints
    from app.routes.main import main_bp
    from app.routes.history import history_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(history_bp)
    
    return app
