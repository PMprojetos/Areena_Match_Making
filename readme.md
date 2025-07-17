# Areena Match Making API

A backend service built with **Flask**, **GraphQL**, and **MongoDB** to manage soccer matches between teams. This API is designed to power league organizers with smart scheduling tools that respect rest periods, allowed time slots, and future extensibility like scores and full season generation.

---

## 🎯 Project Objective

The goal of this project is to simulate a **matchmaking system** for soccer leagues where teams can be created, matches scheduled, and strict business rules enforced, such as:

- Matches must be scheduled only at allowed time slots  
- Teams must rest at least 66 hours between games  
- No match overlaps are allowed for the same team  
- Match data should be easy to query and modify via GraphQL

This API lays the foundation for a more complete sports league management platform.

---

## 🧱 Project Structure

```
├── app/
│   ├── models.py       # MongoEngine models (Team, Match, Round)
│   ├── schema.py       # GraphQL schema and mutations
│   ├── services.py     # Core business logic (scheduling, validations)
│   └── __init__.py     # Flask app setup
├── Scripts/
│   ├── __init__.py 
│   └── seed_teams.py   # Script to seed the database with initial teams
├── tests/              # Unit and integration tests using Pytest
├── run.py              # Entry point to run the Flask app
├── requirements.txt    # Project dependencies
├── Dockerfile          # Docker image setup
└── README.md           # Project documentation
```

## Database Seeding for Tests

To ensure consistent testing, the project includes a pytest fixture that seeds the MongoDB test database with 20 popular Brazilian soccer teams. This allows tests that require existing teams to run reliably.

The fixture is located in the `scripts/` .

Example team names seeded:

- Flamengo
- Cruzeiro
- Palmeiras
- Ceará
- São Paulo
- Santos
- And more...

This setup helps avoid manual database population and makes the test suite easier to run in any environment.

---

## ⚙️ Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/PMprojetos/Areena_Match_Making.git
cd Areena_Match_Making
```

### 2. Create and Activate Virtual Environment

#### On Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If you get a permission error:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### On Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Start the API

```bash
python run.py
```

API will be available at: [http://localhost:5000/graphql](http://localhost:5000/graphql)

### 5. Run Tests

```bash
pytest
```

---

## 📋 Business Rules

These rules are strictly enforced in the API logic:

### ✅ Allowed Time Slots

Matches can only be scheduled at the following time windows:

```python
ALLOWED_SLOTS = {
    "Saturday":   [(18, 0, 20, 0), (20, 30, 22, 30)],
    "Sunday":     [(11, 0, 13, 0), (16, 0, 18, 0), (20, 30, 22, 30)],
    "Monday":     [(20, 0, 22, 0)],
    "Wednesday":  [(20, 30, 22, 30), (21, 30, 23, 30)],
    "Thursday":   [(20, 30, 22, 30), (21, 30, 23, 30)],
}
```

### 🕒 66-Hour Rule

Teams must rest for at least 66 hours between two matches.  
This prevents scheduling back-to-back games and simulates realistic sports calendars.

### 🔁 No Overlapping

A team cannot be scheduled to play two matches at the same time.

---

## 🧠 Assumptions & Shortcuts

- Only basic team and match models are implemented — no player-level data  
- No timezone handling yet — datetimes are naive  
- Authentication and roles are not yet included  
- No frontend — this is backend-only  
- MongoDB must be running locally at `localhost:27017` (or use Docker)  
- Data validation focuses on business rules rather than form inputs  

---

## 🚧 What Could Be Improved With More Time

- ➕ Round number to better organize matches within league structure  
- ➕ Create full calendar feature to auto-generate full season fixtures  
- ➕ Match scoring system with win/loss/tie logic  
- ➕ Pagination for GraphQL queries  
- ➕ Advanced tests focused on edge cases in scheduling  
- 🚀 Deploy to cloud using Kubernetes (AWS EKS or Azure AKS)  
- 🔁 CI/CD pipeline using GitHub Actions or GitLab CI  
- 📱 Frontend using Flutter or React  
- 🔐 Authentication and authorization (JWT/OAuth)  

---

## 🐳 Docker Usage (Optional)

### Build the Image

```bash
docker build -t areena-api .
```

### Run the Container

```bash
docker run -p 5000:5000 areena-api
```

Visit the API at: [http://localhost:5000/graphql](http://localhost:5000/graphql)

---

## ✅ Continuous Integration

![CI](https://github.com/PMprojetos/Areena_Match_Making/actions/workflows/docker-ci-pipeline.yml/badge.svg)

This project uses **GitHub Actions** to automate build and test steps on every `push` or `pull request` to the `main` branch.

### 🧪 What the CI Pipeline Does

- ✅ Checks out the code
- ✅ Sets up Python 3.11
- ✅ Builds the Docker image
- ✅ Installs dependencies and runs tests with `pytest`
- ✅ Pushes the Docker image to Docker Hub

### ⚠️ Why Tests Are Allowed to Fail in CI

Since the project depends on a **locally running MongoDB instance**, tests that rely on database access will fail inside GitHub Actions (which does not include MongoDB by default).

To allow the pipeline to continue (e.g., for Docker build and push), we include:

```yaml
continue-on-error: true
```

This ensures:

- Tests are still executed and visible in the logs
- The build process continues for non-test steps
- This is a **temporary workaround** until CI has a working MongoDB environment

Locally (with MongoDB on `localhost:27017`), the tests pass and validate the full scheduling logic.

### 🛠️ Future CI Improvements

I plan to upgrade the test environment by including a MongoDB service in CI:

```yaml
services:
  mongo:
    image: mongo:6
    ports:
      - 27017:27017
```

This way, GitHub Actions will spin up a MongoDB container during testing, removing the need for `continue-on-error`.

Alternatively, a `docker-compose` setup could ensure both the app and database run together in CI and local dev.

---

## 🧰 Tech Stack

This project uses the following technologies:

### 👨‍💻 Backend

- **Python 3.11**
- **Flask** – Web framework for handling requests
- **Graphene** – Python GraphQL implementation
- **MongoEngine** – ODM for MongoDB integration

### 🗄️ Database

- **MongoDB** – Document database, expected to run on `localhost:27017`  
- Can be run locally or via Docker (see Docker section)

### 🧪 Testing

- **Pytest** – For unit and integration tests
- Tests include validation of scheduling rules and API behaviors

### 🐳 DevOps

- **Docker** – Containerization of the app for consistent builds
- **GitHub Actions** – CI/CD for automatic testing and Docker builds
- **Docker Hub** – Stores the built image for deployment and sharing

### 🔌 APIs & Communication

- **GraphQL** – Flexible API layer for querying and mutating match and team data
- Served via `/graphql` endpoint

---


