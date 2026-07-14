import sqlite3
import random
from datetime import datetime, timedelta
import mysql.connector
from contextlib import contextmanager
import pandas as pd
import json
import os

if os.path.exists('movie_data.json'):
    with open('movie_data.json', 'r') as file:
        # Load the JSON data from the file
        movie_data = json.load(file) 
else:
    with open('movieappcompleteprocess/movie_data.json', 'r') as file:
        movie_data = json.load(file)

@contextmanager
def get_cursor():
    """cursor object"""
    conn = mysql.connector.connect(
        host="193.203.184.196",
        user="u816628190_yashwanth",
        password="Yash@mac1",
        database="u816628190_booking"
    )
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_results_as_dframe(query):
    """returns the dataframe for the select query
    Args:
        query (str): SQL query with optional parameterized values (%s)
    """
    with get_cursor() as cursor:
        cursor.execute(query)
        if cursor.description is None:  # No results returned
            return pd.DataFrame()  # Return empty DataFrame
            
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)

def update_record_in_db(query: str, params: tuple = None) -> None:
    """Executes SQL query with optional parameters
    
    Args:
        query (str): SQL query with optional parameterized values (%s)
        params (tuple, optional): Parameters for the query. Defaults to None.
        
    Raises:
        mysql.connector.Error: If there's an error executing the query
    """
    with get_cursor() as cursor:
        try:
            # Convert any list in params to JSON string
            if params:
                processed_params = tuple(
                    json.dumps(param) if isinstance(param, list) else param
                    for param in params
                )
            else:
                processed_params = params
                
            cursor.execute(query, processed_params)
        except mysql.connector.Error as e:
            print(f"Error executing query: {e}")
            raise
            


# def initialize_movie_booking_db(db_path: str = "movie_booking_details.db"):
#     """Initialize the movie booking database with sample data"""
    
#     # Sample data
#     # movies = [
#     #     "The Dark Knight", "Avengers: Endgame", "Inception", "Interstellar", 
#     #     "The Matrix", "Pulp Fiction", "The Godfather", "Forrest Gump",
#     #     "The Shawshank Redemption", "Fight Club", "Goodfellas", "Casablanca",
#     #     "Titanic", "The Lord of the Rings", "Star Wars", "Jaws",
#     #     "E.T.", "Jurassic Park", "Back to the Future", "Spider-Man",
#     #     "Batman Begins", "Iron Man", "Captain America", "Thor",
#     #     "Black Panther", "Wonder Woman", "Aquaman", "Guardians of the Galaxy",
#     #     "Doctor Strange", "Ant-Man", "The Flash", "Superman",
#     #     "Oppenheimer", "Barbie", "Fast X", "John Wick 4",
#     #     "Scream VI", "Avatar 2", "Top Gun Maverick", "Black Adam"
#     # ]

#     movies = movie_data.keys()
    
#     theatres = [
#         "Metro Cinema", "PVR Cinemas", "INOX", "Cinepolis", 
#         "Multiplex Grand", "Silver Screen", "Gold Cinema", "Platinum Multiplex",
#         "Royal Theatre", "Diamond Cinema", "Star Multiplex", "Crown Theatre",
#         "Elite Cinema", "Premiere Show", "Luxury Cinema", "City Centre Mall",
#         "Forum Mall Cinema", "Phoenix Mall", "Orion Mall", "Garuda Mall"
#     ]
    
#     # Time slots (in 24-hour format)
#     time_slots = [
#         "09:00:00", "09:30:00", "10:00:00", "11:00:00", "11:30:00",
#         "12:00:00", "12:30:00", "13:00:00", "14:00:00", "14:30:00", 
#         "15:00:00", "16:00:00", "16:30:00", "17:00:00", "18:00:00",
#         "18:30:00", "19:00:00", "19:30:00", "20:00:00", "20:30:00",
#         "21:00:00", "21:30:00", "22:00:00", "22:30:00"
#     ]
    
#     try:
#         # Connect to database
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()
        
#         # Drop existing tables if they exist
#         cursor.execute("DROP TABLE IF EXISTS showtimes")
#         cursor.execute("DROP TABLE IF EXISTS movies")  
#         cursor.execute("DROP TABLE IF EXISTS theatres")
        
#         # Create tables
#         cursor.execute('''
#             CREATE TABLE movies (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT UNIQUE NOT NULL
#             )
#         ''')
        
#         cursor.execute('''
#             CREATE TABLE theatres (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT UNIQUE NOT NULL
#             )
#         ''')
        
#         cursor.execute('''
#             CREATE TABLE showtimes (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 movie_id INTEGER,
#                 theatre_id INTEGER,
#                 showtime DATETIME NOT NULL,
#                 price REAL NOT NULL,
#                 FOREIGN KEY (movie_id) REFERENCES movies (id),
#                 FOREIGN KEY (theatre_id) REFERENCES theatres (id)
#             )
#         ''')
        
