"""
Utility functions for ISBN Chile scraper
"""

import json
import os
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import config


def save_checkpoint(data, filename):
    """Save checkpoint data to JSON file"""
    filepath = os.path.join(config.OUTPUT_DIR, filename)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Checkpoint saved: {filename}")


def load_checkpoint(filename):
    """Load checkpoint data from JSON file"""
    filepath = os.path.join(config.OUTPUT_DIR, filename)
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✓ Checkpoint loaded: {filename}")
    return data


def save_json(data, filename):
    """Save data to JSON file"""
    filepath = os.path.join(config.OUTPUT_DIR, filename)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Data saved: {filename}")


def load_json(filename):
    """Load data from JSON file"""
    filepath = os.path.join(config.OUTPUT_DIR, filename)
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def extract_book_id_from_url(url):
    """Extract book ID (nt parameter) from URL"""
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        return params.get('nt', [None])[0]
    except Exception:
        return None


def is_placeholder_cover(url):
    """Check if cover URL is a placeholder"""
    return 'libro2.png' in url if url else True


def get_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def format_duration(seconds):
    """Format seconds into human-readable duration"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def print_progress(current, total, start_time=None, prefix="Progress"):
    """Print progress bar to console"""
    percentage = (current / total) * 100
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    
    progress_str = f"\r{prefix}: [{bar}] {current}/{total} ({percentage:.1f}%)"
    
    if start_time:
        elapsed = time.time() - start_time
        if current > 0:
            rate = current / elapsed
            remaining = (total - current) / rate if rate > 0 else 0
            progress_str += f" | Elapsed: {format_duration(elapsed)} | ETA: {format_duration(remaining)}"
    
    print(progress_str, end='', flush=True)
    
    if current == total:
        print()  # New line when complete


async def retry_with_backoff(func, max_retries=3, initial_delay=1):
    """
    Retry a function with exponential backoff
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
    
    Returns:
        Result of the function or None if all retries failed
    """
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"\n✗ Failed after {max_retries} attempts: {e}")
                return None
            
            print(f"\n⚠ Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
            await asyncio_sleep(delay)
            delay *= 2  # Exponential backoff
    
    return None


async def asyncio_sleep(seconds):
    """Async sleep wrapper"""
    import asyncio
    await asyncio.sleep(seconds)


def create_empty_book_record():
    """Create an empty book record with all schema fields"""
    return {field: None for field in config.BOOK_SCHEMA_FIELDS}


def validate_book_record(book):
    """Validate that a book record has all required fields"""
    missing_fields = [field for field in config.BOOK_SCHEMA_FIELDS if field not in book]
    return len(missing_fields) == 0, missing_fields


def print_statistics(books):
    """Print statistics about scraped books"""
    total = len(books)
    
    if total == 0:
        print("No books to analyze")
        return
    
    # Count fields with data
    field_counts = {field: 0 for field in config.BOOK_SCHEMA_FIELDS}
    real_covers = 0
    
    for book in books:
        for field in config.BOOK_SCHEMA_FIELDS:
            if book.get(field):
                field_counts[field] += 1
        
        if book.get('has_real_cover'):
            real_covers += 1
    
    print("\n" + "="*60)
    print("SCRAPING STATISTICS")
    print("="*60)
    print(f"Total books: {total}")
    print(f"Books with real covers: {real_covers} ({real_covers/total*100:.1f}%)")
    print(f"Books with placeholder covers: {total - real_covers} ({(total-real_covers)/total*100:.1f}%)")
    print("\nField Completion Rates:")
    print("-"*60)
    
    for field in config.BOOK_SCHEMA_FIELDS:
        count = field_counts[field]
        percentage = (count / total) * 100
        bar_length = 30
        filled = int(bar_length * count / total)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"{field:20s} [{bar}] {percentage:5.1f}% ({count}/{total})")
    
    print("="*60)
