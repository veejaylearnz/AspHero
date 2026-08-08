# Stock Portfolio Management System

This Python module provides a class-based portfolio manager using PostgreSQL as the backend.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a PostgreSQL database and user.
3. Set environment variables for PostgreSQL connection:

```bash
set PGHOST=localhost
set PGPORT=5432
set PGDATABASE=portfolio_db
set PGUSER=postgres
set PGPASSWORD=your_password
```

4. Run the portfolio app:

```bash
python portfolio_system.py
```

## Commands

- `buy SYMBOL QUANTITY PRICE` - add shares to the portfolio.
- `sell SYMBOL QUANTITY PRICE` - remove shares from the portfolio.
- `holdings` - display current holdings.
- `history` - display transaction history.
- `summary` - show portfolio summary.
- `help` - show command help.
- `exit` - quit the app.

## Notes

- The system creates PostgreSQL tables automatically on first run.
- It stores portfolios, holdings, and transactions in PostgreSQL.
- Modify `portfolio_system.py` to add ticker price lookup or multi-portfolio support.
