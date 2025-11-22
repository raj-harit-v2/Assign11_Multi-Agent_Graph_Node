"""
Test file for Query Parser Utility
Tests property unit (BHK) and currency (Rs) parsing.
"""

import sys
import io
from pathlib import Path

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.query_parser import (
    PropertyUnitParser,
    CurrencyParser,
    QueryParser,
    parse_property_units,
    parse_currency_amount,
    parse_query
)


def test_property_units():
    """Test property unit (BHK) parsing."""
    print("\n" + "=" * 80)
    print("TESTING PROPERTY UNIT PARSING (BHK)")
    print("=" * 80)
    
    test_cases = [
        "Find number of BHK variants available in DLF Camelia",
        "What are the price ranges for 3BHK apartments in DLF Camelia?",
        "List all available 2 BHK property types",
        "Find amenities available in 4-BHK residential complex",
        "What is the total number of units in 2bhk project?",
        "Show me 3 BHK floor plans",
        "Price for 1BHK unit",
        "Available 5BHK properties"
    ]
    
    for query in test_cases:
        print(f"\nQuery: {query}")
        result = PropertyUnitParser.parse_bhk(query)
        if result:
            print(f"  [FOUND] Bedrooms: {result['bedrooms']}")
            print(f"  [FOUND] BHK Value: {result['bhk_value']}")
            print(f"  [FOUND] Description: {result['full_description']}")
        else:
            print(f"  [NOT FOUND] No BHK pattern detected")


def test_currency():
    """Test currency (Rs) parsing."""
    print("\n" + "=" * 80)
    print("TESTING CURRENCY PARSING (Rs/INR)")
    print("=" * 80)
    
    test_cases = [
        "What are the price ranges for 3BHK apartments costing Rs 50 lakh?",
        "Find properties under Rs. 1 crore",
        "Price is ₹ 25 lakhs",
        "Budget is Rs 5,00,000",
        "Cost around 10 lakh rupees",
        "Properties between Rs 20 lakh and Rs 50 lakh",
        "Show me properties for Rs 1.5 crore",
        "Price range: Rs 75,000",
        "Budget: INR 2 crores"
    ]
    
    for query in test_cases:
        print(f"\nQuery: {query}")
        result = CurrencyParser.parse_currency(query)
        if result:
            print(f"  [FOUND] Amount: {result['amount']:,.2f}")
            print(f"  [FOUND] Original: {result['original_text']}")
            print(f"  [FOUND] Full Format: {result['formatted_full']}")
            print(f"  [FOUND] Indian Format: {result['formatted_indian']}")
            print(f"  [FOUND] Unit: {result['unit']}")
        else:
            print(f"  [NOT FOUND] No currency pattern detected")


def test_combined_parsing():
    """Test combined property and currency parsing."""
    print("\n" + "=" * 80)
    print("TESTING COMBINED PARSING (Property + Currency)")
    print("=" * 80)
    
    test_cases = [
        "Find 3BHK apartments in DLF Camelia costing Rs 50 lakh",
        "What are the price ranges for 2BHK apartments under Rs 1 crore?",
        "Show me 4BHK properties between Rs 20 lakh and Rs 50 lakh",
        "Find number of BHK variants available in DLF Camelia",
        "Properties for Rs 25 lakhs",
        "2BHK apartment for sale"
    ]
    
    for query in test_cases:
        print(f"\nQuery: {query}")
        result = QueryParser.parse(query)
        
        print(f"  Has Property: {result['has_property']}")
        if result['has_property']:
            bhk = result['property']['bhk']
            if bhk:
                print(f"    - BHK: {bhk['bhk_value']} ({bhk['full_description']})")
        
        print(f"  Has Currency: {result['has_currency']}")
        if result['has_currency']:
            currency = result['currency']['currency']
            if currency:
                print(f"    - Amount: {currency['formatted_full']} ({currency['formatted_indian']})")


def test_entity_extraction():
    """Test entity extraction."""
    print("\n" + "=" * 80)
    print("TESTING ENTITY EXTRACTION")
    print("=" * 80)
    
    test_cases = [
        "Find 3BHK apartments in DLF Camelia costing Rs 50 lakh",
        "What are the price ranges for 2BHK apartments under Rs 1 crore?",
        "Show me 4BHK properties between Rs 20 lakh and Rs 50 lakh"
    ]
    
    for query in test_cases:
        print(f"\nQuery: {query}")
        entities = QueryParser.extract_entities(query)
        
        print(f"  Property Units: {len(entities['property_units'])}")
        for prop in entities['property_units']:
            print(f"    - {prop['description']} ({prop['value']})")
        
        print(f"  Currency Amounts: {len(entities['currency_amounts'])}")
        for curr in entities['currency_amounts']:
            print(f"    - {curr['indian_format']} ({curr['formatted']})")


def test_edge_cases():
    """Test edge cases and variations."""
    print("\n" + "=" * 80)
    print("TESTING EDGE CASES")
    print("=" * 80)
    
    # Property edge cases
    print("\n[Property Edge Cases]")
    edge_property = [
        "2bhk",  # lowercase
        "3 BHK",  # space
        "4-BHK",  # hyphen
        "1BHK",   # single digit
        "10BHK",  # double digit
    ]
    
    for query in edge_property:
        result = parse_property_units(query)
        if result:
            print(f"  '{query}' -> {result['bedrooms']} bedrooms ({result['full_description']})")
    
    # Currency edge cases
    print("\n[Currency Edge Cases]")
    edge_currency = [
        "Rs 1 lakh",
        "Rs 1.5 crore",
        "Rs 50,000",
        "₹ 25 lakhs",
        "INR 2 crores",
        "Rs 100",
        "Rs 1,00,000",
    ]
    
    for query in edge_currency:
        result = parse_currency_amount(query)
        if result:
            print(f"  '{query}' -> {result['formatted_indian']} ({result['formatted_full']})")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("QUERY PARSER TEST SUITE")
    print("=" * 80)
    
    test_property_units()
    test_currency()
    test_combined_parsing()
    test_entity_extraction()
    test_edge_cases()
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()

