import sqlite3

conn = sqlite3.connect("satellite_database.db")

c = conn.cursor()
c.execute("PRAGMA foreign_keys = ON")


c.execute("""CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,             
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )""")



c.execute("""CREATE TABLE IF NOT EXISTS Satellites (
        norad_id INTEGER PRIMARY KEY,
        satellite_name TEXT NOT NULL,
        satellite_type TEXT
    )""")


c.execute("""CREATE TABLE IF NOT EXISTS TLE_Data (
        tle_id INTEGER PRIMARY KEY AUTOINCREMENT,
        norad_id INTEGER NOT NULL,
        tle_line1 TEXT NOT NULL,
        tle_line2 TEXT NOT NULL,
        orbit_type TEXT,
        inclination REAL,
        eccentricity REAL,
        mean_motion REAL,
        epoch_date TEXT NOT NULL,
        retrieved_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (norad_id) REFERENCES Satellites(norad_id)
    )""")




c.execute("""CREATE TABLE IF NOT EXISTS User_Favourites (
        favourite_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        norad_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (norad_id) REFERENCES Satellites(norad_id),
        UNIQUE(user_id, norad_id)
    )""")


conn.commit()
conn.close()
