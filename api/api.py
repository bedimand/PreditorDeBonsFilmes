from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import List, Optional
import mysql.connector
import joblib
import numpy as np
import pandas as pd
from fastapi.responses import HTMLResponse

# Database connection settings
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "12345678",
    "database": "IMDB",
    "port": 3306
}

# Pydantic models for responses
class Movie(BaseModel):
    id: str
    primaryTitle: str
    originalTitle: Optional[str]
    releaseDate: Optional[str]
    runtimeMinutes: Optional[int]
    averageRating: Optional[float]
    numVotes: Optional[int]

class Genre(BaseModel):
    id: int
    name: str

class MovieDetail(BaseModel):
    id: str
    url: Optional[str]
    primaryTitle: str
    originalTitle: Optional[str]
    type: Optional[str]
    description: Optional[str]
    primaryImage: Optional[str]
    trailer: Optional[str]
    contentRating: Optional[str]
    isAdult: Optional[bool]
    releaseDate: Optional[str]
    startYear: Optional[int]
    endYear: Optional[int]
    runtimeMinutes: Optional[int]
    budget: Optional[float]
    grossWorldwide: Optional[float]
    averageRating: Optional[float]
    numVotes: Optional[int]
    metascore: Optional[int]
    weekendGrossAmount: Optional[float]
    weekendGrossCurrency: Optional[str]
    lifetimeGrossAmount: Optional[float]
    lifetimeGrossCurrency: Optional[str]
    weeksRunning: Optional[int]
    genres: List[str]
    languages: List[str]
    countries: List[str]
    companies: List[str]
    locations: List[str]

app = FastAPI(title="API de Consulta IMDB")

def get_db():
    """Get a new database connection."""
    return mysql.connector.connect(**DB_CONFIG)

# ----- Prediction Model Setup -----
model = joblib.load("models/gbc_model.joblib")
FEATURE_COLUMNS = list(model.feature_names_in_)

def preprocess_input(data: dict) -> np.ndarray:
    idx = {col: i for i, col in enumerate(FEATURE_COLUMNS)}
    x = np.zeros(len(FEATURE_COLUMNS), dtype=float)
    # Numeric features
    x[idx['runtimeMinutes']] = data.get('runtimeMinutes', 0)
    x[idx['budget']] = data.get('budget', 0)
    # One-hot features
    for g in data.get('genres', []):
        if g in idx: x[idx[g]] = 1.0
    for c in data.get('production_companies', []):
        key = f"comp_{c}"
        if key in idx: x[idx[key]] = 1.0
    for l in data.get('languages', []):
        key = f"lang_{l}"
        if key in idx: x[idx[key]] = 1.0
    for c in data.get('countries', []):
        key = f"ctry_{c}"
        if key in idx: x[idx[key]] = 1.0
    # Categorical rating and location
    rkey = f"rating_{data.get('rating')}"
    if rkey in idx: x[idx[rkey]] = 1.0
    lkey = f"loc_{data.get('loc')}"
    if lkey in idx: x[idx[lkey]] = 1.0
    return x

# ----- Pydantic Schemas for Prediction -----
class PredictRequest(BaseModel):
    runtimeMinutes: float
    budget: float
    genres: List[str]
    production_companies: Optional[List[str]] = []
    languages: List[str]
    countries: Optional[List[str]] = []
    rating: Optional[str] = None
    loc: Optional[str] = None

    @validator('runtimeMinutes')
    def validate_runtime_minutes(cls, v):
        if v <= 0:
            raise ValueError('runtimeMinutes deve ser maior que 0')
        if v > 180:
            raise ValueError('runtimeMinutes deve ser no máximo 180')
        return v

    @validator('budget')
    def validate_budget(cls, v):
        if v < 100:
            raise ValueError('budget deve ser pelo menos 100')
        return v

    @validator('genres')
    def validate_genres(cls, v):
        if not v:
            raise ValueError('é necessário ao menos um gênero')
        return v

    @validator('languages')
    def validate_languages(cls, v):
        if not v:
            raise ValueError('é necessário ao menos um idioma')
        return v

class PredictResponse(BaseModel):
    success_probability: float

