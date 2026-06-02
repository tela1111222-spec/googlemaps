-- database/schema.sql

-- 1. 使用者設定表
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    warning_threshold INTEGER NOT NULL DEFAULT 0,
    enable_voice_alert INTEGER NOT NULL DEFAULT 1,
    approaching_alert_ratio REAL NOT NULL DEFAULT 0.9
);

-- 2. 道路速限表
CREATE TABLE IF NOT EXISTS road_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    road_name TEXT NOT NULL,
    speed_limit INTEGER NOT NULL,
    start_lat REAL NOT NULL,
    start_lng REAL NOT NULL,
    end_lat REAL NOT NULL,
    end_lng REAL NOT NULL,
    upcoming_limit INTEGER,
    upcoming_lat REAL,
    upcoming_lng REAL
);

-- 3. 歷史行程紀錄表
CREATE TABLE IF NOT EXISTS route_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination TEXT NOT NULL,
    avoid_conditions TEXT,
    encrypted_route_data TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
