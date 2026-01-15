"""
Dynamic pricing engine for SarScope.
Implements undercutting logic and price optimization strategies.
"""

from typing import List, Optional, Tuple

from sarscope.core.models import Product, PricingOpportunity
from sarscope.core.notifier import NotificationManager
from sarscope.config import UNDERCUTTING_MARGIN, MIN_PRICE_THRESHOLD
from sarscope.utils.logger import logger


class PricingEngine:
    """Dynamic pricing engine with undercutting logic."""
    
    def __init__(self) -> None:
        """Initialize pricing engine."""
        logger.info("Pricing Engine initialized")
    
    @staticmethod
    def calculate_new_price(
        product: Product,
        competitor_prices: List[float],
        safety_margin: float = UNDERCUTTING_MARGIN,
    ) -> Tuple[float, str]:
        """
        Calculate optimal price based on competitor prices.
        
        Strategy:
        1. Find minimum competitor price
        2. Set our price below it by safety_margin
        3. Ensure it doesn't go below product's min_price (floor limit)
        4. Return new price and reasoning
        
        Args:
            product: Product instance
            competitor_prices: List of competitor prices
            safety_margin: Amount to undercut by (default: $1.00)
            
        Returns:
            Tuple of (new_price, reason_message)
        """
        if not competitor_prices:
            logger.warning(f"No competitor prices for product {product.id}")
            return product.my_price, "NO_COMPETITOR_DATA"
        
        # Remove invalid prices (None, negative, zero)
        valid_prices = [p for p in competitor_prices if p and p > 0]
        
        if not valid_prices:
            logger.warning(f"No valid competitor prices for product {product.id}")
            return product.my_price, "NO_VALID_COMPETITOR_DATA"
        
        min_competitor_price = min(valid_prices)
        max_competitor_price = max(valid_prices)
        avg_competitor_price = sum(valid_prices) / len(valid_prices)
        
        logger.debug(
            f"Product {product.id}: min=${min_competitor_price:.2f}, "
            f"max=${max_competitor_price:.2f}, avg=${avg_competitor_price:.2f}"
        )
        
        # Strategy: Undercut the minimum price
        suggested_price = min_competitor_price - safety_margin
        
        # Apply floor limit
        if suggested_price < product.min_price:
            logger.warning(
                f"Product {product.id}: Suggested price ${suggested_price:.2f} "
                f"below floor limit ${product.min_price:.2f}"
            )
            return product.min_price, "FLOOR_LIMIT_REACHED"
        
        # Check if current price is already optimal
        if suggested_price >= product.my_price:
            return product.my_price, "PRICE_OPTIMAL"
        
        # Verify margin constraints
        margin = (suggested_price - product.cost) / suggested_price if suggested_price > 0 else 0
        
        if margin < 0:
            logger.warning(
                f"Product {product.id}: Suggested price ${suggested_price:.2f} "
                f"would result in loss (cost: ${product.cost:.2f})"
            )
            return product.min_price, "COST_PROTECTION_ENGAGED"
        
        reason = f"UNDERCUT_BY_${safety_margin:.2f}"
        logger.info(
            f"Product {product.id}: New price ${suggested_price:.2f} "
            f"(competitor min: ${min_competitor_price:.2f}) - {reason}"
        )
        
        return suggested_price, reason
    
    @staticmethod
    def identify_opportunities(
        products: List[Product],
        competitor_data: dict,
    ) -> List[PricingOpportunity]:
        """
        Identify pricing opportunities across all products.
        
        Args:
            products: List of Product instances
            competitor_data: Dict mapping product_id to list of competitor prices
            
        Returns:
            List of PricingOpportunity objects
        """
        opportunities = []
        
        for product in products:
            competitor_prices = competitor_data.get(product.id, [])
            
            if not competitor_prices:
                continue
            
            valid_prices = [p for p in competitor_prices if p and p > 0]
            if not valid_prices:
                continue
            
            min_competitor_price = min(valid_prices)
            suggested_price, reason = PricingEngine.calculate_new_price(
                product, valid_prices
            )
            
            # Only create opportunity if price change is significant
            if suggested_price != product.my_price:
                potential_loss = product.my_price - suggested_price
                
                opportunity = PricingOpportunity(
                    product_id=product.id,
                    product_name=product.name,
                    current_price=product.my_price,
                    suggested_price=suggested_price,
                    min_competitor_price=min_competitor_price,
                    potential_loss=potential_loss,
                    reason=reason,
                )
                
                opportunities.append(opportunity)
                logger.info(f"Opportunity identified: {opportunity}")
                
                # Fiyat fırsatı bulunduğunda mail gönder (Entegrasyon)
                try:
                    notifier = NotificationManager()
                    notifier.send_alert(
                        product_name=product.name,
                        my_price=product.my_price,
                        competitor_price=min_competitor_price,
                        url="Otomatik Analiz (Panelden kontrol ediniz)"
                    )
                except Exception as e:
                    logger.error(f"Mail gönderilemedi: {e}")
        
        return opportunities
    
    @staticmethod
    def calculate_margin(cost: float, selling_price: float) -> float:
        """
        Calculate profit margin percentage.
        
        Args:
            cost: Product cost
            selling_price: Selling price
            
        Returns:
            Margin as percentage (0-100)
        """
        if selling_price <= 0:
            return 0
        
        margin = ((selling_price - cost) / selling_price) * 100
        return max(0, margin)  # Don't return negative margins
    
    @staticmethod
    def validate_price(
        price: float,
        min_price: float,
        cost: float,
        product_id: int,
    ) -> Tuple[bool, str]:
        """
        Validate if a price meets business constraints.
        
        Args:
            price: Price to validate
            min_price: Minimum allowed price
            cost: Product cost
            product_id: Product ID for logging
            
        Returns:
            Tuple of (is_valid, reason_message)
        """
        if price <= 0:
            return False, f"Price must be positive (got ${price:.2f})"
        
        if price < min_price:
            return False, f"Price ${price:.2f} below minimum ${min_price:.2f}"
        
        if price < cost:
            return False, f"Price ${price:.2f} below cost ${cost:.2f}"
        
        return True, "Price is valid"
    
    @staticmethod
    def apply_bulk_pricing(
        base_price: float,
        quantity: int,
        discount_tiers: dict = None,
    ) -> float:
        """
        Apply bulk pricing discounts.
        
        Args:
            base_price: Base unit price
            quantity: Quantity ordered
            discount_tiers: Dict mapping quantity thresholds to discounts
                           e.g., {10: 0.05, 50: 0.10, 100: 0.15}
            
        Returns:
            Adjusted price for bulk order
        """
        if discount_tiers is None:
            discount_tiers = {10: 0.05, 50: 0.10, 100: 0.15}
        
        discount = 0
        for threshold in sorted(discount_tiers.keys(), reverse=True):
            if quantity >= threshold:
                discount = discount_tiers[threshold]
                break
        
        adjusted_price = base_price * (1 - discount)
        logger.debug(
            f"Bulk pricing: {quantity} units, "
            f"discount={discount*100:.1f}%, price=${adjusted_price:.2f}"
        )
        
        return adjusted_price
