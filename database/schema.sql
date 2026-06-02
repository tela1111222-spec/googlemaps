-- database/schema.sql

-- 1. 使用者偏好設定表
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    warning_threshold INTEGER NOT NULL DEFAULT 50,
    enable_voice_alert INTEGER NOT NULL DEFAULT 1,
    enable_auto_brightness INTEGER NOT NULL DEFAULT 1
);

-- 2. 路口待轉規則表
CREATE TABLE IF NOT EXISTS intersection_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intersection_name TEXT NOT NULL,
    need_two_stage_turn INTEGER NOT NULL DEFAULT 1,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL
);

-- 3. 歷史行程紀錄表 (保留相容性)
CREATE TABLE IF NOT EXISTS route_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination TEXT NOT NULL,
    avoid_conditions TEXT,
    encrypted_route_data TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 插入模擬待轉路口數據（若不存在）
INSERT OR IGNORE INTO intersection_limits (id, intersection_name, need_two_stage_turn, latitude, longitude)
VALUES (1, '忠孝新生路口 (忠孝新生捷運站旁)', 1, 25.042, 121.535);

INSERT OR IGNORE INTO intersection_limits (id, intersection_name, need_two_stage_turn, latitude, longitude)
VALUES (2, '忠孝復興路口 (SOGO百貨旁)', 1, 25.042, 121.543);

INSERT OR IGNORE INTO intersection_limits (id, intersection_name, need_two_stage_turn, latitude, longitude)
VALUES (3, '北宜公路待轉路口', 1, 24.978, 121.585);

-- 插入預設設定資料（若不存在）
INSERT OR IGNORE INTO user_settings (id, warning_threshold, enable_voice_alert, enable_auto_brightness)
VALUES (1, 50, 1, 1);
