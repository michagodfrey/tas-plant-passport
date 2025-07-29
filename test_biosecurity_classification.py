#!/usr/bin/env python3
"""
Test script to verify biosecurity matter classification.
This tests the classification logic without requiring the full agent.
"""

import os
from dotenv import load_dotenv
from tas_data import commodity_db, BiosecurityCategory, CommodityType

# Load environment variables
load_dotenv()

def test_biosecurity_classification():
    """Test the biosecurity classification system."""
    print("🧪 Testing Biosecurity Matter Classification...")
    print("=" * 60)
    
    # Test cases for different categories
    test_cases = [
        # Permitted matter examples
        ("dried nuts", "Should be PERMITTED"),
        ("honey", "Should be PERMITTED"),
        ("processed foods", "Should be PERMITTED"),
        ("commercial pet food", "Should be PERMITTED"),
        
        # Prohibited matter examples
        ("cannabis seeds", "Should be PROHIBITED"),
        ("opium poppy", "Should be PROHIBITED"),
        ("tomato yellow leaf curl virus", "Should be PROHIBITED"),
        ("fire blight", "Should be PROHIBITED"),
        
        # Restricted matter examples (default)
        ("table grapes", "Should be RESTRICTED"),
        ("nursery stock", "Should be RESTRICTED"),
        ("citrus plants", "Should be RESTRICTED"),
        ("potato tubers", "Should be RESTRICTED"),
    ]
    
    for commodity_name, expected in test_cases:
        print(f"\n📦 Testing: {commodity_name}")
        print(f"Expected: {expected}")
        
        # Test classification
        classification = commodity_db.classify_biosecurity_matter(commodity_name, CommodityType.FRUIT)
        
        print(f"Result: {classification.category.value.upper()}")
        print(f"Reason: {classification.description}")
        print(f"Requirements: {classification.requirements}")
        
        # Check if classification matches expectation
        if "PERMITTED" in expected and classification.category == BiosecurityCategory.PERMITTED:
            print("✅ PASS")
        elif "PROHIBITED" in expected and classification.category == BiosecurityCategory.PROHIBITED:
            print("✅ PASS")
        elif "RESTRICTED" in expected and classification.category == BiosecurityCategory.RESTRICTED:
            print("✅ PASS")
        else:
            print("❌ FAIL - Unexpected classification")

def test_commodity_lookup():
    """Test commodity lookup with biosecurity classification."""
    print("\n" + "=" * 60)
    print("🔍 Testing Commodity Lookup with Classification...")
    print("=" * 60)
    
    test_commodities = [
        "table grapes",
        "potato",
        "citrus",
        "nursery stock"
    ]
    
    for commodity in test_commodities:
        print(f"\n🔍 Looking up: {commodity}")
        
        # Try exact lookup
        result = commodity_db.lookup(commodity)
        if result:
            print(f"Found: {result.name}")
            if result.biosecurity_category:
                print(f"Classification: {result.biosecurity_category.category.value.upper()}")
                print(f"Reason: {result.biosecurity_category.description}")
            else:
                print("No biosecurity classification found")
        else:
            print("Not found in database")
            
            # Try search
            matches = commodity_db.search(commodity)
            if matches:
                print(f"Found {len(matches)} similar matches:")
                for match in matches[:3]:  # Show first 3
                    print(f"  - {match.name}")
                    if match.biosecurity_category:
                        print(f"    Classification: {match.biosecurity_category.category.value.upper()}")
            else:
                print("No similar matches found")

def main():
    """Run all tests."""
    print("🧪 Testing Biosecurity Classification System...")
    print("=" * 60)
    
    # Test classification logic
    test_biosecurity_classification()
    
    # Test commodity lookup
    test_commodity_lookup()
    
    print("\n" + "=" * 60)
    print("✅ Biosecurity classification tests completed!")
    print("\nNext steps:")
    print("1. Test with the full agent: python agent_setup_tas.py")
    print("2. Try different commodities to see classification in action")

if __name__ == "__main__":
    main() 