@app.post("/predict", response_model=PredictResponse)
def predict_endpoint(req: PredictRequest):
    """Retorna a probabilidade prevista de sucesso de um filme em porcentagem."""
    data = req.dict()
    x = preprocess_input(data)
    df = pd.DataFrame([x], columns=FEATURE_COLUMNS)
    prob = model.predict_proba(df)[0, 1] * 100
    return PredictResponse(success_probability=prob)

@app.get("/movies", response_model=List[Movie])
def list_movies(limit: int = 10, offset: int = 0):
    """Retorna uma lista de filmes com paginação."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, primaryTitle, originalTitle, DATE_FORMAT(releaseDate, '%Y-%m-%d') AS releaseDate, \
         runtimeMinutes, averageRating, numVotes \
         FROM movies LIMIT %s OFFSET %s",
        (limit, offset)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.get("/movies/{movie_id}", response_model=MovieDetail)
def get_movie(movie_id: str):
    """Retorna detalhes completos do filme juntamente com gêneros, idiomas, países, produtoras e locações relacionados."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    # Main movie data
    cursor.execute(
        """
        SELECT id, url, primaryTitle, originalTitle, type, description, primaryImage, trailer, contentRating,
               isAdult, DATE_FORMAT(releaseDate, '%Y-%m-%d') AS releaseDate, startYear, endYear, runtimeMinutes,
               budget, grossWorldwide, averageRating, numVotes, metascore, weekendGrossAmount,
               weekendGrossCurrency, lifetimeGrossAmount, lifetimeGrossCurrency, weeksRunning
        FROM movies WHERE id = %s
        """, (movie_id,)
    )
    movie = cursor.fetchone()
    if not movie:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    # Fetch related lists
    cursor.execute("SELECT g.name FROM genres g JOIN movie_genres mg ON g.id = mg.genre_id WHERE mg.movie_id = %s", (movie_id,))
    movie['genres'] = [r['name'] for r in cursor.fetchall()]
    cursor.execute("SELECT l.name FROM languages l JOIN movie_languages ml ON l.id = ml.language_id WHERE ml.movie_id = %s", (movie_id,))
    movie['languages'] = [r['name'] for r in cursor.fetchall()]
    cursor.execute("SELECT c.name FROM countries c JOIN movie_countries mc ON c.id = mc.country_id WHERE mc.movie_id = %s", (movie_id,))
    movie['countries'] = [r['name'] for r in cursor.fetchall()]
    cursor.execute("SELECT co.name FROM companies co JOIN movie_companies mco ON co.id = mco.company_id WHERE mco.movie_id = %s", (movie_id,))
    movie['companies'] = [r['name'] for r in cursor.fetchall()]
    cursor.execute("SELECT lo.name FROM locations lo JOIN movie_locations mlc ON lo.id = mlc.location_id WHERE mlc.movie_id = %s", (movie_id,))
    movie['locations'] = [r['name'] for r in cursor.fetchall()]
    cursor.close()
    conn.close()
    return movie

@app.get("/genres", response_model=List[Genre])
def list_genres():
    """Retorna todos os gêneros."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM genres ORDER BY name")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.get("/genres/{genre_id}/movies", response_model=List[Movie])
def movies_by_genre(genre_id: int, limit: int = 10, offset: int = 0):
    """Retorna filmes de um gênero específico."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT m.id, m.primaryTitle, m.originalTitle, DATE_FORMAT(m.releaseDate, '%Y-%m-%d') AS releaseDate, \
         m.runtimeMinutes, m.averageRating, m.numVotes \
         FROM movie_genres mg \
         JOIN movies m ON mg.movie_id = m.id \
         WHERE mg.genre_id = %s LIMIT %s OFFSET %s",
        (genre_id, limit, offset)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# ----- Master table endpoints -----
class Language(BaseModel):
    id: str
    name: str

class Country(BaseModel):
    id: str
    name: str

class Company(BaseModel):
    id: str
    name: str

class Location(BaseModel):
    id: int
    name: str

