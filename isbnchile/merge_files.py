#!/usr/bin/env python3
"""
Merge books_partial_0.json and books_complete.json into final database
"""

import json
from datetime import datetime

print("=" * 60)
print("MERGING SCRAPED DATA FILES")
print("=" * 60)

# Load partial file (books 1-81,600)
print("\n📖 Loading books_partial_0.json...")
with open('scraped_data/books_partial_0.json', 'r') as f:
    partial_data = json.load(f)

partial_books = partial_data.get('books', [])
print(f"   ✓ Loaded {len(partial_books)} books (IDs 1-81,600)")

# Load complete file (books 81,601-180,000)
print("\n📖 Loading books_complete.json...")
with open('scraped_data/books_complete.json', 'r') as f:
    complete_data = json.load(f)

complete_books = complete_data.get('books', [])
print(f"   ✓ Loaded {len(complete_books)} books (IDs 81,601-180,000)")

# Merge books
print("\n🔗 Merging books...")
all_books = partial_books + complete_books
print(f"   ✓ Total books: {len(all_books)}")

# Calculate statistics
books_with_data = [b for b in all_books if b.get('isbn') or b.get('title')]
books_with_real_covers = [b for b in all_books if b.get('has_real_cover')]

# Create final merged file
final_data = {
    'total_books': len(all_books),
    'books_with_data': len(books_with_data),
    'books_with_real_covers': len(books_with_real_covers),
    'books': all_books,
    'merged_at': datetime.now().isoformat(),
    'source_files': ['books_partial_0.json', 'books_complete.json']
}

# Save merged file
output_file = 'scraped_data/isbn_chile_complete.json'
print(f"\n💾 Saving to {output_file}...")
with open(output_file, 'w') as f:
    json.dump(final_data, f, indent=2)

print(f"   ✓ Saved!")

# Print summary
print("\n" + "=" * 60)
print("✓ MERGE COMPLETE!")
print("=" * 60)
print(f"Total books: {len(all_books):,}")
print(f"Books with data: {len(books_with_data):,} ({len(books_with_data)/len(all_books)*100:.1f}%)")
print(f"Books with real covers: {len(books_with_real_covers):,} ({len(books_with_real_covers)/len(all_books)*100:.1f}%)")
print(f"\nOutput file: {output_file}")
print("=" * 60)
