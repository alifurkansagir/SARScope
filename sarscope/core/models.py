"""
Data models for SarScope.
Defines Product and Competitor dataclasses with type hints.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Product:
    """Represents a product in the watchlist."""
    
    id: int
    name: str
    sku: str
    my_price: float
    min_price: float
    cost: float
    target_margin: float
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self) -> None:
        """Validate product data after initialization."""
        if self.my_price <= 0:
            raise ValueError("my_price must be greater than 0")
        if self.min_price <= 0:
            raise ValueError("min_price must be greater than 0")
        if self.cost < 0:
            raise ValueError("cost cannot be negative")
        if self.target_margin < 0 or self.target_margin > 1:
            raise ValueError("target_margin must be between 0 and 1")
    
    def current_margin(self) -> float:
        """Calculate current margin as a percentage."""
        if self.my_price <= 0:
            return 0.0
        return (self.my_price - self.cost) / self.my_price
    
    def __repr__(self) -> str:
        """String representation of Product."""
        return f"Product(id={self.id}, name='{self.name}', sku='{self.sku}', price=${self.my_price:.2f})"


@dataclass
class Competitor:
    """Represents a competitor price for a product."""
    
    id: int
    product_id: int
    url: str
    last_price: Optional[float] = None
    status: str = "active"  # active, inactive, error
    checked_at: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self) -> None:
        """Validate competitor data after initialization."""
        if self.product_id <= 0:
            raise ValueError("product_id must be greater than 0")
        if not self.url.strip():
            raise ValueError("url cannot be empty")
        if self.last_price is not None and self.last_price < 0:
            raise ValueError("last_price cannot be negative")
        valid_statuses = {"active", "inactive", "error"}
        if self.status not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}")
    
    def is_price_available(self) -> bool:
        """Check if price data is available."""
        return self.last_price is not None and self.status == "active"
    
    def __repr__(self) -> str:
        """String representation of Competitor."""
        price_str = f"${self.last_price:.2f}" if self.last_price else "N/A"
        return f"Competitor(product_id={self.product_id}, price={price_str}, status='{self.status}')"


@dataclass
class PricingOpportunity:
    """Represents a pricing opportunity identified by the system."""
    
    product_id: int
    product_name: str
    current_price: float
    suggested_price: float
    min_competitor_price: float
    potential_loss: float
    reason: str
    created_at: datetime = field(default_factory=datetime.now)
    
    def __repr__(self) -> str:
        """String representation of PricingOpportunity."""
        return (
            f"PricingOpportunity(product='{self.product_name}', "
            f"current=${self.current_price:.2f}, suggested=${self.suggested_price:.2f}, "
            f"reason='{self.reason}')"
        )


@dataclass
class TrendOpportunity:
    """Represents a market trend opportunity."""
    
    product_name: str
    rank: int
    estimated_sales_velocity: str  # low, medium, high
    match_score: float  # 0-100 fuzzy match score
    category: str
    identified_at: datetime = field(default_factory=datetime.now)
    
    def __repr__(self) -> str:
        """String representation of TrendOpportunity."""
        return (
            f"TrendOpportunity(name='{self.product_name}', rank={self.rank}, "
            f"score={self.match_score:.0f}%, velocity='{self.estimated_sales_velocity}')"
        )
