from app import create_app, init_db
import sys

app = create_app()

if __name__ == '__main__':
    # 提供指令列參數供快速初始化 SQLite 資料庫
    # 執行: python app.py init-db
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        init_db()
    else:
        app.run(debug=True)