#         # Insert movies
#         for movie in movies:
#             cursor.execute("INSERT INTO movies (name) VALUES (?)", (movie,))
        
#         # Insert theatres
#         for theatre in theatres:
#             cursor.execute("INSERT INTO theatres (name) VALUES (?)", (theatre,))
        
#         # Generate showtimes starting from today
#         current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         # current_date = '2025-07-19 08:00:00'
#         showtime_count = 0
        
#         # Generate showtimes for next 10 days to ensure we get 300+ records
#         for day_offset in range(10):
#             show_date = current_date + timedelta(days=day_offset)
            
#             # For each day, create multiple showtimes
#             for movie_id in range(1, len(movies) + 1):
#                 # Each movie gets 2-4 random time slots per day
#                 num_shows = random.randint(2, 4)
#                 selected_times = random.sample(time_slots, num_shows)
                
#                 for time_slot in selected_times:
#                     # Random theatre for each show
#                     theatre_id = random.randint(1, len(theatres))
                    
#                     # Create datetime string
#                     show_datetime = f"{show_date.strftime('%Y-%m-%d')} {time_slot}"
                    
#                     # Random price between 150-500 INR
#                     price = round(random.uniform(150, 500), 2)
                    
#                     # Insert showtime
#                     cursor.execute('''
#                         INSERT INTO showtimes (movie_id, theatre_id, showtime, price)
#                         VALUES (?, ?, ?, ?)
#                     ''', (movie_id, theatre_id, show_datetime, price))
                    
#                     showtime_count += 1
                    
#                     # Break if we've reached our target
#                     if showtime_count >= 300:
#                         break
                
#                 if showtime_count >= 300:
#                     break
            
#             if showtime_count >= 300:
#                 break
        
#         # Commit changes
#         conn.commit()
        
#         # Verify data insertion
#         cursor.execute("SELECT COUNT(*) FROM movies")
#         movie_count = cursor.fetchone()[0]
        
#         cursor.execute("SELECT COUNT(*) FROM theatres")  
#         theatre_count = cursor.fetchone()[0]
        
#         cursor.execute("SELECT COUNT(*) FROM showtimes")
#         showtime_count = cursor.fetchone()[0]
        
#         print(f"Database initialized successfully!")
#         print(f"Movies: {movie_count}")
#         print(f"Theatres: {theatre_count}")
#         print(f"Showtimes: {showtime_count}")
        
#         # Show sample data
#         print(f"\nSample showtimes (first 10):")
#         cursor.execute('''
#             SELECT m.name, t.name, s.showtime, s.price 
#             FROM showtimes s 
#             JOIN movies m ON s.movie_id = m.id 
#             JOIN theatres t ON s.theatre_id = t.id 
#             ORDER BY s.showtime 
#             LIMIT 10
#         ''')
        
#         for row in cursor.fetchall():
#             print(f"  {row[0]} | {row[1]} | {row[2]} | ₹{row[3]}")
        
#         conn.close()
        
#     except sqlite3.Error as e:
#         print(f"Database error: {e}")
#     except Exception as e:
#         print(f"Error: {e}")


# # Integration with your existing chatbot
# def setup_chatbot_with_data():
#     """Setup chatbot with initialized database"""
    
#     # Initialize database first
#     print("Setting up movie booking database...")
#     initialize_movie_booking_db()
    
#     # Import your chatbot class (assuming it's in the same directory)
#     # from your_chatbot_file import MovieBookingChatbot
    
#     # Create chatbot instance
#     # bot = MovieBookingChatbot()
#     # return bot
    
#     print("Database setup complete! You can now run your chatbot.")


