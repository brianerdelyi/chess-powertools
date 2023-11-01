import argparse
import sqlite3
import utils

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Read PGN file and save to an SQLite database.")
parser.add_argument("pgn_file", help="Input PGN file path")
parser.add_argument("db_file", help="Output SQLite database path")
args = parser.parse_args()

# Define the columns you want to exclude
columns_to_exclude = ["PlyCount", "SomeOtherColumn"]  # Add column names you want to exclude here

# Connect to SQLite database
try:
    conn = sqlite3.connect(args.db_file)
except ConnectionRefusedError:
    print("Error: Couldn't connect to Database, please try again")
    exit()
cursor = conn.cursor()

# Define the table name
table_name = "games"

# Detect the headers
headers = utils.extract_headers_pgn(args.pgn_file)
if not headers:
    print("No games found in the PGN file.")
    conn.close()
    exit()

# Check if the table exists and create it if it doesn't
cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
if cursor.fetchone() is None:
    # The table doesn't exist, so create it with a single dummy column
    cursor.execute(f"CREATE TABLE {table_name} (GameID INTEGER PRIMARY KEY AUTOINCREMENT);")
    conn.commit()

# Add columns based on PGN file headers
cursor.execute(f"PRAGMA table_info({table_name})")
existing_columns = [column[1] for column in cursor.fetchall()]

for header in headers:
    if header not in existing_columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {header} TEXT")

conn.commit()

# Filter out columns to exclude
columns_to_insert = [header for header in headers if header not in columns_to_exclude]

# Get the games
games = utils.extract_games_pgn(args.pgn_file)
total_games = len(games)

for game in games:
    # Insert the data into the SQLite table
    placeholders = ', '.join(['?'] * len(columns_to_insert))
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns_to_insert)}) VALUES ({placeholders})"
    cursor.execute(insert_sql, tuple(game[header] if header in game.keys() else None for header in columns_to_insert))
    conn.commit()

if total_games > 0:
    print(f"Successfully inserted {total_games} games")

# Close the SQLite connection
conn.close()
