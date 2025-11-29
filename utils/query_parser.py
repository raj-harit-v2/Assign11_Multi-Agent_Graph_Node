"""
Query Parser Utility for Session 10
Extracts property units (BHK) and currency (Rs) from queries.
"""

import re
from typing import Dict, Optional, Tuple


class PropertyUnitParser:
    """Parser for property units (BHK - Bedroom, Hall, Kitchen)."""
    
    # BHK patterns: 1BHK, 2BHK, 3BHK, 4BHK, 5BHK, 6BHK, 7BHK, etc.
    BHK_PATTERN = re.compile(r'(\d+)\s*BHK', re.IGNORECASE)
    
    # Alternative patterns: 2 BHK, 2-BHK, 2bhk, etc.
    BHK_PATTERN_ALT = re.compile(r'(\d+)\s*[-]?\s*BHK', re.IGNORECASE)
    
    # Penthouse pattern
    PENTHOUSE_PATTERN = re.compile(r'\bpenthouse\b', re.IGNORECASE)
    
    # Amenities patterns (common property amenities)
    AMENITIES_PATTERNS = {
        'clubhouse': re.compile(r'\bclubhouse\b', re.IGNORECASE),
        'pool': re.compile(r'\b(swimming\s*)?pool\b', re.IGNORECASE),
        'gym': re.compile(r'\b(gym|gymnasium|fitness\s*center)\b', re.IGNORECASE),
        'parking': re.compile(r'\b(parking|car\s*park)\b', re.IGNORECASE),
        'garden': re.compile(r'\b(garden|landscaped\s*garden)\b', re.IGNORECASE),
        'security': re.compile(r'\b(security|24/7\s*security)\b', re.IGNORECASE),
        'playground': re.compile(r'\b(playground|kids\s*play\s*area)\b', re.IGNORECASE),
        'lift': re.compile(r'\b(lift|elevator)\b', re.IGNORECASE),
        'power_backup': re.compile(r'\b(power\s*backup|generator)\b', re.IGNORECASE),
        'wifi': re.compile(r'\b(wifi|wi-fi|internet)\b', re.IGNORECASE),
    }
    
    @staticmethod
    def parse_bhk(query: str) -> Optional[Dict[str, any]]:
        """
        Parse BHK (Bedroom, Hall, Kitchen) from query.
        Supports 1BHK, 2BHK, 3BHK, 4BHK, 5BHK, 6BHK, 7BHK, and penthouse.
        
        Args:
            query: Query text to parse
        
        Returns:
            Dict with:
                - bedrooms: int (number of bedrooms, 0 for penthouse)
                - bhk_value: str (original BHK string like "2BHK" or "penthouse")
                - full_description: str (e.g., "2 Bedrooms, Hall, Kitchen" or "Penthouse")
                - category: int (1-7 for BHK, 8 for penthouse)
                - found: bool
            Or None if not found
        """
        query_lower = query.lower()
        
        # Check for penthouse first
        if PropertyUnitParser.PENTHOUSE_PATTERN.search(query):
            return {
                "bedrooms": 0,  # Penthouse doesn't have standard BHK count
                "bhk_value": "penthouse",
                "full_description": "Penthouse",
                "category": 8,  # Category 8 for penthouse
                "found": True
            }
        
        # Try main pattern first
        match = PropertyUnitParser.BHK_PATTERN.search(query)
        if not match:
            # Try alternative pattern
            match = PropertyUnitParser.BHK_PATTERN_ALT.search(query)
        
        if match:
            bedrooms = int(match.group(1))
            bhk_value = match.group(0)
            
            # Validate BHK range (1-7)
            if bedrooms < 1 or bedrooms > 7:
                return None
            
            # Build full description
            if bedrooms == 1:
                full_desc = "1 Bedroom, Hall, Kitchen"
            else:
                full_desc = f"{bedrooms} Bedrooms, Hall, Kitchen"
            
            return {
                "bedrooms": bedrooms,
                "bhk_value": bhk_value,
                "full_description": full_desc,
                "category": bedrooms,  # Category 1-7 for BHK
                "found": True
            }
        
        return None
    
    @staticmethod
    def parse_all_bhk(query: str) -> list[Dict[str, any]]:
        """
        Parse all BHK types mentioned in query (e.g., "1BHK, 2BHK, 3BHK").
        
        Args:
            query: Query text to parse
        
        Returns:
            List of BHK info dicts, sorted by category (1-8)
        """
        results = []
        
        # Check for penthouse
        if PropertyUnitParser.PENTHOUSE_PATTERN.search(query):
            results.append({
                "bedrooms": 0,
                "bhk_value": "penthouse",
                "full_description": "Penthouse",
                "category": 8,
                "found": True
            })
        
        # Find all BHK patterns
        matches = PropertyUnitParser.BHK_PATTERN.finditer(query)
        for match in matches:
            bedrooms = int(match.group(1))
            if 1 <= bedrooms <= 7:  # Valid range
                bhk_value = match.group(0)
                if bedrooms == 1:
                    full_desc = "1 Bedroom, Hall, Kitchen"
                else:
                    full_desc = f"{bedrooms} Bedrooms, Hall, Kitchen"
                
                results.append({
                    "bedrooms": bedrooms,
                    "bhk_value": bhk_value,
                    "full_description": full_desc,
                    "category": bedrooms,
                    "found": True
                })
        
        # Remove duplicates and sort by category
        seen = set()
        unique_results = []
        for result in sorted(results, key=lambda x: x["category"]):
            key = result["category"]
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        return unique_results
    
    @staticmethod
    def parse_amenities(query: str) -> list[str]:
        """
        Parse amenities from query (clubhouse, pool, gym, etc.).
        
        Args:
            query: Query text to parse
        
        Returns:
            List of found amenities (normalized names)
        """
        found_amenities = []
        
        for amenity_name, pattern in PropertyUnitParser.AMENITIES_PATTERNS.items():
            if pattern.search(query):
                found_amenities.append(amenity_name)
        
        return found_amenities
    
    @staticmethod
    def extract_property_info(query: str) -> Dict[str, any]:
        """
        Extract all property-related information from query.
        Includes BHK categorization (1-7, penthouse) and amenities.
        
        Args:
            query: Query text to parse
        
        Returns:
            Dict with property information including:
                - bhk: Single BHK info (first found)
                - all_bhk: List of all BHK types found
                - amenities: List of amenities found
                - property_type: Primary property type
                - categories: List of BHK categories (1-7, 8 for penthouse)
        """
        result = {
            "has_property_query": False,
            "bhk": None,
            "all_bhk": [],
            "amenities": [],
            "property_type": None,
            "categories": []
        }
        
        # Check for BHK (all types)
        all_bhk = PropertyUnitParser.parse_all_bhk(query)
        if all_bhk:
            result["has_property_query"] = True
            result["all_bhk"] = all_bhk
            result["bhk"] = all_bhk[0]  # First found as primary
            result["categories"] = [bhk["category"] for bhk in all_bhk]
            
            # Set property type
            if len(all_bhk) == 1:
                bhk_info = all_bhk[0]
                if bhk_info["category"] == 8:
                    result["property_type"] = "penthouse"
                else:
                    result["property_type"] = bhk_info["bhk_value"]
            else:
                # Multiple types
                types = [bhk["bhk_value"] for bhk in all_bhk]
                result["property_type"] = ", ".join(types)
        
        # Check for amenities
        amenities = PropertyUnitParser.parse_amenities(query)
        if amenities:
            result["has_property_query"] = True
            result["amenities"] = amenities
        
        return result


