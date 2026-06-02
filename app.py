from app import create_app

app = create_app()

if __name__ == '__main__':
    # 預設啟動在 localhost:5000，並啟用除錯模式
    app.run(host='127.0.0.1', port=5000, debug=True)
