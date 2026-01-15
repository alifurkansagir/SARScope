"""
Example usage of SarScope components programmatically.
This demonstrates how to use SarScope as a library in your own projects.
"""

from sarscope.database import DatabaseManager
from sarscope.core.models import Product
from sarscope.core.scraper import SarScopeScraper
from sarscope.core.pricer import PricingEngine
from sarscope.core.trend_hunter import TrendHunter
from sarscope.utils.logger import logger


def example_1_basic_product_management():
    """Example 1: Add products and competitors, retrieve data"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Product Management")
    print("=" * 60)
    
    # Initialize database
    db = DatabaseManager()
    
    # Add a product
    product_id = db.add_product(
        name="Premium Wireless Headphones",
        sku="WH-PREM-001",
        my_price=129.99,
        min_price=89.99,
        cost=45.00,
        target_margin=0.50,
    )
    print(f"✓ Product added: ID={product_id}")
    
    # Add competitors
    competitor_urls = [
        "https://amazon.com/s?k=wireless-headphones",
        "https://bestbuy.com/site/searchpage.jsp?st=wireless+headphones",
        "https://ebay.com/sch/i.html?_nkw=wireless+headphones",
    ]
    
    for url in competitor_urls:
        comp_id = db.add_competitor(product_id, url)
        print(f"✓ Competitor added: {url}")
    
    # Retrieve product
    product = db.get_product(product_id)
    print(f"\nRetrieved Product: {product}")
    print(f"  Current Margin: {product.current_margin()*100:.1f}%")
    
    # Get all competitors
    competitors = db.get_competitors(product_id)
    print(f"\nCompetitors ({len(competitors)}):")
    for comp in competitors:
        print(f"  - {comp.url}")
    
    print()


def example_2_price_monitoring():
    """Example 2: Fetch and monitor competitor prices"""
    print("=" * 60)
    print("EXAMPLE 2: Price Monitoring")
    print("=" * 60)
    
    db = DatabaseManager()
    scraper = SarScopeScraper()
    
    # Get first product
    products = db.get_all_products()
    if not products:
        print("No products in database. Add products first!")
        return
    
    product = products[0]
    print(f"Monitoring: {product.name}")
    print(f"Your Price: ${product.my_price:.2f}")
    
    # Get competitors and fetch prices
    competitors = db.get_competitors(product.id)
    print(f"\nFetching {len(competitors)} competitor prices...\n")
    
    prices = []
    for comp in competitors:
        print(f"Checking: {comp.url}")
        
        # Fetch price (with anti-detection delays)
        price = scraper.fetch_price(comp.url)
        
        if price:
            prices.append(price)
            print(f"  ✓ Price: ${price:.2f}")
            
            # Update database
            db.update_competitor_price(comp.id, price, "active")
        else:
            print(f"  ✗ Failed to extract price")
            db.update_competitor_price(comp.id, None, "error")
    
    # Show price summary
    if prices:
        print(f"\nPrice Summary:")
        print(f"  Min Competitor: ${min(prices):.2f}")
        print(f"  Max Competitor: ${max(prices):.2f}")
        print(f"  Avg Competitor: ${sum(prices)/len(prices):.2f}")
    
    scraper.close()
    print()


def example_3_dynamic_pricing():
    """Example 3: Calculate optimal prices"""
    print("=" * 60)
    print("EXAMPLE 3: Dynamic Pricing Engine")
    print("=" * 60)
    
    db = DatabaseManager()
    pricer = PricingEngine()
    
    # Get all products
    products = db.get_all_products()
    
    print(f"Analyzing {len(products)} product(s) for pricing opportunities...\n")
    
    # Collect competitor data
    competitor_data = {}
    for product in products:
        competitors = db.get_competitors(product.id)
        prices = [c.last_price for c in competitors if c.last_price]
        competitor_data[product.id] = prices
    
    # Identify opportunities
    opportunities = pricer.identify_opportunities(products, competitor_data)
    
    if opportunities:
        print(f"Found {len(opportunities)} pricing opportunities:\n")
        for opp in opportunities:
            print(f"Product: {opp.product_name}")
            print(f"  Current Price:        ${opp.current_price:.2f}")
            print(f"  Suggested Price:      ${opp.suggested_price:.2f}")
            print(f"  Min Competitor:       ${opp.min_competitor_price:.2f}")
            print(f"  Potential Loss/Gain:  ${-opp.potential_loss:.2f}")
            print(f"  Reason:               {opp.reason}")
            print()
    else:
        print("No pricing opportunities found. Your prices are optimal!")
    
    print()


def example_4_trend_hunting():
    """Example 4: Hunt for market trends"""
    print("=" * 60)
    print("EXAMPLE 4: Trend Hunter")
    print("=" * 60)
    
    db = DatabaseManager()
    trend_hunter = TrendHunter()
    
    # Example category URL (would be real in production)
    category_url = "https://amazon.com/s?k=wireless+headphones&bbn=172659&_bfs=1"
    
    print(f"Scanning category: {category_url}\n")
    
    # Scan category
    best_sellers = trend_hunter.scan_category(category_url)
    print(f"Found {len(best_sellers)} best-selling products\n")
    
    if best_sellers:
        print("Top 5 Best Sellers:")
        for product in best_sellers[:5]:
            print(f"  #{product['rank']}: {product['name']}")
    
    # Match against existing inventory
    existing_products = db.get_all_products()
    
    if existing_products:
        print(f"\nMatching against {len(existing_products)} existing products...\n")
        opportunities = trend_hunter.match_opportunities(
            best_sellers, existing_products
        )
        
        if opportunities:
            print(f"Found {len(opportunities)} new market opportunities:\n")
            for opp in opportunities[:5]:
                velocity_emoji = "🔥" if opp.estimated_sales_velocity == "high" else "⚡"
                print(f"{velocity_emoji} {opp.product_name}")
                print(f"   Rank: #{opp.rank}, Match: {opp.match_score:.0f}%")
        else:
            print("All best-sellers are already in your inventory.")
    
    trend_hunter.close()
    print()


def example_5_dashboard_analytics():
    """Example 5: View dashboard analytics"""
    print("=" * 60)
    print("EXAMPLE 5: Dashboard Analytics")
    print("=" * 60)
    
    db = DatabaseManager()
    
    # Get statistics
    stats = db.get_dashboard_stats()
    
    print(f"SarScope Dashboard Statistics:")
    print(f"  📦 Total Products:          {stats['total_products']}")
    print(f"  🔗 Active Competitors:      {stats['total_competitors']}")
    print(f"  📈 Average Margin:          {stats['average_margin']:.1f}%")
    print(f"  💰 Total Inventory Value:   ${stats['total_inventory_value']:.2f}")
    
    # Get all products with details
    products = db.get_all_products()
    
    if products:
        print(f"\nProduct Inventory ({len(products)} products):")
        print("-" * 60)
        
        for product in products:
            competitors = db.get_competitors(product.id)
            competitor_prices = [c.last_price for c in competitors if c.last_price]
            
            print(f"\n{product.name}")
            print(f"  SKU: {product.sku}")
            print(f"  Your Price:     ${product.my_price:.2f}")
            print(f"  Min Price:      ${product.min_price:.2f}")
            print(f"  Cost:           ${product.cost:.2f}")
            print(f"  Margin:         {product.current_margin()*100:.1f}%")
            print(f"  Competitors:    {len(competitors)} tracked")
            
            if competitor_prices:
                print(f"  Price Range:    ${min(competitor_prices):.2f} - ${max(competitor_prices):.2f}")
            
            # Show price history
            history = db.get_price_history(product.id, limit=3)
            if history:
                print(f"  Recent Changes:")
                for h in history:
                    print(f"    - ${h['old_price']:.2f} → ${h['new_price']:.2f} ({h['reason']})")
    
    print()


def example_6_programmatic_workflow():
    """Example 6: Complete workflow"""
    print("=" * 60)
    print("EXAMPLE 6: Complete Workflow")
    print("=" * 60)
    
    db = DatabaseManager()
    scraper = SarScopeScraper()
    pricer = PricingEngine()
    
    # Step 1: Get product
    products = db.get_all_products()
    if not products:
        print("No products found. Add products first!")
        scraper.close()
        return
    
    product = products[0]
    print(f"Step 1: Processing {product.name}")
    
    # Step 2: Fetch competitor prices
    print(f"Step 2: Fetching competitor prices...")
    competitors = db.get_competitors(product.id)
    prices = []
    
    for comp in competitors:
        price = scraper.fetch_price(comp.url)
        if price:
            prices.append(price)
            db.update_competitor_price(comp.id, price, "active")
    
    print(f"  Found {len(prices)} prices")
    
    # Step 3: Calculate new price
    if prices:
        print(f"Step 3: Calculating optimal price...")
        new_price, reason = pricer.calculate_new_price(product, prices)
        
        # Step 4: Validate price
        print(f"Step 4: Validating price constraints...")
        is_valid, msg = pricer.validate_price(
            new_price, product.min_price, product.cost, product.id
        )
        
        if is_valid:
            print(f"Step 5: Price change would be applied:")
            print(f"  Old Price: ${product.my_price:.2f}")
            print(f"  New Price: ${new_price:.2f}")
            print(f"  Reason:    {reason}")
            print(f"  Action:    {'UPDATE' if new_price != product.my_price else 'NO CHANGE'}")
        else:
            print(f"  ✗ Price validation failed: {msg}")
    
    scraper.close()
    print()


def run_all_examples():
    """Run all examples"""
    try:
        example_1_basic_product_management()
        # Uncomment to run other examples:
        # example_2_price_monitoring()
        # example_3_dynamic_pricing()
        # example_4_trend_hunting()
        # example_5_dashboard_analytics()
        # example_6_programmatic_workflow()
        
        print("=" * 60)
        print("✓ All examples completed!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Example error: {e}", exc_info=True)
        print(f"Error: {e}")


if __name__ == "__main__":
    print("\n")
    run_all_examples()
