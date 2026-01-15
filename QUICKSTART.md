# SarScope Quick Start Guide

## Installation (macOS/Linux)

### 1. Navigate to project directory
```bash
cd /Users/alifurkansagir/Desktop/sartech/sarscope
```

### 2. Run installation script
```bash
chmod +x install.sh
./install.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running SarScope

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the application
python sarscope/main.py
```

## First Steps

### Add a Product
1. Select option **3** from the menu
2. Fill in product details:
   - Name: e.g., "Wireless Headphones"
   - SKU: e.g., "WH-001"
   - Your Price: e.g., 79.99
   - Minimum Price: e.g., 50.00
   - Cost: e.g., 30.00
   - Target Margin: e.g., 50

3. Add competitor URLs:
   - Provide URLs where competitors sell similar products
   - Example: "https://amazon.com/dp/B0XXXXXX"

### Monitor Prices
1. Select option **1** from the menu (Price Patrol)
2. The system will:
   - Fetch competitor prices
   - Compare against your price
   - Suggest optimized pricing
   - Show opportunities

### Discover Trends
1. Select option **2** from the menu (Trend Hunter)
2. Enter a category URL to scan
3. View new opportunities:
   - Products not in your inventory
   - Sales velocity estimation
   - Fuzzy match scores

### View Report
1. Select option **4** from the menu
2. See:
   - Dashboard statistics
   - Product watchlist
   - Pricing recommendations

## Common Tasks

### Check Competitor Prices
```
Menu → Option 1 → Price Patrol
```

### Find Market Opportunities
```
Menu → Option 2 → Trend Hunter
```

### Add New Product to Monitor
```
Menu → Option 3 → Add Product
```

### Export Data

Products are stored in SQLite database: `sarscope.db`

To backup:
```bash
cp sarscope/sarscope.db sarscope/sarscope_backup_$(date +%Y%m%d).db
```

## Programmatic Usage

```python
from sarscope.database import DatabaseManager
from sarscope.core.scraper import SarScopeScraper

# Initialize
db = DatabaseManager()
scraper = SarScopeScraper()

# Get all products
products = db.get_all_products()
for product in products:
    print(f"{product.name}: ${product.my_price:.2f}")

# Fetch price
price = scraper.fetch_price("https://competitor.com/product")
print(f"Competitor price: ${price:.2f}")

# Get statistics
stats = db.get_dashboard_stats()
print(f"Total products: {stats['total_products']}")
```

## Customization

### Change Pricing Strategy
Edit `sarscope/config.py`:
```python
UNDERCUTTING_MARGIN = 2.0  # $2 below competitor instead of $1
```

### Adjust Anti-Detection
```python
MIN_DELAY = 5  # Longer delays
MAX_DELAY = 10
```

### Change Fuzzy Match Sensitivity
```python
FUZZY_MATCH_THRESHOLD = 75  # Lower = more lenient matching
```

## Logging

Check logs in: `sarscope/sarscope.log`

View live logs:
```bash
tail -f sarscope/sarscope.log
```

## Troubleshooting

### Import Error
```
ModuleNotFoundError: No module named 'requests'
```
Solution:
```bash
pip install -r requirements.txt
```

### Database Error
```
sqlite3.OperationalError: database is locked
```
Solution:
```bash
rm sarscope/sarscope.db  # Reset database
python sarscope/main.py  # Reinitialize
```

### Website Blocking
- Increase delays in `config.py`
- Try adding different user agent
- Check if site allows scraping in `robots.txt`

## Tips & Best Practices

✓ **Do's**
- Add multiple competitor URLs per product
- Run Price Patrol regularly (daily recommended)
- Monitor margins closely
- Review trends weekly

✗ **Don'ts**
- Don't set minimum price below cost
- Don't scrape sites that block scraping
- Don't run multiple instances simultaneously
- Don't use delays less than 3 seconds

## Performance

- **Typical Price Check**: 2-5 seconds per competitor
- **Trend Scan**: 10-30 seconds per category
- **Fuzzy Matching**: <1 second for hundreds of products

## Next Steps

1. Add your product inventory
2. Add competitor URLs
3. Run Price Patrol to establish baseline
4. Scan markets for trends
5. Review opportunities report
6. Adjust pricing automatically

---

For detailed documentation, see [README.md](README.md)
