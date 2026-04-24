#!/usr/bin/env python
"""
Script to set default categories for existing products based on their names.
Run this script to categorize existing products.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from members.models import Product

def categorize_products():
    """Set categories for existing products based on their names"""
    
    # Category keywords mapping
    category_keywords = {
        'dairy': ['milk', 'dairy', 'cheese', 'butter', 'yogurt', 'curd', 'ghee', 'cream', 'paneer'],
        'vegetables': ['vegetable', 'onion', 'tomato', 'potato', 'carrot', 'cabbage', 'spinach', 'cucumber', 'brinjal', 'lady finger', 'okra'],
        'fruits': ['fruit', 'apple', 'banana', 'orange', 'mango', 'grapes', 'papaya', 'guava', 'pomegranate'],
        'grains': ['rice', 'wheat', 'flour', 'dal', 'lentil', 'chana', 'moong', 'masoor', 'toor', 'gram'],
        'spices': ['spice', 'salt', 'pepper', 'turmeric', 'cumin', 'coriander', 'chili', 'garam masala', 'cardamom', 'cinnamon'],
        'beverages': ['tea', 'coffee', 'juice', 'water', 'soft drink', 'energy drink', 'soda'],
        'snacks': ['snack', 'biscuit', 'cookie', 'chips', 'namkeen', 'sweets', 'chocolate', 'cake'],
        'household': ['soap', 'shampoo', 'detergent', 'toothpaste', 'brush', 'tissue', 'paper', 'cleaning']
    }
    
    products = Product.objects.all()
    categorized = 0
    
    print(f"Found {products.count()} products to categorize...")
    
    for product in products:
        if product.category == 'other':  # Only categorize if not already set
            product_name_lower = product.name.lower()
            product_desc_lower = product.description.lower()
            
            # Check for category matches
            for category, keywords in category_keywords.items():
                if any(keyword in product_name_lower or keyword in product_desc_lower for keyword in keywords):
                    product.category = category
                    product.save()
                    print(f"Categorized '{product.name}' as {category}")
                    categorized += 1
                    break
    
    print(f"\nCategorization complete! {categorized} products were categorized.")
    print("\nRemaining products by category:")
    
    for category, _ in category_keywords.items():
        count = Product.objects.filter(category=category).count()
        print(f"  {category}: {count} products")
    
    other_count = Product.objects.filter(category='other').count()
    print(f"  other: {other_count} products")

if __name__ == "__main__":
    categorize_products()
