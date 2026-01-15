# SarScope - E-Commerce Intelligence Tool

A modular, production-ready CLI application for price monitoring, trend hunting, and dynamic pricing strategies.

## Features

### 🕵️ Price Patrol
- **Real-time Price Monitoring**: Track competitor prices across multiple URLs
- **Anti-Detection**: Random delays (3-7s) and rotating user agents to avoid blocking
- **Robust Extraction**: Regex-based price extraction with multiple fallback patterns
- **Price History**: Store and track price changes over time

### 🚀 Trend Hunter
- **Best-Seller Scanning**: Identify trending products in market categories
- **Fuzzy Matching**: Match discovered products against your inventory using AI fuzzy matching
- **Opportunity Detection**: Find gaps in your product portfolio with high-demand items
- **Velocity Analysis**: Estimate sales velocity based on ranking positions

### 💡 Dynamic Pricing
- **Undercutting Logic**: Automatically suggest prices to undercut competition by $1
- **Floor Limits**: Protect margin with configurable minimum price thresholds
- **Margin Protection**: Prevent pricing below cost
- **Bulk Pricing**: Support for quantity-based discount tiers

## Project Structure

```
sarscope/
├── main.py                 # CLI entry point with menu system
├── config.py              # Configuration & constants
├── database.py            # SQLite database manager
├── requirements.txt       # Python dependencies
├── core/
│   ├── models.py          # Data classes with type hints
│   ├── scraper.py         # Web scraping with anti-detection
│   ├── pricer.py          # Dynamic pricing engine
│   └── trend_hunter.py    # Market trend analysis
└── utils/
    └── logger.py          # Custom logging with colors
```

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

1. **Clone/Navigate to the project:**
```bash
cd /Users/alifurkansagir/Desktop/sartech/sarscope
```

2. **Create a virtual environment (recommended):**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python sarscope/main.py
```

This opens an interactive CLI menu:

```
╔═══════════════════════════════════════════╗
║             ★ SAR-SCOPE ★                ║
║   E-Commerce Intelligence Tool            ║
║   Version 1.0.0                           ║
╚═══════════════════════════════════════════╝

1. 🕵️  Start Price Patrol (Check Competitors)
2. 🚀 Run Trend Hunter (Scan Best Sellers)
3. ➕ Add Product to Watchlist
4. 📊 View Opportunities Report
5. 🚪 Exit
```

### Menu Options

#### 1. Price Patrol
- Checks all competitors for each product in your watchlist
- Extracts current prices
- Identifies pricing opportunities
- Suggests price adjustments to remain competitive

#### 2. Trend Hunter
- Scans a category URL for best-selling products
- Uses fuzzy matching to compare against your inventory
- Identifies new market opportunities you're not selling
- Ranks by sales velocity and demand

#### 3. Add Product to Watchlist
- Add new products to monitor
- Set your price, minimum price, cost, and target margin
- Add competitor URLs to track
- Stores data in SQLite database

#### 4. View Opportunities Report
- Dashboard with key statistics:
  - Number of products being tracked
  - Number of active competitors
  - Average profit margin
  - Total inventory value
- Product watchlist with pricing recommendations
- Current vs. suggested prices with visual indicators

#### 5. Exit
- Gracefully shutdown application
- Cleanup resources

## Architecture & Design Patterns

### Clean Architecture
- **Separation of Concerns**: Each module handles a specific responsibility
- **Type Hints**: Full type annotations for IDE support and error prevention
- **OOP Principles**: Classes and methods are well-organized and extensible

### Design Patterns Used
- **Singleton Pattern**: Database manager and logger use singleton pattern
- **Context Manager**: Database connections use context managers for resource cleanup
- **Dependency Injection**: Services injected through constructors
- **Strategy Pattern**: Multiple pricing strategies (undercutting, margin-based, etc.)

## Configuration

Edit [sarscope/config.py](sarscope/config.py) to customize:

```python
# Pricing
DEFAULT_MIN_MARGIN = 0.05  # 5% minimum margin
UNDERCUTTING_MARGIN = 1.0  # $1 below competitor
MIN_PRICE_THRESHOLD = 1.0

# Scraping
REQUEST_TIMEOUT = 10  # seconds
MIN_DELAY = 3  # seconds
MAX_DELAY = 7  # seconds
RETRY_ATTEMPTS = 3

# Fuzzy Matching
FUZZY_MATCH_THRESHOLD = 80  # 80% similarity
```

## Database Schema

### products table
- `id`: Auto-increment primary key
- `name`: Product name (unique)
- `sku`: Stock keeping unit (unique)
- `my_price`: Your selling price
- `min_price`: Minimum allowed price
- `cost`: Product cost
- `target_margin`: Target profit margin (0-1)
- `created_at`, `updated_at`: Timestamps

### competitors table
- `id`: Auto-increment primary key
- `product_id`: Foreign key to products
- `url`: Competitor URL
- `last_price`: Most recent scraped price
- `status`: 'active', 'inactive', or 'error'
- `checked_at`, `created_at`: Timestamps

### price_history table
- `id`: Auto-increment primary key
- `product_id`: Foreign key to products
- `old_price`: Previous price
- `new_price`: Updated price
- `reason`: Reason for change
- `created_at`: Timestamp

## API Usage (Programmatic)

```python
from database import DatabaseManager
from core.scraper import SarScopeScraper
from core.pricer import PricingEngine
from core.trend_hunter import TrendHunter

