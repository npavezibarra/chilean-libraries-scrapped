"""
Phase 2 HTTP: Complete Metadata Extraction (Lightweight)
Uses requests + BeautifulSoup for fragile servers
"""

import requests
from bs4 import BeautifulSoup
import argparse
import time
import random
from datetime import datetime
import config_http as config
import utils


class Phase2HTTPScraper:
    def __init__(self, test_mode=False, test_limit=10):
        self.test_mode = test_mode
        self.test_limit = test_limit
        self.books = []
        self.book_ids = []
        self.start_index = 0
        self.start_time = None
        self.failed_ids = []
        self.consecutive_failures = 0
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        
    def load_book_ids(self):
        """Load book IDs from Phase 1 output"""
        input_file = "book_ids_test.json" if self.test_mode else config.PHASE1_OUTPUT_FILE
        data = utils.load_json(input_file)
        
        if not data:
            print(f"✗ Could not load book IDs from {input_file}")
            print("  Please run Phase 1 first!")
            return False
        
        all_ids = data.get('book_ids', [])
        
        if self.test_mode:
            self.book_ids = all_ids[:self.test_limit]
            print(f"🧪 TEST MODE: Processing first {len(self.book_ids)} books")
        else:
            self.book_ids = all_ids
            print(f"📚 Processing {len(self.book_ids)} books")
        
        return True
    
    def load_checkpoint(self):
        """Load checkpoint if exists"""
        checkpoint = utils.load_checkpoint(config.PHASE2_CHECKPOINT_FILE)
        if checkpoint:
            self.books = checkpoint.get('books', [])
            self.start_index = checkpoint.get('last_index', -1) + 1
            self.failed_ids = checkpoint.get('failed_ids', [])
            print(f"✓ Resuming from index {self.start_index} with {len(self.books)} books already scraped")
        else:
            print("✓ Starting fresh scrape")
    
    def save_checkpoint(self, current_index):
        """Save checkpoint"""
        checkpoint_data = {
            'books': self.books,
            'last_index': current_index,
            'total_scraped': len(self.books),
            'failed_ids': self.failed_ids,
            'timestamp': utils.get_timestamp()
        }
        utils.save_checkpoint(checkpoint_data, config.PHASE2_CHECKPOINT_FILE)
    
    def wait_with_backoff(self, attempt=0):
        """Wait with exponential backoff"""
        if attempt == 0:
            delay = config.DELAY_BETWEEN_REQUESTS
            delay += random.uniform(0, config.DELAY_RANDOMIZATION)
        else:
            delay = config.RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
        
        time.sleep(delay)
    
    def circuit_breaker_check(self):
        """Check if circuit breaker should activate"""
        if self.consecutive_failures >= config.CIRCUIT_BREAKER_THRESHOLD:
            print(f"\n⚠️  CIRCUIT BREAKER ACTIVATED")
            print(f"   {self.consecutive_failures} consecutive failures detected")
            print(f"   Cooling down for {config.CIRCUIT_BREAKER_COOLDOWN}s ({config.CIRCUIT_BREAKER_COOLDOWN//60} minutes)...")
            time.sleep(config.CIRCUIT_BREAKER_COOLDOWN)
            self.consecutive_failures = 0
            print(f"✓ Circuit breaker reset, resuming scraping")
    
    def extract_field_value(self, soup, label_text):
        """Extract field value by finding the label span and getting the next element's text"""
        try:
            # Find all spans with class 'labels'
            labels = soup.find_all('span', class_='labels')
            for label in labels:
                if label_text in label.get_text():
                    # First, try to find a direct <a> sibling (for author field)
                    next_link = label.find_next_sibling('a')
                    if next_link and next_link.get('class') and 'texto' in next_link.get('class'):
                        return next_link.get_text(strip=True)
                    
                    # Otherwise, get the next sibling span (for other fields)
                    next_span = label.find_next_sibling('span')
                    if next_span:
                        # Get text from the span, or from link inside it
                        link = next_span.find('a')
                        if link:
                            return link.get_text(strip=True)
                        return next_span.get_text(strip=True)
            return None
        except:
            return None
    
    def extract_book_metadata(self, book_id):
        """Extract complete metadata from a book detail page"""
        url = config.BOOK_DETAIL_URL.format(book_id=book_id)
        
        for attempt in range(config.MAX_RETRIES):
            try:
                # Make HTTP request
                response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
                
                # Check for server errors
                if response.status_code == 504:
                    raise Exception("504 Gateway Time-out")
                elif response.status_code == 503:
                    raise Exception("503 Service Unavailable")
                elif response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}")
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Create book record
                book = utils.create_empty_book_record()
                book['book_id'] = book_id
                book['source_url'] = url
                book['scraped_at'] = utils.get_timestamp()
                
                # Extract cover URL
                cover_img = soup.select_one('.lista_libros img')
                if cover_img and cover_img.get('src'):
                    cover_url = cover_img['src']
                    # Convert relative URL to absolute
                    if cover_url.startswith('./'):
                        cover_url = cover_url.replace('./', 'https://isbnchile.cl/')
                    elif not cover_url.startswith('http'):
                        cover_url = 'https://isbnchile.cl/' + cover_url
                    
                    book['cover_url'] = cover_url
                    book['has_real_cover'] = not utils.is_placeholder_cover(cover_url)
                else:
                    book['cover_url'] = config.PLACEHOLDER_COVER_URL
                    book['has_real_cover'] = False
                
                # Extract title from TituloNolink span
                title_span = soup.find('span', class_='TituloNolink')
                if title_span:
                    # Get all text, removing the subtitle (in <i> tag)
                    title_text = title_span.get_text(separator=' ', strip=True)
                    # Check for subtitle in <i> tag
                    subtitle_tag = title_span.find('i')
                    if subtitle_tag:
                        subtitle_text = subtitle_tag.get_text(strip=True)
                        book['subtitle'] = subtitle_text
                        # Remove subtitle from title
                        title_text = title_text.replace(subtitle_text, '').strip()
                    book['title'] = title_text
                
                # Extract ISBN from span with class 'isbn'
                isbn_span = soup.find('span', class_='isbn')
                if isbn_span:
                    isbn_text = isbn_span.get_text(strip=True)
                    # Remove "ISBN" label
                    book['isbn'] = isbn_text.replace('ISBN', '').strip()
                
                # Extract other metadata fields using the new method
                book['author'] = self.extract_field_value(soup, 'Autor:')
                book['publisher'] = self.extract_field_value(soup, 'Editorial:')
                book['subject'] = self.extract_field_value(soup, 'Materia:')
                book['target_audience'] = self.extract_field_value(soup, 'Público objetivo:')
                book['publication_date'] = self.extract_field_value(soup, 'Publicado:')
                book['edition_number'] = self.extract_field_value(soup, 'Número de edición:')
                book['page_count'] = self.extract_field_value(soup, 'Número de páginas:')
                book['size'] = self.extract_field_value(soup, 'Tamaño:')
                book['price'] = self.extract_field_value(soup, 'Precio:')
                book['binding'] = self.extract_field_value(soup, 'Encuadernación:')
                book['format'] = self.extract_field_value(soup, 'Soporte:')
                book['language'] = self.extract_field_value(soup, 'Idioma:')
                
                # Success - reset failure counter
                self.consecutive_failures = 0
                return book
                
            except Exception as e:
                self.consecutive_failures += 1
                
                if attempt < config.MAX_RETRIES - 1:
                    wait_time = config.RETRY_BACKOFF_BASE * (2 ** attempt)
                    print(f"\n⚠️  Error on book {book_id} (attempt {attempt + 1}/{config.MAX_RETRIES}): {e}")
                    print(f"   Retrying in {wait_time}s...")
                    self.wait_with_backoff(attempt + 1)
                else:
                    print(f"\n✗ Failed book {book_id} after {config.MAX_RETRIES} attempts: {e}")
                    return None
        
        return None
    
    def run(self):
        """Main scraping logic"""
        print("="*60)
        print("PHASE 2 HTTP: COMPLETE METADATA EXTRACTION (LIGHTWEIGHT)")
        print("="*60)
        
        # Load book IDs
        if not self.load_book_ids():
            return
        
        print(f"⚙️  Settings:")
        print(f"   - Delay: {config.DELAY_BETWEEN_REQUESTS}s + random 0-{config.DELAY_RANDOMIZATION}s")
        print(f"   - Max retries: {config.MAX_RETRIES}")
        print(f"   - Backoff: {config.RETRY_BACKOFF_BASE}s base (exponential)")
        print(f"   - Circuit breaker: {config.CIRCUIT_BREAKER_THRESHOLD} failures = {config.CIRCUIT_BREAKER_COOLDOWN}s cooldown")
        print(f"   - Checkpoint: every {config.PHASE2_CHECKPOINT_INTERVAL} books")
        print()
        
        # Load checkpoint
        self.load_checkpoint()
        
        if self.start_index >= len(self.book_ids):
            print("✓ All books already scraped!")
            return
        
        self.start_time = time.time()
        
        # Scrape books sequentially (no concurrency for fragile server)
        for index in range(self.start_index, len(self.book_ids)):
            book_id = self.book_ids[index]
            
            # Check circuit breaker
            self.circuit_breaker_check()
            
            # Extract book metadata
            book = self.extract_book_metadata(book_id)
            
            if book:
                self.books.append(book)
            else:
                self.failed_ids.append(book_id)
            
            # Progress tracking
            completed = index - self.start_index + 1
            total = len(self.book_ids) - self.start_index
            utils.print_progress(completed, total, self.start_time, prefix="Progress")
            
            # Checkpoint periodically
            if (index + 1) % config.PHASE2_CHECKPOINT_INTERVAL == 0:
                self.save_checkpoint(index)
            
            # Rate limiting (except on last book)
            if index < len(self.book_ids) - 1:
                self.wait_with_backoff()
        
        # Save final results
        output_file = "books_complete_test.json" if self.test_mode else config.PHASE2_OUTPUT_FILE
        
        result_data = {
            'total_books': len(self.books),
            'failed_books': len(self.failed_ids),
            'books': self.books,
            'failed_ids': self.failed_ids,
            'scraped_at': utils.get_timestamp()
        }
        
        utils.save_json(result_data, output_file)
        
        # Print summary
        elapsed = time.time() - self.start_time
        total_attempted = len(self.books) + len(self.failed_ids)
        success_rate = (len(self.books) / total_attempted * 100) if total_attempted > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"✓ Phase 2 HTTP Complete!")
        print(f"  Total books scraped: {len(self.books)}")
        print(f"  Failed books: {len(self.failed_ids)}")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Time elapsed: {utils.format_duration(elapsed)}")
        print(f"  Average: {elapsed/total_attempted:.1f}s per book")
        print(f"  Output saved to: {output_file}")
        print(f"{'='*60}")
        
        # Print statistics
        if len(self.books) > 0:
            utils.print_statistics(self.books)


def main():
    parser = argparse.ArgumentParser(description='Phase 2 HTTP: Extract complete metadata from ISBN Chile (Lightweight)')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--limit', type=int, default=10, help='Number of books for test mode')
    
    args = parser.parse_args()
    
    scraper = Phase2HTTPScraper(test_mode=args.test, test_limit=args.limit)
    scraper.run()


if __name__ == "__main__":
    main()