@app.get("/languages", response_model=List[Language])
def list_languages():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM languages ORDER BY name")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.get("/languages/{lang_id}/movies", response_model=List[Movie])
def movies_by_language(lang_id: str, limit: int = 10, offset: int = 0):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT m.id, m.primaryTitle, m.originalTitle, DATE_FORMAT(m.releaseDate, '%Y-%m-%d') AS releaseDate, "
        "m.runtimeMinutes, m.averageRating, m.numVotes "
        "FROM movie_languages ml JOIN movies m ON ml.movie_id=m.id "
        "WHERE ml.language_id=%s LIMIT %s OFFSET %s",
        (lang_id, limit, offset)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.get("/countries", response_model=List[Country])
def list_countries():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM countries ORDER BY name")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.get("/countries/{country_id}/movies", response_model=List[Movie])
def movies_by_country(country_id: str, limit: int = 10, offset: int = 0):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT m.id, m.primaryTitle, m.originalTitle, DATE_FORMAT(m.releaseDate, '%Y-%m-%d') AS releaseDate, "
        "m.runtimeMinutes, m.averageRating, m.numVotes "
        "FROM movie_countries mc JOIN movies m ON mc.movie_id=m.id "
        "WHERE mc.country_id=%s LIMIT %s OFFSET %s",
        (country_id, limit, offset)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.get("/companies", response_model=List[Company])
def list_companies():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM companies ORDER BY name")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.get("/companies/{company_id}/movies", response_model=List[Movie])
def movies_by_company(company_id: str, limit: int = 10, offset: int = 0):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT m.id, m.primaryTitle, m.originalTitle, DATE_FORMAT(m.releaseDate, '%Y-%m-%d') AS releaseDate, "
        "m.runtimeMinutes, m.averageRating, m.numVotes "
        "FROM movie_companies mco JOIN movies m ON mco.movie_id=m.id "
        "WHERE mco.company_id=%s LIMIT %s OFFSET %s",
        (company_id, limit, offset)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.get("/locations", response_model=List[Location])
def list_locations():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM locations ORDER BY name")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.get("/locations/{location_id}/movies", response_model=List[Movie])
def movies_by_location(location_id: int, limit: int = 10, offset: int = 0):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT m.id, m.primaryTitle, m.originalTitle, DATE_FORMAT(m.releaseDate, '%Y-%m-%d') AS releaseDate, "
        "m.runtimeMinutes, m.averageRating, m.numVotes "
        "FROM movie_locations mlc JOIN movies m ON mlc.movie_id=m.id "
        "WHERE mlc.location_id=%s LIMIT %s OFFSET %s",
        (location_id, limit, offset)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# ----- Stats -----
class GenreCount(BaseModel):
    name: str
    movie_count: int

class YearlyCount(BaseModel):
    year: int
    count: int

@app.get("/stats/genres/top", response_model=List[GenreCount])
def stats_top_genres(limit: int = 10):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT g.name, COUNT(*) AS movie_count FROM movie_genres mg JOIN genres g ON mg.genre_id=g.id GROUP BY g.name ORDER BY movie_count DESC LIMIT %s", (limit,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.get("/stats/yearly/count", response_model=List[YearlyCount])
def stats_yearly_count(start: Optional[int] = None, end: Optional[int] = None):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT startYear AS year, COUNT(*) AS count FROM movies WHERE startYear IS NOT NULL"
    params = []
    if start is not None:
        sql += " AND startYear >= %s"; params.append(start)
    if end is not None:
        sql += " AND startYear <= %s"; params.append(end)
    sql += " GROUP BY startYear ORDER BY startYear"
    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

@app.get("/health")
def health_check():
    return {"status":"ok"}

