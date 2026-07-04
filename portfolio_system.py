"""Stock Portfolio Management System with PostgreSQL backend.

Usage:
  1. Install dependencies: pip install -r requirements.txt
  2. Set PostgreSQL connection env vars:
     PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
  3. Run: python portfolio_system.py

This module defines classes for portfolio and transaction management and stores
portfolio data in PostgreSQL.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional

import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor


class DatabaseManager:
    def __init__(self, host: str = None, port: int = None, dbname: str = None, user: str = None, password: str = None):
        self.host = host or os.getenv("PGHOST", "localhost")
        self.port = port or int(os.getenv("PGPORT", "5432"))
        self.dbname = dbname or os.getenv("PGDATABASE", "stocks")
        self.user = user or os.getenv("PGUSER", "postgres")
        self.password = password or os.getenv("PGPASSWORD", "admin")
        self.connection = None

    def connect(self):
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
            )
        return self.connection

    def execute(self, query: str, params: tuple = (), commit: bool = False):
        conn = self.connect()
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, params)
            if commit:
                conn.commit()
            return cursor

    def fetchall(self, query: str, params: tuple = ()):  # pragma: no cover
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def fetchone(self, query: str, params: tuple = ()):  # pragma: no cover
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def initialize_schema(self):
        create_portfolios = """
        CREATE TABLE IF NOT EXISTS portfolios (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """

        create_holdings = """
        CREATE TABLE IF NOT EXISTS holdings (
            id SERIAL PRIMARY KEY,
            portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
            symbol TEXT NOT NULL,
            quantity NUMERIC NOT NULL CHECK (quantity >= 0),
            average_price NUMERIC NOT NULL CHECK (average_price >= 0),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            UNIQUE(portfolio_id, symbol)
        )
        """

        create_transactions = """
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
            symbol TEXT NOT NULL,
            transaction_type TEXT NOT NULL CHECK (transaction_type IN ('BUY', 'SELL')),
            quantity NUMERIC NOT NULL CHECK (quantity > 0),
            price NUMERIC NOT NULL CHECK (price >= 0),
            total NUMERIC NOT NULL CHECK (total >= 0),
            transaction_date TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """

        self.execute(create_portfolios, commit=True)
        self.execute(create_holdings, commit=True)
        self.execute(create_transactions, commit=True)

    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()


@dataclass
class StockHolding:
    symbol: str
    quantity: Decimal
    average_price: Decimal

    def market_value(self, current_price: Decimal) -> Decimal:
        return self.quantity * current_price


@dataclass
class Transaction:
    symbol: str
    transaction_type: str
    quantity: Decimal
    price: Decimal
    total: Decimal
    transaction_date: datetime


class Portfolio:
    def __init__(self, db: DatabaseManager, name: str = "default"):
        self.db = db
        self.name = name.strip().upper()
        self.id = self._ensure_portfolio_exists()

    def _ensure_portfolio_exists(self) -> int:
        result = self.db.fetchone("SELECT id FROM portfolios WHERE name = %s", (self.name,))
        if result:
            return result["id"]
        cursor = self.db.execute(
            "INSERT INTO portfolios (name) VALUES (%s) RETURNING id",
            (self.name,),
            commit=True,
        )
        return cursor.fetchone()["id"]

    def _normalize_symbol(self, symbol: str) -> str:
        return symbol.strip().upper()

    def _to_decimal(self, value) -> Decimal:
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Amount and price must be numeric values.")

    def buy(self, symbol: str, quantity, price):
        symbol = self._normalize_symbol(symbol)
        quantity = self._to_decimal(quantity)
        price = self._to_decimal(price)
        if quantity <= 0 or price < 0:
            raise ValueError("Buy quantity must be positive and price cannot be negative.")

        holding = self.db.fetchone(
            "SELECT quantity, average_price FROM holdings WHERE portfolio_id = %s AND symbol = %s",
            (self.id, symbol),
        )

        if holding:
            existing_quantity = Decimal(str(holding["quantity"]))
            existing_avg_price = Decimal(str(holding["average_price"]))
            total_cost = existing_quantity * existing_avg_price + quantity * price
            new_quantity = existing_quantity + quantity
            new_avg_price = total_cost / new_quantity
            self.db.execute(
                "UPDATE holdings SET quantity = %s, average_price = %s, updated_at = NOW() WHERE portfolio_id = %s AND symbol = %s",
                (new_quantity, new_avg_price, self.id, symbol),
                commit=True,
            )
        else:
            self.db.execute(
                "INSERT INTO holdings (portfolio_id, symbol, quantity, average_price) VALUES (%s, %s, %s, %s)",
                (self.id, symbol, quantity, price, ),
                commit=True,
            )

        self._record_transaction(symbol, "BUY", quantity, price)

    def sell(self, symbol: str, quantity, price):
        symbol = self._normalize_symbol(symbol)
        quantity = self._to_decimal(quantity)
        price = self._to_decimal(price)
        if quantity <= 0 or price < 0:
            raise ValueError("Sell quantity must be positive and price cannot be negative.")

        holding = self.db.fetchone(
            "SELECT quantity, average_price FROM holdings WHERE portfolio_id = %s AND symbol = %s",
            (self.id, symbol),
        )
        if not holding:
            raise ValueError(f"No holdings found for symbol {symbol}.")

        existing_quantity = Decimal(str(holding["quantity"]))
        if quantity > existing_quantity:
            raise ValueError("Cannot sell more shares than currently held.")

        new_quantity = existing_quantity - quantity
        if new_quantity == 0:
            self.db.execute(
                "DELETE FROM holdings WHERE portfolio_id = %s AND symbol = %s",
                (self.id, symbol),
                commit=True,
            )
        else:
            self.db.execute(
                "UPDATE holdings SET quantity = %s, updated_at = NOW() WHERE portfolio_id = %s AND symbol = %s",
                (new_quantity, self.id, symbol),
                commit=True,
            )

        self._record_transaction(symbol, "SELL", quantity, price)

    def _record_transaction(self, symbol: str, transaction_type: str, quantity: Decimal, price: Decimal):
        total = quantity * price
        self.db.execute(
            "INSERT INTO transactions (portfolio_id, symbol, transaction_type, quantity, price, total) VALUES (%s, %s, %s, %s, %s, %s)",
            (self.id, symbol, transaction_type, quantity, price, total),
            commit=True,
        )

    def get_holdings(self) -> List[StockHolding]:
        rows = self.db.fetchall(
            "SELECT symbol, quantity, average_price FROM holdings WHERE portfolio_id = %s ORDER BY symbol",
            (self.id,),
        )
        return [StockHolding(symbol=row["symbol"], quantity=Decimal(str(row["quantity"])), average_price=Decimal(str(row["average_price"]))) for row in rows]

    def get_transaction_history(self) -> List[Transaction]:
        rows = self.db.fetchall(
            "SELECT symbol, transaction_type, quantity, price, total, transaction_date FROM transactions WHERE portfolio_id = %s ORDER BY transaction_date DESC",
            (self.id,),
        )
        return [Transaction(
            symbol=row["symbol"],
            transaction_type=row["transaction_type"],
            quantity=Decimal(str(row["quantity"])),
            price=Decimal(str(row["price"])),
            total=Decimal(str(row["total"])),
            transaction_date=row["transaction_date"],
        ) for row in rows]

    def get_summary(self, current_prices: Optional[Dict[str, Decimal]] = None) -> Dict[str, Decimal]:
        holdings = self.get_holdings()
        cost_basis = sum(h.quantity * h.average_price for h in holdings)
        market_value = Decimal("0")

        for holding in holdings:
            price = current_prices.get(holding.symbol, holding.average_price) if current_prices else holding.average_price
            market_value += holding.market_value(price)

        unrealized_gain = market_value - cost_basis

        return {
            "cost_basis": cost_basis,
            "market_value": market_value,
            "unrealized_gain": unrealized_gain,
            "total_holdings": Decimal(len(holdings)),
        }


class PortfolioCLI:
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    def run(self):
        print("Stock Portfolio Management System")
        print("Connected portfolio:", self.portfolio.name)
        print("Type 'help' to see commands. Type 'exit' to quit.")

        while True:
            try:
                command = input("portfolio> ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                break

            if not command:
                continue
            if command in {"exit", "quit"}:
                break
            if command == "help":
                self._print_help()
                continue
            self._handle_command(command)

    def _print_help(self):
        print(
            "Commands:\n"
            "  buy SYMBOL QUANTITY PRICE    - Buy shares for a stock\n"
            "  sell SYMBOL QUANTITY PRICE   - Sell shares for a stock\n"
            "  holdings                    - Show current holdings\n"
            "  history                     - Show transaction history\n"
            "  summary                     - Show portfolio summary\n"
            "  help                        - Show this help message\n"
            "  exit                        - Quit the application"
        )

    def _handle_command(self, command: str):
        parts = command.split()
        action = parts[0]

        try:
            if action == "buy" and len(parts) == 4:
                self.portfolio.buy(parts[1], parts[2], parts[3])
                print(f"Bought {parts[2]} shares of {parts[1].upper()} at {parts[3]} each.")
            elif action == "sell" and len(parts) == 4:
                self.portfolio.sell(parts[1], parts[2], parts[3])
                print(f"Sold {parts[2]} shares of {parts[1].upper()} at {parts[3]} each.")
            elif action == "holdings":
                self._print_holdings()
            elif action == "history":
                self._print_history()
            elif action == "summary":
                self._print_summary()
            else:
                print("Unknown command or wrong syntax. Type 'help' for commands.")
        except Exception as exc:
            print(f"Error: {exc}")

    def _print_holdings(self):
        holdings = self.portfolio.get_holdings()
        if not holdings:
            print("No holdings in portfolio.")
            return
        print(f"{'SYMBOL':<10}{'QTY':>10}{'AVG PRICE':>15}{'POSITION VALUE':>18}")
        for holding in holdings:
            position_value = holding.quantity * holding.average_price
            print(f"{holding.symbol:<10}{holding.quantity:>10}{holding.average_price:>15}{position_value:>18}")

    def _print_history(self):
        history = self.portfolio.get_transaction_history()
        if not history:
            print("No transactions yet.")
            return
        print(f"{'DATE':<20}{'TYPE':<8}{'SYMBOL':<10}{'QTY':>10}{'PRICE':>12}{'TOTAL':>15}")
        for tx in history:
            date_str = tx.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{date_str:<20}{tx.transaction_type:<8}{tx.symbol:<10}{tx.quantity:>10}{tx.price:>12}{tx.total:>15}")

    def _print_summary(self):
        summary = self.portfolio.get_summary()
        print("Portfolio Summary")
        print(f"  Cost Basis: {summary['cost_basis']}")
        print(f"  Market Value: {summary['market_value']}")
        print(f"  Unrealized Gain: {summary['unrealized_gain']}")
        print(f"  Total Holdings: {summary['total_holdings']}")


def main():
    db = DatabaseManager()
    try:
        db.connect()
        db.initialize_schema()
        portfolio = Portfolio(db, name="Main")
        cli = PortfolioCLI(portfolio)
        cli.run()
    finally:
        db.close()


if __name__ == "__main__":
    main()