class CurrencyParser:
    """Parser for Indian Rupees (Rs) currency amounts."""
    
    # Currency patterns
    RS_PATTERN = re.compile(r'Rs\.?\s*([\d,.\s]+)\s*(lakh|lakhs|crore|crores|lakh|thousand|thousands|hundred|hundreds)?', re.IGNORECASE)
    RS_PATTERN_ALT = re.compile(r'₹\s*([\d,.\s]+)\s*(lakh|lakhs|crore|crores|lakh|thousand|thousands|hundred|hundreds)?', re.IGNORECASE)
    INDIAN_RUPEE_PATTERN = re.compile(r'INR\s*([\d,.\s]+)\s*(lakh|lakhs|crore|crores|lakh|thousand|thousands|hundred|hundreds)?', re.IGNORECASE)
    
    # Indian number system multipliers
    MULTIPLIERS = {
        'hundred': 100,
        'hundreds': 100,
        'thousand': 1000,
        'thousands': 1000,
        'lakh': 100000,
        'lakhs': 100000,
        'crore': 10000000,
        'crores': 10000000
    }
    
    @staticmethod
    def parse_currency(query: str) -> Optional[Dict[str, any]]:
        """
        Parse currency amount from query (Indian Rupees).
        
        Args:
            query: Query text to parse
        
        Returns:
            Dict with:
                - amount: float (numeric amount)
                - original_text: str (original currency string)
                - formatted_full: str (full length format)
                - formatted_indian: str (Indian number format with commas)
                - unit: str (lakh, crore, etc.)
                - found: bool
            Or None if not found
        """
        # Try different patterns
        match = CurrencyParser.RS_PATTERN.search(query)
        if not match:
            match = CurrencyParser.RS_PATTERN_ALT.search(query)
        if not match:
            match = CurrencyParser.INDIAN_RUPEE_PATTERN.search(query)
        
        if match:
            amount_str = match.group(1).strip().replace(',', '').replace(' ', '')
            unit = match.group(2).lower() if match.group(2) else None
            
            try:
                # Parse base amount
                base_amount = float(amount_str)
                
                # Apply multiplier if unit is specified
                if unit and unit in CurrencyParser.MULTIPLIERS:
                    numeric_amount = base_amount * CurrencyParser.MULTIPLIERS[unit]
                else:
                    numeric_amount = base_amount
                
                original_text = match.group(0)
                
                # Format as full length number
                formatted_full = f"{int(numeric_amount):,}"
                
                # Format in Indian number system (lakhs, crores)
                formatted_indian = CurrencyParser._format_indian_number(numeric_amount)
                
                return {
                    "amount": numeric_amount,
                    "original_text": original_text,
                    "formatted_full": formatted_full,
                    "formatted_indian": formatted_indian,
                    "unit": unit or "rupees",
                    "found": True
                }
            except ValueError:
                return None
        
        return None
    
    @staticmethod
    def _format_indian_number(amount: float) -> str:
        """
        Format number in Indian numbering system (lakhs, crores).
        
        Args:
            amount: Numeric amount
        
        Returns:
            Formatted string in Indian format
        """
        amount_int = int(amount)
        
        # Crores (1 crore = 10 million)
        if amount_int >= 10000000:
            crores = amount_int // 10000000
            remainder = amount_int % 10000000
            if remainder == 0:
                return f"{crores} Crore" if crores == 1 else f"{crores} Crores"
            else:
                lakhs = remainder // 100000
                if lakhs == 0:
                    return f"{crores} Crore {remainder:,}"
                else:
                    return f"{crores} Crore {lakhs} Lakh"
        
        # Lakhs (1 lakh = 100,000)
        elif amount_int >= 100000:
            lakhs = amount_int // 100000
            remainder = amount_int % 100000
            if remainder == 0:
                return f"{lakhs} Lakh" if lakhs == 1 else f"{lakhs} Lakhs"
            else:
                return f"{lakhs} Lakh {remainder:,}"
        
        # Thousands
        elif amount_int >= 1000:
            thousands = amount_int // 1000
            remainder = amount_int % 1000
            if remainder == 0:
                return f"{thousands} Thousand" if thousands == 1 else f"{thousands} Thousands"
            else:
                return f"{thousands} Thousand {remainder:,}"
        
        # Hundreds
        elif amount_int >= 100:
            hundreds = amount_int // 100
            remainder = amount_int % 100
            if remainder == 0:
                return f"{hundreds} Hundred" if hundreds == 1 else f"{hundreds} Hundreds"
            else:
                return f"{hundreds} Hundred {remainder:,}"
        
        # Units
        else:
            return f"{amount_int:,}"
    
    @staticmethod
    def extract_currency_info(query: str) -> Dict[str, any]:
        """
        Extract all currency-related information from query.
        
        Args:
            query: Query text to parse
        
        Returns:
            Dict with currency information
        """
        result = {
            "has_currency": False,
            "currency": None,
            "currency_type": None
        }
        
        # Check for Indian Rupees
        currency_info = CurrencyParser.parse_currency(query)
        if currency_info:
            result["has_currency"] = True
            result["currency"] = currency_info
            result["currency_type"] = "INR"
        
        return result