@app.get("/version")
def version():
    return {"api_version":"1.0.0","database":"IMDB"}

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Preditor de Sucesso de Filmes</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; margin:0; padding:0; display:flex; justify-content:center; align-items:center; height:100vh; }
        .container { background:#fff; padding:20px; border-radius:8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); width: 400px; }
        h1 { text-align:center; color:#333; }
        form { display: flex; flex-direction: column; gap:12px; }
        label { font-weight: bold; color: #555; }
        input { width:100%; padding:8px; border:1px solid #ccc; border-radius:4px; }
        button { padding:10px; background: #007bff; color:#fff; border:none; border-radius:4px; cursor:pointer; font-size:16px; }
        button:hover { background: #0056b3; }
        #result { text-align:center; margin-top:15px; font-weight:bold; color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Preditor de Sucesso de Filmes</h1>
        <form id="predictForm">
            <label>Duração (minutos):
                <input type="number" id="runtimeMinutes" placeholder="ex: 120" required max="180">
            </label>
            <label>Orçamento (em dólares):
                <input type="number" id="budget" placeholder="ex: 500000" required>
            </label>
            <label>Gêneros (em inglês, separados por vírgula):
                <input type="text" id="genres" placeholder="ex: Action, Comedy, Drama">
            </label>
            <button type="button" id="btnGenres" style="margin-left:4px;">Ver gêneros</button>
            <label>Produtoras (separadas por vírgula):
                <input type="text" id="production_companies" placeholder="ex: Twentieth Century Fox, Netflix">
            </label>
            <button type="button" id="btnCompanies" style="margin-left:4px;">Ver produtoras</button>
            <label>Idiomas (separados por vírgula):
                <input type="text" id="languages" placeholder="ex: en, pt">
            </label>
            <button type="button" id="btnLanguages" style="margin-left:4px;">Ver idiomas</button>
            <label>Países (separados por vírgula):
                <input type="text" id="countries" placeholder="ex: US, UK">
            </label>
            <button type="button" id="btnCountries" style="margin-left:4px;">Ver países</button>
            <label>Classificação Indicativa:
                <select id="rating">
                    <option value="G">G</option>
                    <option value="PG">PG</option>
                    <option value="Not Rated">Not Rated</option>
                    <option value="PG-13">PG-13</option>
                    <option value="R">R</option>
                </select>
            </label>
            <button type="button" id="btnPredict">Prever</button>
        </form>
        <h2 id="result"></h2>
    </div>
    <script>
        async function makePrediction() {
            const payload = {
                runtimeMinutes: parseFloat(document.getElementById('runtimeMinutes').value),
                budget: parseFloat(document.getElementById('budget').value),
                genres: document.getElementById('genres').value.split(',').map(s => s.trim()).filter(Boolean),
                production_companies: document.getElementById('production_companies').value.split(',').map(s => s.trim()).filter(Boolean),
                languages: document.getElementById('languages').value.split(',').map(s => s.trim()).filter(Boolean),
                countries: document.getElementById('countries').value.split(',').map(s => s.trim()).filter(Boolean),
                rating: document.getElementById('rating').value
            };
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            if (response.ok) {
                const data = await response.json();
                document.getElementById('result').innerText = 'Probabilidade de sucesso prevista: ' + data.success_probability.toFixed(2) + '%';
            } else {
                const err = await response.json();
                // Extrai apenas as mensagens de validação
                const msgs = (err.detail || []).map(e => e.msg).join('; ');
                document.getElementById('result').innerText = 'Erro ' + response.status + ': ' + msgs;
            }
        }
        // Disparo dos eventos após carregamento da página
        window.onload = () => {
            document.getElementById('btnPredict').addEventListener('click', makePrediction);
            // Listagem de opções disponíveis
            document.getElementById('btnGenres').addEventListener('click', () => {
                window.open('/genres', '_blank');
            });
            document.getElementById('btnCompanies').addEventListener('click', () => {
                window.open('/companies', '_blank');
            });
            document.getElementById('btnLanguages').addEventListener('click', () => {
                window.open('/languages', '_blank');
            });
            document.getElementById('btnCountries').addEventListener('click', () => {
                window.open('/countries', '_blank');
            });
        };
    </script>
</body>
</html>"""

# Adiciono classe e endpoint para listar classificações indicativas
class RatingOption(BaseModel):
    rating: str

@app.get("/ratings", response_model=List[RatingOption])
def list_ratings():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT contentRating AS rating FROM movies WHERE contentRating IS NOT NULL ORDER BY rating")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# To run:
# uvicorn api:app --reload --host 0.0.0.0 --port 8000
