-- database/schema.sql
-- Google Maps 地圖導航系統 SQLite 資料庫結構設計

-- 1. 行程歷史紀錄表 (加密儲存，維護個人隱私)
CREATE TABLE IF NOT EXISTS route_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination TEXT NOT NULL,
    avoid_conditions TEXT,
    encrypted_route_data TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 測速照相點資料表 (預載及自訂測速點，支援快速空間查詢)
CREATE TABLE IF NOT EXISTS speed_camera (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    speed_limit INTEGER NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. 兩段式待轉路口資料表 (預載待轉提示路口)
CREATE TABLE IF NOT EXISTS two_stage_turn (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. 即時路況與障礙物回報表 (用路人一鍵回報及按讚覆核)
CREATE TABLE IF NOT EXISTS hazard_report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    hazard_type TEXT NOT NULL, -- 'accident' (車禍), 'construction' (施工), 'obstacle' (障礙物)
    description TEXT,
    votes INTEGER DEFAULT 0,  -- 覆核按讚數，可用於防刷及可信度篩選
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
