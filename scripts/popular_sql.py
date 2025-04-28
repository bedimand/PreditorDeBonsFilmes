import mysql.connector
import pandas as pd
import ast
import pycountry

# Establish a connection to the MySQL server
conn = mysql.connector.connect(
    host="localhost",  # Your MySQL host
    user="root",  # Your MySQL username
    password="12345678",  # Your MySQL password
    database="IMDB",  # Your database name
    port=3306  # MySQL port, default is 3306
)

cursor = conn.cursor(buffered=True)

# Define the function to create tables
def create_tables():
    # First, create the movies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id VARCHAR(255) PRIMARY KEY,
            url VARCHAR(255),
            primaryTitle VARCHAR(255),
            originalTitle VARCHAR(255),
            type VARCHAR(50),
            description TEXT,
            primaryImage VARCHAR(255),
            trailer VARCHAR(255),
            contentRating VARCHAR(50),
            isAdult BOOLEAN,
            releaseDate DATE,
            startYear INT,
            endYear INT,
            runtimeMinutes INT,
            budget DECIMAL(15,2),
            grossWorldwide DECIMAL(15,2),
            averageRating DECIMAL(3,2),
            numVotes INT,
            metascore INT,
            weekendGrossAmount DECIMAL(15,2),
            weekendGrossCurrency VARCHAR(50),
            lifetimeGrossAmount DECIMAL(15,2),
            lifetimeGrossCurrency VARCHAR(50),
            weeksRunning INT
        );
    """)
    conn.commit()  # Commit here to ensure the movies table is created before proceeding

    # Now, create the other tables that reference the movies table
    queries = [
        """
        CREATE TABLE IF NOT EXISTS companies (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS countries (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS genres (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS languages (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS locations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS movie_companies (
            movie_id VARCHAR(255),
            company_id VARCHAR(255),
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS movie_countries (
            movie_id VARCHAR(255),
            country_id VARCHAR(255),
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            FOREIGN KEY (country_id) REFERENCES countries(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS movie_genres (
            movie_id VARCHAR(255),
            genre_id INT,
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            FOREIGN KEY (genre_id) REFERENCES genres(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS movie_languages (
            movie_id VARCHAR(255),
            language_id VARCHAR(255),
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            FOREIGN KEY (language_id) REFERENCES languages(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS movie_locations (
            movie_id VARCHAR(255),
            location_id INT,
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            FOREIGN KEY (location_id) REFERENCES locations(id)
        );
        """
    ]

    # Execute each query to create the remaining tables
    for query in queries:
        cursor.execute(query)

    # Commit all changes to the database
    conn.commit()

# Function to insert data into the tables
def insert_data(data):
    # Initialize caches for master tables
    genre_cache = {}
    language_cache = {}
    country_cache = {}
    company_cache = {}
    location_cache = {}

    # Insert data into movies table and their relationships
    for _, row in data.iterrows():
        # Prepare movie record
        movie_values = (
            row['id'], row['url'], row['primaryTitle'], row['originalTitle'], row['type'], row['description'],
            row['primaryImage'], row['trailer'], row['contentRating'], row['isAdult'], row['releaseDate'],
            row['startYear'], row['endYear'], row['runtimeMinutes'], row['budget'], row['grossWorldwide'],
            row['averageRating'], row['numVotes'], row['metascore'], row['weekendGrossAmount'],
            row['weekendGrossCurrency'], row['lifetimeGrossAmount'], row['lifetimeGrossCurrency'], row['weeksRunning']
        )
        movie_values = [None if pd.isna(val) else val for val in movie_values]
        cursor.execute("""
            INSERT INTO movies (id, url, primaryTitle, originalTitle, type, description, primaryImage, trailer, contentRating,
            isAdult, releaseDate, startYear, endYear, runtimeMinutes, budget, grossWorldwide, averageRating, numVotes,
            metascore, weekendGrossAmount, weekendGrossCurrency, lifetimeGrossAmount, lifetimeGrossCurrency, weeksRunning)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, movie_values)

        # genres cache-backed inserts
        for genre in row['genres']:
            if genre not in genre_cache:
                cursor.execute("INSERT IGNORE INTO genres (name) VALUES (%s)", (genre,))
                cursor.execute("SELECT id FROM genres WHERE name = %s", (genre,))
                genre_cache[genre] = cursor.fetchone()[0]
            cursor.execute("INSERT IGNORE INTO movie_genres (movie_id, genre_id) VALUES (%s, %s)", (row['id'], genre_cache[genre]))

        # languages cache-backed inserts
        for language in row['spokenLanguages']:
            if language not in language_cache:
                cursor.execute("INSERT IGNORE INTO languages (id, name) VALUES (%s, %s)", (language, language))
                language_cache[language] = language
            cursor.execute("INSERT IGNORE INTO movie_languages (movie_id, language_id) VALUES (%s, %s)", (row['id'], language_cache[language]))

        # countries cache-backed inserts
        for country in row['countriesOfOrigin']:
            if country not in country_cache:
                cursor.execute("INSERT IGNORE INTO countries (id, name) VALUES (%s, %s)", (country, country))
                country_cache[country] = country
            cursor.execute("INSERT IGNORE INTO movie_countries (movie_id, country_id) VALUES (%s, %s)", (row['id'], country_cache[country]))

        # companies cache-backed inserts
        for comp in row['productionCompanies']:
            if isinstance(comp, dict):
                comp_id = comp.get('id')
                comp_name = comp.get('name')
            else:
                comp_id = str(comp)
                comp_name = str(comp)
            if comp_id not in company_cache:
                cursor.execute("INSERT IGNORE INTO companies (id, name) VALUES (%s, %s)", (comp_id, comp_name))
                company_cache[comp_id] = comp_id
            cursor.execute("INSERT IGNORE INTO movie_companies (movie_id, company_id) VALUES (%s, %s)", (row['id'], comp_id))

        # locations cache-backed inserts
        for loc in row['filmingLocations']:
            if loc not in location_cache:
                cursor.execute("INSERT IGNORE INTO locations (name) VALUES (%s)", (loc,))
                cursor.execute("SELECT id FROM locations WHERE name = %s", (loc,))
                location_cache[loc] = cursor.fetchone()[0]
            cursor.execute("INSERT IGNORE INTO movie_locations (movie_id, location_id) VALUES (%s, %s)", (row['id'], location_cache[loc]))

    conn.commit()

# Load the Excel data
file_path = 'movies_data.xlsx'
data = pd.read_excel(file_path)
# Drop duplicate entries by movie id to avoid primary key conflicts
data = data.drop_duplicates(subset=['id'])
# Convert string representations of list columns into actual Python lists
list_columns = ['genres', 'countriesOfOrigin', 'spokenLanguages', 'productionCompanies', 'filmingLocations']
for col in list_columns:
    data[col] = data[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else (x if isinstance(x, list) else []))

# Create tables
create_tables()

# Dynamically seed the countries master table using codes from the DataFrame
unique_country_codes = {
    code for codes in data['countriesOfOrigin'] for code in codes
}
country_mapping = []
for code in unique_country_codes:
    country = pycountry.countries.get(alpha_2=code)
    country_name = country.name if country else code
    country_mapping.append((code, country_name))
cursor.executemany(
    "INSERT IGNORE INTO countries (id, name) VALUES (%s, %s)",
    country_mapping
)
conn.commit()

# Now insert movie data
insert_data(data)

# Close the connection to the database
cursor.close()
conn.close()

"Data inserted successfully!"