# Initialize components
db = DatabaseManager()
scraper = SarScopeScraper()
pricer = PricingEngine()
trend_hunter = TrendHunter()

# Add a product
product_id = db.add_product(
    name="Wireless Headphones",
    sku="WH-001",
    my_price=79.99,
    min_price=50.00,
    cost=30.00,
    target_margin=0.50
)

# Add competitor
db.add_competitor(product_id, "https://competitor1.com/product")

# Fetch price
price = scraper.fetch_price("https://competitor1.com/product")

# Calculate new price
product = db.get_product(product_id)
new_price, reason = pricer.calculate_new_price(product, [price])
print(f"New price: ${new_price:.2f} - {reason}")

# Update product price
db.update_product_price(product_id, new_price, reason)

# Get dashboard stats
stats = db.get_dashboard_stats()
print(stats)
```

## Logging

Logs are written to both console (colored) and file (`sarscope.log`):

```
2026-01-04 14:30:45 - sarscope - INFO - SarScope v1.0.0 initialized
2026-01-04 14:30:46 - sarscope - INFO - Starting Price Patrol...
2026-01-04 14:30:47 - sarscope - DEBUG - Fetching URL: https://competitor.com/product
2026-01-04 14:30:48 - sarscope - INFO - Successfully fetched (Status: 200)
```

### Log Levels
- `DEBUG`: Detailed information for diagnostics
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical failure messages

## Anti-Detection Features

To avoid being blocked by websites:

1. **Random Delays**: 3-7 second random delays between requests
2. **User Agent Rotation**: Cycles through pool of realistic user agents
3. **Session Persistence**: Maintains cookies and connection pooling
4. **Retry Strategy**: Automatic retries with exponential backoff
5. **Headers Spoofing**: Realistic browser headers (Accept, Accept-Language, etc.)

## Error Handling

The application includes comprehensive error handling:

- **Network Errors**: Graceful fallback when sites are unreachable
- **Parsing Errors**: Multiple regex patterns for price extraction
- **Database Errors**: Transaction rollback on constraint violations
- **Validation Errors**: Input validation with user-friendly error messages

## Performance Considerations

- **Database Indexing**: Primary and foreign keys automatically indexed
- **Connection Pooling**: Reuses HTTP connections
- **Lazy Loading**: Data loaded on-demand
- **Batch Operations**: Efficient bulk competitor updates

## Extensibility

### Adding New Pricing Strategies

```python
# In pricer.py
@staticmethod
def calculate_dynamic_price(product, competitor_prices, market_demand):
    # Your custom logic here
    pass
```

### Adding New Scraping Targets

```python
# Extend SarScopeScraper with site-specific logic
def fetch_amazon_price(self, asin: str) -> Optional[float]:
    # Amazon-specific scraping
    pass
```

### Adding New Market Scanners

```python
# Extend TrendHunter
def scan_amazon_bestsellers(self, category_id: str) -> List[dict]:
    # Amazon bestsellers logic
    pass
```

## Troubleshooting

### Website Returns 403/429 (Blocked)
- Increase `MAX_DELAY` in config.py
- Add proxy support in future versions
- Check if site has anti-scraping measures

### Price Not Extracted
- Website structure may have changed
- Add custom CSS selector when adding competitor
- Check logs for debug information

### Database Locked Error
- Ensure only one instance is running
- Delete `sarscope.db` and reinitialize if corrupted

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| requests | 2.31.0 | HTTP client for web requests |
| beautifulsoup4 | 4.12.2 | HTML parsing and scraping |
| fake-useragent | 1.4.0 | Realistic user agent rotation |
| fuzzywuzzy | 0.18.0 | Fuzzy string matching for product matching |
| tabulate | 0.9.0 | ASCII table formatting for reports |
| colorama | 0.4.6 | Colored terminal output |

## Future Enhancements

- [ ] Proxy support for large-scale scraping
- [ ] GraphQL API for external integrations
- [ ] Advanced ML-based demand prediction
- [ ] Multi-currency support
- [ ] Webhook notifications for price changes
- [ ] Email report generation
- [ ] Cloud sync for multi-device support
- [ ] Integration with e-commerce platforms (Shopify, WooCommerce)

## License

Proprietary - SarScope Development Team

## Support

For issues or questions, refer to:
- Check logs in `sarscope.log`
- Review configuration in `config.py`
- Test individual components programmatically

---

**Version**: 1.0.0  
**Last Updated**: January 4, 2026  
**Author**: SarScope Development Team
