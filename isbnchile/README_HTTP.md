# ISBN Chile Scraper - Lightweight HTTP Version

**Optimized for fragile servers with aggressive rate limiting**

## Overview

This is a lightweight HTTP-based scraper designed specifically for the fragile ISBN Chile server that experiences frequent timeouts and 504 Gateway errors.

### Key Features

- ✅ **Lightweight**: Uses `requests` + `BeautifulSoup` instead of Playwright
- ✅ **Conservative**: 3-second delays between requests (vs 0.5s)
- ✅ **Single worker**: No concurrent requests to avoid overloading server
- ✅ **Exponential backoff**: 30s, 60s, 120s, 240s, 480s retry delays
- ✅ **Circuit breaker**: Pauses for 5 minutes after 10 consecutive failures
- ✅ **Frequent checkpointing**: Every 50 pages/books for reliability
- ✅ **Resume capability**: Automatically resumes from last checkpoint

### Time Estimates

- **Phase 1**: ~23 hours (27,885 pages × 3 seconds)
- **Phase 2**: ~139 hours / ~5.8 days (167,309 books × 3 seconds)
- **Total**: ~7 days of continuous running

## Setup

```bash
# Install dependencies
cd /Users/nicolasibarra/Desktop/PoliteiaBookCanonicalScraper
pip3 install beautifulsoup4 requests --user

# Navigate to scraper directory
cd isbnchile
```

## Usage

### Phase 1: Collect Book IDs

```bash
# Test mode (first 3 pages)
python3 phase1_http.py --test --pages 3

# Full scrape (all 27,885 pages)
python3 phase1_http.py
```

**Output**: `scraped_data/book_ids.json`

### Phase 2: Extract Complete Metadata

```bash
# Test mode (first 10 books)
python3 phase2_http.py --test --limit 10

# Full scrape (all books from Phase 1)
python3 phase2_http.py
```

**Output**: `scraped_data/books_complete.json`

### Validate Data

```bash
python3 validate_data.py books_complete_test.json
```

## Configuration

Edit `config_http.py` to adjust settings:

```python
# Rate limiting
DELAY_BETWEEN_REQUESTS = 3  # Seconds between requests
DELAY_RANDOMIZATION = 1     # Add random 0-1 seconds

# Retry settings
MAX_RETRIES = 5                 # Max attempts per request
RETRY_BACKOFF_BASE = 30         # Base seconds for exponential backoff

# Circuit breaker
CIRCUIT_BREAKER_THRESHOLD = 10  # Consecutive failures before break
CIRCUIT_BREAKER_COOLDOWN = 300  # Seconds to wait (5 minutes)

# Checkpointing
PHASE1_CHECKPOINT_INTERVAL = 50  # Save every 50 pages
PHASE2_CHECKPOINT_INTERVAL = 50  # Save every 50 books
```

## How It Works

### Exponential Backoff

When a request fails, the scraper waits progressively longer before retrying:

1. **Attempt 1 fails**: Wait 30 seconds
2. **Attempt 2 fails**: Wait 60 seconds
3. **Attempt 3 fails**: Wait 120 seconds
4. **Attempt 4 fails**: Wait 240 seconds
5. **Attempt 5 fails**: Skip and continue

### Circuit Breaker

If 10 consecutive requests fail:
1. Scraper pauses for 5 minutes
2. Resets failure counter
3. Resumes scraping

This prevents hammering a down server and gives it time to recover.

### Checkpointing

Progress is saved every 50 pages/books to:
- `scraped_data/phase1_checkpoint.json`
- `scraped_data/phase2_checkpoint.json`

If interrupted, simply run the same command again to resume.

## Monitoring Progress

The scraper displays real-time progress:

```
Progress: [████████████░░░░░░░░░░░░░░░░] 150/500 (30.0%) | Elapsed: 12m 30s | ETA: 29m 10s
```

## Troubleshooting

### Server Still Timing Out

If you see repeated timeout errors:

