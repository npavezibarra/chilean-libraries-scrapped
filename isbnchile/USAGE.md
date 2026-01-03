# ISBN Chile Scraper - Usage Guide

## Overview

This scraper extracts complete book metadata from the ISBN Chile catalog (https://isbnchile.cl). It uses a lightweight HTTP-based approach with `requests` and `BeautifulSoup`.

## Quick Start

### 1. Install Dependencies

```bash
pip install requests beautifulsoup4
```

### 2. Generate Book IDs

Instead of scraping search pages, generate all possible book IDs:

```python
# Create book_ids.json with IDs 1-180000
book_ids = [str(i) for i in range(1, 180001)]
import json
with open('scraped_data/book_ids.json', 'w') as f:
    json.dump({'book_ids': book_ids}, f)
```

Or use the existing `scraped_data/book_ids.json` file.

### 3. Run the Scraper

```bash
# Run in background
nohup python3 phase2_http.py > phase2.log 2>&1 &

# Monitor progress
tail -f phase2.log
```

## Configuration

Edit `config_http.py` to adjust settings:

```python
# Speed settings
DELAY_BETWEEN_REQUESTS = 0      # 0 = maximum speed
DELAY_RANDOMIZATION = 0.5       # Random 0-0.5s delay

# Reliability settings
REQUEST_TIMEOUT = 180           # 3 minutes per request
MAX_RETRIES = 5                 # Retry failed requests
CHECKPOINT_INTERVAL = 50        # Save every 50 books
```

## Files

| File | Purpose |
|------|---------|
| `phase2_http.py` | Main scraper script |
| `config_http.py` | Configuration settings |
| `utils.py` | Helper functions |
| `validate_data.py` | Data validation |
| `merge_files.py` | Merge partial files |

## Output

**Final Database**: `scraped_data/isbn_chile_complete.json`

**Structure**:
```json
{
  "total_books": 180000,
  "books": [
    {
      "book_id": "1",
      "isbn": "978-956-...",
      "title": "Book Title",
      "author": "Author Name",
      "publisher": "Publisher",
      "publication_date": "2020-01-01",
      ...
    }
  ]
}
```

## Data Fields (20 total)

- `book_id` - Unique ID
- `isbn` - ISBN-13 or ISBN-10
- `title` - Book title
- `subtitle` - Subtitle (if exists)
- `author` - Author name(s)
- `publisher` - Publisher/Editorial
- `subject` - Subject/Category
- `target_audience` - Target audience
- `publication_date` - Publication date
- `edition_number` - Edition number
- `page_count` - Number of pages
- `size` - Physical dimensions
- `price` - Price (if available)
- `binding` - Binding type
- `format` - Format (print/digital)
- `language` - Language
- `cover_url` - Cover image URL
- `has_real_cover` - True if real cover exists
- `source_url` - Detail page URL
- `scraped_at` - Timestamp

## Resuming After Crash

The scraper automatically resumes from the last checkpoint:

```bash
# Just restart - it will continue from where it stopped
nohup python3 phase2_http.py > phase2.log 2>&1 &
```

## Validation

Validate the scraped data:

```bash
python3 validate_data.py scraped_data/isbn_chile_complete.json
```

## Performance

- **Speed**: ~0.6 seconds per book (with 0 delay)
- **Time**: ~31 hours for 180,000 books
- **Success Rate**: 100%
- **Data Completeness**: 95.7%

## Troubleshooting

### Server Errors (500/503)

The scraper automatically waits 5 minutes and retries up to 10 times.

### Timeouts

Increase `REQUEST_TIMEOUT` in `config_http.py`:

```python
REQUEST_TIMEOUT = 300  # 5 minutes
```

### Memory Issues

The scraper saves checkpoints every 50 books to prevent memory issues. If it crashes, split the checkpoint:

```bash
python3 split_checkpoint.py
```

### Slow Progress

Reduce delay in `config_http.py`:

```python
DELAY_BETWEEN_REQUESTS = 0  # Maximum speed
```

## Advanced Usage

### Scrape Specific Range

Edit `phase2_http.py` to set start/end indices:

```python
# In the run() method
for i in range(50000, 100000):  # Books 50k-100k only
    ...
```

### Export to CSV

```python
import json
import csv

with open('scraped_data/isbn_chile_complete.json', 'r') as f:
    data = json.load(f)

with open('books.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=data['books'][0].keys())
    writer.writeheader()
    writer.writerows(data['books'])
```

## Notes

- The scraper is designed for the ISBN Chile website structure as of January 2026
- If the website structure changes, update the selectors in `phase2_http.py`
- Always respect the website's terms of service
- Use conservative delays to avoid overloading the server

## Support

For issues or questions, check:
- `phase2.log` for error messages
- `scraped_data/phase2_checkpoint.json` for current progress
- `README_HTTP.md` for detailed documentation
