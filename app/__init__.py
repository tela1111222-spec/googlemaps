import os
import sqlite3
from flask import Flask

# 建立 Flask 應用程式初始化
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # 預設設定
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-googlemaps'),
        DATABASE=os.path.join(app.instance_path, 'database.db'),
    )

    if test_config is None:
        # 載入實例設定 (如果有的話)
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 載入測試設定
        app.config.from_mapping(test_config)

    # 確保實例資料夾存在 (存放 SQLite 資料庫用)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 註冊 Blueprints 路由控制器
    from app.routes.main import main_bp
    from app.routes.alert import alert_bp
    from app.routes.hazard import hazard_bp
    from app.routes.history import history_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(hazard_bp)
    app.register_blueprint(history_bp)

    return app

def init_db():
    """初始化 SQLite 資料庫結構"""
    db_path = 'instance/database.db'
    schema_path = 'database/schema.sql'
    
    # 確保 instance 目錄存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    print(f"正在初始化資料庫: {db_path} ...")
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("資料庫初始化完成！")
