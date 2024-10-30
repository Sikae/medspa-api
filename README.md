# Medspa Appointment API

An API built with Flask for managing medspa appointments and services.

## Prerequisites

- **Python 3.7+**
- **PostgreSQL 12+**
- **Git**

## Setup Instructions

### 1. Clone the Repository

Clone the project to your local machine:

```bash
git clone https://github.com/Sikae/medspa-api.git
cd medspa-api
```

### 2. Create and Activate a Virtual Environment

Clone the project to your local machine:

```bash
python3 -m venv venv
source venv/bin/activate  # for mac
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a .env file in the project’s root directory with the following content. Update username and password with your PostgreSQL credentials:

```bash
FLASK_APP=app
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost:5432/medspa_db
```

### 5. Set Up the PostgreSQL Database

#### Access PostgreSQL:
```bash
psql -U postgres
```
#### Create a New Database::
```bash
CREATE DATABASE medspa_db;
```

### 6. Initialize the Database with Flask-Migrate

Run the following commands to set up the database tables:
```bash
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

### 7. Start the Flask Server
Run the Flask development server:
```bash
flask run --port 5001
```

## API Endpoints

There is a file `requests.http` with some example requests you can run. You need to have the `REST Client` extension installed on VS Code.