```
⚠️  Error on page 1 (attempt 3/5): Read timed out
   Retrying in 120s...
```

**Solutions**:
1. **Increase delays**: Edit `config_http.py` and set `DELAY_BETWEEN_REQUESTS = 5`
2. **Increase timeout**: Set `REQUEST_TIMEOUT = 60`
3. **Wait for off-peak hours**: Try scraping at 2-6 AM Chilean time
4. **Check server status**: Visit https://isbnchile.cl in browser

### Circuit Breaker Activating Frequently

If you see:

```
⚠️  CIRCUIT BREAKER ACTIVATED
   10 consecutive failures detected
   Cooling down for 300s (5 minutes)...
```

**Solutions**:
1. **Increase cooldown**: Set `CIRCUIT_BREAKER_COOLDOWN = 600` (10 minutes)
2. **Reduce threshold**: Set `CIRCUIT_BREAKER_THRESHOLD = 5`
3. **Check if server is down**: The server may be experiencing extended outage

### Resume After Interruption

If scraping is interrupted (Ctrl+C, computer sleep, etc.):

```bash
# Just run the same command again
python3 phase1_http.py  # Automatically resumes from checkpoint
```

### Check Checkpoint Status

```bash
# View Phase 1 checkpoint
cat scraped_data/phase1_checkpoint.json

# View Phase 2 checkpoint
cat scraped_data/phase2_checkpoint.json
```

## Running in Background

For long-running scrapes, use `nohup` to run in background:

```bash
# Phase 1 in background
nohup python3 phase1_http.py > phase1.log 2>&1 &

# Check progress
tail -f phase1.log

# Find process ID
ps aux | grep phase1_http

# Stop if needed
kill <process_id>
```

## Data Schema

Same as the Playwright version - extracts 20 fields per book:

- book_id, isbn, title, subtitle
- author, publisher, subject, target_audience
- publication_date, edition_number, page_count, size
- price, binding, format, language
- cover_url, has_real_cover, source_url, scraped_at

## Comparison: HTTP vs Playwright

| Feature | HTTP (Lightweight) | Playwright (Original) |
|---------|-------------------|----------------------|
| **Speed** | ~7 days | ~5-6 hours |
| **Reliability** | High (handles fragile servers) | Low (times out) |
| **Server Load** | Very low | High |
| **Concurrency** | 1 worker | 5-10 workers |
| **Delays** | 3s + random | 0.5s |
| **Retries** | 5 attempts, exponential backoff | 3 attempts |
| **Circuit Breaker** | Yes (5min cooldown) | No |
| **Best For** | Fragile/overloaded servers | Fast, stable servers |

## Recommended Workflow

1. **Test first**: Run Phase 1 test with 3 pages
2. **Verify data**: Check that book IDs are extracted correctly
3. **Run Phase 1 full**: Let it run for ~23 hours (can run overnight)
4. **Test Phase 2**: Run Phase 2 test with 10 books
5. **Verify metadata**: Check that all fields are extracted
6. **Run Phase 2 full**: Let it run for ~6 days (can run in background)
7. **Validate**: Run validation script on final data

## Tips for Success

1. **Run during off-peak hours**: 2-6 AM Chilean time (UTC-3)
2. **Use background mode**: Use `nohup` for long runs
3. **Monitor logs**: Check for repeated failures
4. **Be patient**: 7 days is slow but reliable for fragile servers
5. **Don't interrupt**: Let checkpoints save automatically

## Files

- `config_http.py` - Configuration for HTTP scraper
- `phase1_http.py` - Phase 1 HTTP scraper (book IDs)
- `phase2_http.py` - Phase 2 HTTP scraper (metadata)
- `utils.py` - Shared utilities
- `validate_data.py` - Data validation
- `scraped_data/` - Output directory

## Support

If you encounter issues:

1. Check server status: `curl -I https://isbnchile.cl`
2. Review logs for error patterns
3. Adjust configuration in `config_http.py`
4. Try increasing delays and timeouts