# ...existing code...
def initialize_movie_booking_db():
    movies = list(movie_data.keys())
    
    theatres = [
        "Metro Cinema", "PVR Cinemas", "INOX", "Cinepolis", 
        "Multiplex Grand", "Silver Screen", "Gold Cinema", "Platinum Multiplex",
        "Royal Theatre", "Diamond Cinema", "Star Multiplex", "Crown Theatre",
        "Elite Cinema", "Premiere Show", "Luxury Cinema", "City Centre Mall",
        "Forum Mall Cinema", "Phoenix Mall", "Orion Mall", "Garuda Mall"
    ]
    
    time_slots = [
        "09:00:00", "09:30:00", "10:00:00", "11:00:00", "11:30:00",
        "12:00:00", "12:30:00", "13:00:00", "14:00:00", "14:30:00", 
        "15:00:00", "16:00:00", "16:30:00", "17:00:00", "18:00:00",
        "18:30:00", "19:00:00", "19:30:00", "20:00:00", "20:30:00",
        "21:00:00", "21:30:00", "22:00:00", "22:30:00"
    ]
    
    try:
        # use one cursor for all operations
        with get_cursor() as cursor:
            # clear existing rows (preserve schema)
            cursor.execute("DELETE FROM showtimes")
            cursor.execute("DELETE FROM movies")
            cursor.execute("DELETE FROM theatres")
            # reset MySQL AUTO_INCREMENT
            cursor.execute("ALTER TABLE movies AUTO_INCREMENT = 1")
            cursor.execute("ALTER TABLE theatres AUTO_INCREMENT = 1")
            cursor.execute("ALTER TABLE showtimes AUTO_INCREMENT = 1")
            
            # insert movies with genre and theatres in batch
            movies_data = []
            for movie_name in movies:
                genre = movie_data[movie_name].get('genre', 'Unknown') if isinstance(movie_data[movie_name], dict) else 'Unknown'
                movies_data.append((movie_name, genre))
            
            cursor.executemany("INSERT IGNORE INTO movies (name, genre) VALUES (%s, %s)", movies_data)
            cursor.executemany("INSERT IGNORE INTO theatres (name) VALUES (%s)", [(t,) for t in theatres])
            
            # prepare showtime rows in memory and insert in one batch
            current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            show_rows = []
            showtime_count = 0
            for day_offset in range(10):
                show_date = current_date + timedelta(days=day_offset)
                for movie_id in range(1, len(movies) + 1):
                    num_shows = random.randint(2, 4)
                    selected_times = random.sample(time_slots, num_shows)
                    for time_slot in selected_times:
                        theatre_id = random.randint(1, len(theatres))
                        show_datetime = f"{show_date.strftime('%Y-%m-%d')} {time_slot}"
                        price = round(random.uniform(150, 500), 2)
                        show_rows.append((movie_id, theatre_id, show_datetime, price))
                        showtime_count += 1
                        if showtime_count >= 300:
                            break
                    if showtime_count >= 300:
                        break
                if showtime_count >= 300:
                    break
            
            if show_rows:
                cursor.executemany(
                    "INSERT INTO showtimes (movie_id, theatre_id, showtime, price) VALUES (%s, %s, %s, %s)",
                    show_rows
                )
        # context manager commits here
        # verify counts (reuses get_results_as_dframe)
        df = get_results_as_dframe("SELECT COUNT(*) as cnt FROM movies")
        movie_count = int(df.iloc[0]['cnt']) if not df.empty else 0
        df = get_results_as_dframe("SELECT COUNT(*) as cnt FROM theatres")
        theatre_count = int(df.iloc[0]['cnt']) if not df.empty else 0
        df = get_results_as_dframe("SELECT COUNT(*) as cnt FROM showtimes")
        showtime_count = int(df.iloc[0]['cnt']) if not df.empty else 0

        print(f"Database initialized successfully!")
        print(f"Movies: {movie_count}")
        print(f"Theatres: {theatre_count}")
        print(f"Showtimes: {showtime_count}")
    except Exception as e:
        print(f"Error: {e}")

# def verify_database(db_path: str = "movie_booking_details.db"):
#     """Verify the database structure and data"""
#     try:
#         conn = sqlite3.connect(db_path)
#         cursor = conn.cursor()
        
#         # Check table structure
#         print("Database Tables:")
#         cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
#         tables = cursor.fetchall()
#         for table in tables:
#             print(f"  - {table[0]}")
        
#         # Check date range of showtimes
#         cursor.execute("SELECT MIN(showtime), MAX(showtime) FROM showtimes")
#         date_range = cursor.fetchone()
#         print(f"\nShowtime date range: {date_range[0]} to {date_range[1]}")
        
#         # Show some sample queries
#         print(f"\nSample queries:")
        
#         # Movies available today
#         today = datetime.now().strftime('%Y-%m-%d')
#         # today = '2025-07-19 08:00:00'
#         cursor.execute('''
#             SELECT DISTINCT m.name 
#             FROM showtimes s 
#             JOIN movies m ON s.movie_id = m.id 
#             WHERE DATE(s.showtime) = ? 
#             LIMIT 5
#         ''', (today,))
        
#         print("Movies available today:")
#         for row in cursor.fetchall():
#             print(f"  - {row[0]}")
        
#         conn.close()
        
#     except Exception as e:
#         print(f"Verification error: {e}")


def ensure_genre_column():
    """Ensure genre column exists in movies table."""
    try:
        with get_cursor() as cursor:
            # Check if genre column exists
            cursor.execute("SHOW COLUMNS FROM movies LIKE 'genre'")
            result = cursor.fetchone()
            
            if not result:
                # Add genre column if it doesn't exist
                cursor.execute("ALTER TABLE movies ADD COLUMN genre VARCHAR(50) DEFAULT 'Unknown'")
                print("✓ Added 'genre' column to movies table")
            else:
                print("✓ Genre column already exists in movies table")
    except Exception as e:
        print(f"Error ensuring genre column: {e}")

print("Initializing movie booking database...")
ensure_genre_column()
initialize_movie_booking_db()
print("\n" + "="*50)

# ...existing code...
    
    # Uncomment to test with your chatbot
    # print("\n" + "="*50)
    # print("Testing chatbot...")
    # bot = setup_chatbot_with_data()