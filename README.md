# Installation

Note this assumes you already have Python 3.12 and postgres installed.

```bash
pip install -r requirements.txt
```

# Setup
This also assumes you've already created a database in postgres with a user who has full access to it.
Create a `.env` file in the root directory and add the following:

```bash
DB_NAME = "your_db_name"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_HOST = "localhost"
DB_PORT = "5432"
```

# Run

```bash
python main.py
```