class QueryParser:
    """Main query parser that combines property and currency parsing."""
    
    @staticmethod
    def parse(query: str) -> Dict[str, any]:
        """
        Parse query for property units and currency.
        
        Args:
            query: Query text to parse
        
        Returns:
            Dict with:
                - property: Dict with property information
                - currency: Dict with currency information
                - has_property: bool
                - has_currency: bool
        """
        property_info = PropertyUnitParser.extract_property_info(query)
        currency_info = CurrencyParser.extract_currency_info(query)
        
        return {
            "property": property_info,
            "currency": currency_info,
            "has_property": property_info["has_property_query"],
            "has_currency": currency_info["has_currency"]
        }
    
    @staticmethod
    def extract_entities(query: str) -> Dict[str, any]:
        """
        Extract all entities from query (property, currency, etc.).
        
        Args:
            query: Query text to parse
        
        Returns:
            Dict with extracted entities
        """
        parsed = QueryParser.parse(query)
        
        entities = {
            "property_units": [],
            "currency_amounts": []
        }
        
        if parsed["has_property"]:
            prop_info = parsed["property"]
            
            # Add all BHK types
            for bhk in prop_info.get("all_bhk", []):
                entities["property_units"].append({
                    "type": "BHK" if bhk["category"] <= 7 else "PENTHOUSE",
                    "bedrooms": bhk["bedrooms"],
                    "value": bhk["bhk_value"],
                    "description": bhk["full_description"],
                    "category": bhk["category"]
                })
            
            # Add amenities
            amenities = prop_info.get("amenities", [])
            if amenities:
                entities["amenities"] = amenities
        
        if parsed["has_currency"]:
            currency = parsed["currency"]["currency"]
            if currency:
                entities["currency_amounts"].append({
                    "type": "INR",
                    "amount": currency["amount"],
                    "formatted": currency["formatted_full"],
                    "indian_format": currency["formatted_indian"],
                    "unit": currency["unit"]
                })
        
        return entities


# Convenience functions
def parse_property_units(query: str) -> Optional[Dict[str, any]]:
    """Parse property units (BHK) from query."""
    return PropertyUnitParser.parse_bhk(query)


def parse_currency_amount(query: str) -> Optional[Dict[str, any]]:
    """Parse currency amount from query."""
    return CurrencyParser.parse_currency(query)


def parse_query(query: str) -> Dict[str, any]:
    """Parse query for all entities."""
    return QueryParser.parse(query)

