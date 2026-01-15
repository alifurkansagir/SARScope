"""
SQLite database manager for SarScope.
Handles all database operations with type hints and error handling.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

from sarscope.config import DATABASE_PATH
from sarscope.core.models import Product, Competitor
from sarscope.utils.logger import logger


class DatabaseManager:
    """Manages SQLite database operations for SarScope."""
    
    def __init__(self, db_path: str = DATABASE_PATH) -> None:
        """Initialize database manager."""
        self.db_path = db_path
        self._initialize_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _initialize_database(self) -> None:
        """Create tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    sku TEXT NOT NULL UNIQUE,
                    my_price REAL NOT NULL,
                    min_price REAL NOT NULL,
                    cost REAL NOT NULL,
                    target_margin REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Competitors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS competitors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    last_price REAL,
                    status TEXT DEFAULT 'active',
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    UNIQUE(product_id, url)
                )
            """)
            
            # Pricing history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    old_price REAL NOT NULL,
                    new_price REAL NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                )
            """)
            
            logger.info("Database initialized successfully")
    
    # Product Operations
    def add_product(self, name: str, sku: str, my_price: float, 
                   min_price: float, cost: float, target_margin: float) -> int:
        """Add a new product to the watchlist."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO products 
                    (name, sku, my_price, min_price, cost, target_margin)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, sku, my_price, min_price, cost, target_margin))
                product_id = cursor.lastrowid
                logger.info(f"Product '{name}' added with ID: {product_id}")
                return product_id
        except sqlite3.IntegrityError as e:
            logger.error(f"Product already exists or duplicate SKU: {e}")
            raise
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Retrieve a product by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            if row:
                return Product(
                    id=row["id"],
                    name=row["name"],
                    sku=row["sku"],
                    my_price=row["my_price"],
                    min_price=row["min_price"],
                    cost=row["cost"],
                    target_margin=row["target_margin"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                )
            return None
    
    def get_all_products(self) -> List[Product]:
        """Retrieve all products from the watchlist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [
                Product(
                    id=row["id"],
                    name=row["name"],
                    sku=row["sku"],
                    my_price=row["my_price"],
                    min_price=row["min_price"],
                    cost=row["cost"],
                    target_margin=row["target_margin"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                )
                for row in rows
            ]
    
    def update_product_price(self, product_id: int, new_price: float, 
                            reason: str = "") -> None:
        """Update product price and record history."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get old price
                cursor.execute("SELECT my_price FROM products WHERE id = ?", (product_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Product {product_id} not found")
                
                old_price = row["my_price"]
                
                # Update price
                cursor.execute(
                    "UPDATE products SET my_price = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (new_price, product_id)
                )
                
                # Record history
                cursor.execute("""
                    INSERT INTO price_history (product_id, old_price, new_price, reason)
                    VALUES (?, ?, ?, ?)
                """, (product_id, old_price, new_price, reason))
                
                logger.info(f"Product {product_id} price updated: ${old_price:.2f} -> ${new_price:.2f}")
        except Exception as e:
            logger.error(f"Error updating product price: {e}")
            raise
    
    def delete_product(self, product_id: int) -> None:
        """Delete a product and its associated competitors."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            logger.info(f"Product {product_id} deleted")
    
    # Competitor Operations
    def add_competitor(self, product_id: int, url: str) -> int:
        """Add a competitor URL for a product."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO competitors (product_id, url)
                    VALUES (?, ?)
                """, (product_id, url))
                competitor_id = cursor.lastrowid
                logger.info(f"Competitor URL added for product {product_id}: {url}")
                return competitor_id
        except sqlite3.IntegrityError as e:
            logger.error(f"Competitor URL already exists: {e}")
            raise
    
    def get_competitors(self, product_id: int) -> List[Competitor]:
        """Retrieve all competitors for a product."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM competitors 
                WHERE product_id = ? 
                ORDER BY created_at DESC
            """, (product_id,))
            rows = cursor.fetchall()
            return [
                Competitor(
                    id=row["id"],
                    product_id=row["product_id"],
                    url=row["url"],
                    last_price=row["last_price"],
                    status=row["status"],
                    checked_at=datetime.fromisoformat(row["checked_at"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                for row in rows
            ]
    
    def update_competitor_price(self, competitor_id: int, price: Optional[float], 
                               status: str = "active") -> None:
        """Update competitor price data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE competitors 
                SET last_price = ?, status = ?, checked_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (price, status, competitor_id))
            logger.debug(f"Competitor {competitor_id} updated: price={price}, status={status}")
    
    def get_all_competitors(self) -> List[Tuple[int, int, str, Optional[float]]]:
        """Retrieve all competitors (for batch updates)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, product_id, url, last_price FROM competitors 
                WHERE status = 'active'
            """)
            return cursor.fetchall()
    
    # Price History Operations
    def get_price_history(self, product_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve price history for a product."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT old_price, new_price, reason, created_at 
                FROM price_history
                WHERE product_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (product_id, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    # Statistics Operations
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total products
            cursor.execute("SELECT COUNT(*) as count FROM products")
            total_products = cursor.fetchone()["count"]
            
            # Total competitors
            cursor.execute("SELECT COUNT(*) as count FROM competitors WHERE status = 'active'")
            total_competitors = cursor.fetchone()["count"]
            
            # Average margin
            cursor.execute("""
                SELECT AVG((my_price - cost) / my_price) as avg_margin 
                FROM products WHERE my_price > 0
            """)
            avg_margin = cursor.fetchone()["avg_margin"] or 0
            
            # Total inventory value
            cursor.execute("SELECT SUM(my_price) as total FROM products")
            total_value = cursor.fetchone()["total"] or 0
            
            return {
                "total_products": total_products,
                "total_competitors": total_competitors,
                "average_margin": avg_margin * 100,
                "total_inventory_value": total_value,
            }
