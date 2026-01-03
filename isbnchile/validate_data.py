"""
Data Validation Script
Validates scraped book data and generates quality reports
"""

import argparse
import json
import sys
import config
import utils


def validate_data(filename):
    """Validate scraped book data"""
    print("="*60)
    print("DATA VALIDATION REPORT")
    print("="*60)
    
    # Load data
    data = utils.load_json(filename)
    
    if not data:
        print(f"✗ Could not load data from {filename}")
        return False
    
    books = data.get('books', [])
    
    if not books:
        print("✗ No books found in data file")
        return False
    
    print(f"\n📊 Analyzing {len(books)} books...\n")
    
    # Validation checks
    issues = []
    
    # Check schema compliance
    print("Schema Validation:")
    print("-"*60)
    for i, book in enumerate(books):
        valid, missing = utils.validate_book_record(book)
        if not valid:
            issues.append(f"Book {i} (ID: {book.get('book_id', 'unknown')}) missing fields: {missing}")
            if len(issues) <= 5:  # Only print first 5
                print(f"  ✗ Book {i}: Missing {missing}")
    
    if not issues:
        print("  ✓ All books have complete schema")
    else:
        print(f"  ⚠ {len(issues)} books have missing fields")
    
    # Check required fields
    print("\nRequired Fields Check:")
    print("-"*60)
    required_fields = ['book_id', 'title', 'isbn', 'source_url']
    for field in required_fields:
        count = sum(1 for book in books if book.get(field))
        percentage = (count / len(books)) * 100
        status = "✓" if percentage == 100 else "⚠"
        print(f"  {status} {field:20s}: {count}/{len(books)} ({percentage:.1f}%)")
    
    # Check cover URLs
    print("\nCover URL Validation:")
    print("-"*60)
    real_covers = sum(1 for book in books if book.get('has_real_cover'))
    placeholder_covers = len(books) - real_covers
    print(f"  Real covers:        {real_covers} ({real_covers/len(books)*100:.1f}%)")
    print(f"  Placeholder covers: {placeholder_covers} ({placeholder_covers/len(books)*100:.1f}%)")
    
    # Sample data
    print("\nSample Book Records:")
    print("-"*60)
    for i in range(min(3, len(books))):
        book = books[i]
        print(f"\nBook {i+1}:")
        print(f"  ID:        {book.get('book_id')}")
        print(f"  Title:     {book.get('title', 'N/A')[:50]}")
        print(f"  ISBN:      {book.get('isbn', 'N/A')}")
        print(f"  Author:    {book.get('author', 'N/A')[:40]}")
        print(f"  Publisher: {book.get('publisher', 'N/A')[:40]}")
        print(f"  Cover:     {'Real' if book.get('has_real_cover') else 'Placeholder'}")
        print(f"  URL:       {book.get('source_url', 'N/A')}")
    
    # Print full statistics
    utils.print_statistics(books)
    
    # Summary
    print("\n" + "="*60)
    if len(issues) == 0:
        print("✓ VALIDATION PASSED")
        print("="*60)
        return True
    else:
        print(f"⚠ VALIDATION COMPLETED WITH {len(issues)} ISSUES")
        print("="*60)
        return False


def main():
    parser = argparse.ArgumentParser(description='Validate scraped book data')
    parser.add_argument('filename', nargs='?', default='books_complete_test.json',
                       help='JSON file to validate (default: books_complete_test.json)')
    
    args = parser.parse_args()
    
    success = validate_data(args.filename)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
