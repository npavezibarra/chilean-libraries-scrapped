# ISBN Chile Scraper

Scraper for https://isbnchile.cl/ - the Chilean ISBN registry.

## Overview

This scraper extracts **complete metadata** for all ~167,309 books from the Chilean ISBN database using a two-phase approach:

- **Phase 1**: Collect all book IDs from search results (~47 minutes)
- **Phase 2**: Extract complete metadata including book covers (~4.6 hours)

## Features

- ✅ Async Playwright for high performance
- ✅ Concurrent workers (5 for Phase 1, 10 for Phase 2)
- ✅ Automatic checkpointing and resume capability
- ✅ Retry logic with exponential backoff
- ✅ Progress tracking with ETA
- ✅ Book cover extraction with placeholder detection
- ✅ Complete metadata extraction (20+ fields)

## Setup

```bash
# Install dependencies
cd /Users/nicolasibarra/Desktop/PoliteiaBookCanonicalScraper
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Usage

### Phase 1: Collect Book IDs

Collect all book IDs from search result pages.

```bash
cd isbnchile

# Test mode (first 10 pages, ~60 books)
python phase1_collect_ids.py --test --pages 10

# Full scrape (all 27,885 pages, ~167,309 books)
python phase1_collect_ids.py
```

**Output**: `scraped_data/book_ids.json` (or `book_ids_test.json` in test mode)

**Resume**: If interrupted, simply run the same command again - it will resume from the last checkpoint.

### Phase 2: Extract Complete Metadata

Extract complete metadata for each book including covers.

```bash
cd isbnchile

# Test mode (first 10 books)
python phase2_fetch_details.py --test --limit 10

# Full scrape (all books from Phase 1)
python phase2_fetch_details.py
```

**Output**: `scraped_data/books_complete.json` (or `books_complete_test.json` in test mode)

**Resume**: If interrupted, simply run the same command again - it will resume from the last checkpoint.

### Validate Data

Check data quality and generate reports.

```bash
cd isbnchile

# Validate test data
python validate_data.py books_complete_test.json

# Validate full data
python validate_data.py books_complete.json
```

## Data Schema

Each book record contains 20 fields:

```json
{
  "book_id": "179422",
  "isbn": "978-956-00-2009-3",
  "title": "Book Title",
  "subtitle": "Subtitle if exists",
  "author": "Author Name",
  "publisher": "Publisher Name",
  "subject": "Subject Area",
  "target_audience": "Target Audience",
  "publication_date": "2024-01-01",
  "edition_number": "1",
  "page_count": "250",
  "size": "21x14 cm",
  "price": "15000",
  "binding": "Tapa blanda",
  "format": "Libro",
  "language": "Español",
  "cover_url": "https://isbnchile.cl/files/titulos/179422.jpg",
  "has_real_cover": true,
  "source_url": "https://isbnchile.cl/catalogo.php?mode=detalle&nt=179422",
  "scraped_at": "2026-01-01T10:00:00"
}
```

## Book Covers

- **Real covers**: `https://isbnchile.cl/files/titulos/{book_id}.jpg`
- **Placeholder**: `https://isbnchile.cl/img/libro2.png` (green book icon)
- **Detection**: The `has_real_cover` field indicates whether the book has a real cover image

## Files

- `config.py` - Configuration settings
- `utils.py` - Shared utility functions
- `phase1_collect_ids.py` - Phase 1 scraper (book ID collection)
- `phase2_fetch_details.py` - Phase 2 scraper (metadata extraction)
- `validate_data.py` - Data validation script
- `scraped_data/` - Output directory

## Configuration

Edit `config.py` to adjust:

- `HEADLESS` - Run browser in headless mode (default: True)
- `DELAY_BETWEEN_REQUESTS` - Delay between requests in seconds (default: 0.5)
- `PHASE1_CONCURRENT_WORKERS` - Number of concurrent workers for Phase 1 (default: 5)
- `PHASE2_CONCURRENT_WORKERS` - Number of concurrent workers for Phase 2 (default: 10)
- `PHASE1_CHECKPOINT_INTERVAL` - Save checkpoint every N pages (default: 100)
- `PHASE2_CHECKPOINT_INTERVAL` - Save checkpoint every N books (default: 100)

## Troubleshooting

**Phase 1 fails to start**: Make sure Playwright is installed with `playwright install chromium`

**Phase 2 can't find book IDs**: Run Phase 1 first to collect book IDs

**Scraper stops unexpectedly**: Just run the same command again - it will resume from the last checkpoint

**Too many errors**: Try reducing concurrent workers or increasing delay in `config.py`

## Time Estimates

- **Phase 1 (Test)**: ~30 seconds for 10 pages
- **Phase 1 (Full)**: ~47 minutes for 27,885 pages
- **Phase 2 (Test)**: ~10 seconds for 10 books
- **Phase 2 (Full)**: ~4.6 hours for 167,309 books

**Total time for complete scrape**: ~5-6 hours
