# Backend Lab 4

**Author:** Kyryl Kozarezov, IM-33

**Variant:** 33 % 3 = 0 (Облік доходів)

**Each lab builds on the previous one**

**Deploy:** [https://backend-lab3-u65x.onrender.com](https://backend-lab3-u65x.onrender.com)

## Requirements

- Python
- FastAPI (v0.95.0 or higher)
- Docker and Docker Compose
  
## Requirements

This project uses environment variables for configuratSion. You need to create a .env file in the root of the project.

The file should contain the following variables:
```
PORT=8000
DATABASE_URL=your_database_url
```
PORT: The port on which the application server will run. DATABASE_URL: URL to your database
Default PORT is 3000 if not set in .env file
  
## Setup and launch

### 1. Clone the repository

```
git clone (https://github.com/Kiryaoo/Backend-LAB2.git)
cd Backend-LAB2
```

### 2. Choose a launch method

#### Option A: Local launch (without Docker)

```
# Create and activate the virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the server (autoreload)
uvicorn main:app --reload
```

The application will be available at `http://localhost:8000` (or `http://localhost:<PORT>` if you specify a different port).

#### Option B: Docker

```
# 1. Build the image
docker build . -t backend-lab2:latest .

# 2. Run the container
docker run -it --rm --network=host -e PORT=8000 backend-lab2:latest
```

The application is available at `(http://localhost:8000)`.

---

#### Option C: Docker Compose

```
docker compose up --build
```

> For older versions of the Docker CLI, you may need the hyphenated command: `docker-compose up --build`.

To stop containers:

```
docker compose down
```

## Endpoints

### Health Check

After starting, check the service's health:

`http://localhost:8000/healthcheck`

Expected response:

```
{"status":"ok"}
```
### Users 

`http://localhost:8000/users`

### Categories

`http://localhost:8000/categories`

### Records 

`http://localhost:8000/records`

### Other 

`http://127.0.0.1:8000/docs`


Follow this link you can test all of used methods like POST,GET, etc. and all endpoints
