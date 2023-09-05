CREATE TABLE IF NOT EXISTS user (
    chat_id INTEGER PRIMARY KEY,
    lon REAL default NULL,
    lat REAL default NULL,
    city TEXT default NULL,
    notice_time INTEGER default NULL
);
CREATE TABLE IF NOT EXISTS user_choices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER UNIQUE,
    yandex INTEGER default 0,
    gismeteo INTEGER default 0,
    FOREIGN KEY (chat_id)  REFERENCES user (chat_id)
);
CREATE TABLE IF NOT EXISTS weather_history (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT,
    lon REAL,
    lat REAL,
    dt TEXT
);
CREATE TABLE IF NOT EXISTS weather_history_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stat_id INTEGER,
    source TEXT, -- yandex/gismeteo
    part TEXT, -- day/morning/night/evening
    temp_avg INTEGER,
    wind_speed INTEGER,
    wind_dir TEXT,
    pressure_mm INTEGER,
    humidity INTEGER,
    prec_type TEXT,
    FOREIGN KEY (stat_id)  REFERENCES yandex_history (id)
);