"""
Trend Hunter module for SarScope.
Identifies market trends and best-seller opportunities.
"""

from typing import List, Dict, Optional
from fuzzywuzzy import fuzz
from fuzzywuzzy import process as fuzz_process

from sarscope.core.models import TrendOpportunity, Product
from sarscope.core.scraper import SarScopeScraper
from sarscope.config import FUZZY_MATCH_THRESHOLD, TREND_WATCHLIST
from sarscope.utils.logger import logger
from sarscope.core.notifier import NotificationManager


class TrendHunter:
    """Identifies and analyzes market trends and opportunities."""
    
    def __init__(self) -> None:
        """Initialize trend hunter."""
        self.scraper = SarScopeScraper()
        logger.info("Trend Hunter initialized")
    
    def scan_category(self, url: str) -> List[dict]:
        """
        Scan a category page for best-sellers.
        
        Args:
            url: Category or best-seller list URL
            
        Returns:
            List of best-seller products with rank and name
        """
        logger.info(f"Scanning category: {url}")
        return self.scraper.fetch_best_sellers(url)

    def run_daily_scan_and_report(self):
        """Config'deki tüm kategorileri tarar ve mail atar."""
        logger.info("Günlük otomatik tarama başlatılıyor...")
        report_data = {}
        
        for category_name, url in TREND_WATCHLIST.items():
            print(f"\n🔎 Taranıyor: {category_name}...")
            products = self.scan_category(url)
            if products:
                report_data[category_name] = products
                print(f"✅ {len(products)} ürün bulundu.")
            else:
                print(f"❌ {category_name} için veri bulunamadı.")
        
        # Mail Gönderimi
        if report_data:
            print("\n📧 Rapor hazırlanıyor ve gönderiliyor...")
            notifier = NotificationManager()
            notifier.send_trend_report(report_data)
        else:
            logger.warning("Raporlanacak veri bulunamadı.")
    
    def match_opportunities(
        self,
        scraped_products: List[dict],
        existing_products: List[Product],
    ) -> List[TrendOpportunity]:
        """
        Match scraped products against existing inventory using fuzzy matching.
        
        Args:
            scraped_products: List of products from scraping
            existing_products: List of products in our database
            
        Returns:
            List of new opportunities found
        """
        opportunities = []
        existing_names = {p.name: p for p in existing_products}
        
        logger.info(f"Matching {len(scraped_products)} scraped products against {len(existing_products)} existing")
        
        for scraped in scraped_products:
            product_name = scraped.get("name", "Unknown")
            rank = scraped.get("rank", 999)
            
            # Check for exact match
            if product_name in existing_names:
                logger.debug(f"Product '{product_name}' already in inventory")
                continue
            
            # Fuzzy match against existing products
            best_match, best_score = fuzz_process.extractOne(
                product_name,
                existing_names.keys(),
                scorer=fuzz.token_set_ratio,
            )
            
            logger.debug(f"Fuzzy match for '{product_name}': {best_match} ({best_score}%)")
            
            # If no good match found, it's an opportunity
            if best_score < FUZZY_MATCH_THRESHOLD:
                # Estimate sales velocity based on rank
                if rank <= 10:
                    velocity = "high"
                elif rank <= 50:
                    velocity = "medium"
                else:
                    velocity = "low"
                
                opportunity = TrendOpportunity(
                    product_name=product_name,
                    rank=rank,
                    estimated_sales_velocity=velocity,
                    match_score=best_score,
                    category="Discovered",
                )
                
                opportunities.append(opportunity)
                logger.info(
                    f"New opportunity identified: {product_name} "
                    f"(rank #{rank}, velocity={velocity})"
                )
        
        return opportunities
    
    @staticmethod
    def analyze_trend(
        current_price: float,
        historical_prices: List[float],
        threshold: float = 0.10,
    ) -> Dict[str, any]:
        """
        Analyze price trend for a product.
        
        Args:
            current_price: Current price
            historical_prices: Historical price data
            threshold: Change threshold to flag as trend
            
        Returns:
            Dict with trend analysis
        """
        if not historical_prices:
            return {
                "trend": "no_data",
                "direction": None,
                "change_percent": 0,
                "severity": "none",
            }
        
        average_price = sum(historical_prices) / len(historical_prices)
        change_percent = (current_price - average_price) / average_price
        
        if abs(change_percent) < threshold:
            trend = "stable"
            severity = "low"
        elif change_percent > 0:
            trend = "increasing"
            severity = "high" if change_percent > 0.20 else "medium"
        else:
            trend = "decreasing"
            severity = "high" if change_percent < -0.20 else "medium"
        
        return {
            "trend": trend,
            "direction": "up" if change_percent > 0 else "down",
            "change_percent": abs(change_percent) * 100,
            "severity": severity,
            "average_price": average_price,
        }
    
    @staticmethod
    def identify_seasonal_patterns(
        price_history: List[dict],
        window_size: int = 4,
    ) -> Dict[str, any]:
        """
        Identify seasonal or cyclical price patterns.
        
        Args:
            price_history: Historical price data with timestamps
            window_size: Number of data points to consider for pattern
            
        Returns:
            Dict with pattern analysis
        """
        if len(price_history) < window_size:
            return {"pattern": "insufficient_data"}
        
        recent_prices = [p.get("new_price", 0) for p in price_history[:window_size]]
        
        # Check for increasing/decreasing pattern
        is_increasing = all(
            recent_prices[i] <= recent_prices[i+1]
            for i in range(len(recent_prices)-1)
        )
        is_decreasing = all(
            recent_prices[i] >= recent_prices[i+1]
            for i in range(len(recent_prices)-1)
        )
        
        if is_increasing:
            pattern = "upward_trend"
            recommendation = "Consider increasing price"
        elif is_decreasing:
            pattern = "downward_trend"
            recommendation = "Monitor competition"
        else:
            pattern = "cyclical"
            recommendation = "Price is volatile"
        
        return {
            "pattern": pattern,
            "recommendation": recommendation,
            "price_range": (min(recent_prices), max(recent_prices)),
        }
    
    def get_market_intelligence(self, category_url: str) -> Dict[str, any]:
        """
        Generate comprehensive market intelligence report.
        
        Args:
            category_url: URL of the category to analyze
            
        Returns:
            Dict with market analysis
        """
        logger.info(f"Generating market intelligence for: {category_url}")
        
        products = self.scan_category(category_url)
        
        if not products:
            logger.warning("No products found in category")
            return {"status": "error", "message": "No products found"}
        
        total_products = len(products)
        avg_rank = sum(p.get("rank", 999) for p in products) / total_products
        
        intelligence = {
            "url": category_url,
            "total_products_found": total_products,
            "average_rank": avg_rank,
            "top_products": products[:10] if len(products) >= 10 else products,
            "market_saturation": "high" if total_products > 1000 else "medium" if total_products > 100 else "low",
        }
        
        logger.info(
            f"Market intelligence: {total_products} products, "
            f"avg_rank={avg_rank:.1f}, saturation={intelligence['market_saturation']}"
        )
        
        return intelligence
    
    def close(self) -> None:
        """Clean up resources."""
        self.scraper.close()
        logger.info("Trend Hunter closed")
