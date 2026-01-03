"""
Configuration for lightweight HTTP-based scraper
Optimized for fragile servers with aggressive rate limiting
"""

# Base URL
BASE_URL = "https://isbnchile.cl/"

# Output settings
OUTPUT_DIR = "scraped_data"
OUTPUT_FORMAT = "json"

# HTTP Scraping settings (optimized for stable detail pages)
REQUEST_TIMEOUT = 180  # Seconds to wait for response
DELAY_BETWEEN_REQUESTS = 0  # No delay - maximum speed!
DELAY_RANDOMIZATION = 0.5  # Small random delay to appear more human
MAX_RETRIES = 5  # Maximum retry attempts per request
RETRY_BACKOFF_BASE = 30  # Base seconds for exponential backoff (30, 60, 120, 240, 480)

# Server error handling (for 500/503 errors)
SERVER_ERROR_WAIT_TIME = 300  # Wait 5 minutes when server returns 500/503
SERVER_ERROR_MAX_RETRIES = 10  # Try up to 10 times for server errors (50 minutes total)

# Circuit breaker settings
CIRCUIT_BREAKER_THRESHOLD = 10  # Consecutive failures before circuit breaks
CIRCUIT_BREAKER_COOLDOWN = 300  # Seconds to wait when circuit breaks (5 minutes)

# Phase 1 settings - Book ID Collection
PHASE1_TOTAL_PAGES = 27885
PHASE1_CHECKPOINT_INTERVAL = 50  # Save every 50 pages (more frequent for reliability)
PHASE1_OUTPUT_FILE = "book_ids.json"
PHASE1_CHECKPOINT_FILE = "phase1_checkpoint.json"

# Phase 2 settings - Complete Metadata Extraction
PHASE2_CHECKPOINT_INTERVAL = 50  # Save every 50 books
PHASE2_OUTPUT_FILE = "books_complete.json"
PHASE2_CHECKPOINT_FILE = "phase2_checkpoint.json"

# URL templates
SEARCH_RESULTS_URL = "https://isbnchile.cl/catalogo.php?mode=resultados_avanzada&pagina={page}"
BOOK_DETAIL_URL = "https://isbnchile.cl/catalogo.php?mode=detalle&nt={book_id}"
BOOK_COVER_URL = "https://isbnchile.cl/files/titulos/{book_id}.jpg"
PLACEHOLDER_COVER_URL = "https://isbnchile.cl/img/libro2.png"

# HTTP Headers
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-CL,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

# Complete book record schema
BOOK_SCHEMA_FIELDS = [
    "book_id",           # NT parameter
    "isbn",              # ISBN-13 or ISBN-10
    "title",             # Main title
    "subtitle",          # Subtitle (if exists)
    "author",            # Author name(s)
    "publisher",         # Editorial/Publisher
    "subject",           # Materia/Subject
    "target_audience",   # Público objetivo
    "publication_date",  # Fecha de publicación
    "edition_number",    # Número de edición
    "page_count",        # Número de páginas
    "size",              # Tamaño (dimensions)
    "price",             # Precio
    "binding",           # Encuadernación
    "format",            # Soporte (book, ebook, etc)
    "language",          # Idioma
    "cover_url",         # Book cover image URL
    "has_real_cover",    # True if not placeholder
    "source_url",        # Detail page URL
    "scraped_at"         # ISO timestamp
]
