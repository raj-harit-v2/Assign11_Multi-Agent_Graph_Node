"""
Query Parser Utility for Session 10
Extracts property units (BHK) and currency (Rs) from queries.
"""

import re
from typing import Dict, Optional, Tuple


class PropertyUnitParser:
    """Parser for property units (BHK - Bedroom, Hall, Kitchen)."""
    
    # BHK patterns: 2BHK, 3BHK, 4BHK, etc.
    BHK_PATTERN = re.compile(r'(\d+)\s*BHK', re.IGNORECASE)
    
    # Alternative patterns: 2 BHK, 2-BHK, 2bhk, etc.
    BHK_PATTERN_ALT = re.compile(r'(\d+)\s*[-]?\s*BHK', re.IGNORECASE)
    
    @staticmethod
    def parse_bhk(query: str) -> Optional[Dict[str, any]]:
        """
        Parse BHK (Bedroom, Hall, Kitchen) from query.
        
        Args:
            query: Query text to parse
        
        Returns:
            Dict with:
                - bedrooms: int (number of bedrooms)
                - bhk_value: str (original BHK string like "2BHK")
                - full_description: str (e.g., "2 Bedrooms, Hall, Kitchen")
                - found: bool
            Or None if not found
        """
        query_lower = query.lower()
        
        # Try main pattern first
        match = PropertyUnitParser.BHK_PATTERN.search(query)
        if not match:
            # Try alternative pattern
            match = PropertyUnitParser.BHK_PATTERN_ALT.search(query)
        
        if match:
            bedrooms = int(match.group(1))
            bhk_value = match.group(0)
            
            # Build full description
            if bedrooms == 1:
                full_desc = "1 Bedroom, Hall, Kitchen"
            else:
                full_desc = f"{bedrooms} Bedrooms, Hall, Kitchen"
            
            return {
                "bedrooms": bedrooms,
                "bhk_value": bhk_value,
                "full_description": full_desc,
                "found": True
            }
        
        return None
    
    @staticmethod
    def extract_property_info(query: str) -> Dict[str, any]:
        """
        Extract all property-related information from query.
        
        Args:
            query: Query text to parse
        
        Returns:
            Dict with property information including BHK
        """
        result = {
            "has_property_query": False,
            "bhk": None,
            "property_type": None
        }
        
        # Check for BHK
        bhk_info = PropertyUnitParser.parse_bhk(query)
        if bhk_info:
            result["has_property_query"] = True
            result["bhk"] = bhk_info
            result["property_type"] = f"{bhk_info['bedrooms']}BHK"
        
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
            bhk = parsed["property"]["bhk"]
            if bhk:
                entities["property_units"].append({
                    "type": "BHK",
                    "bedrooms": bhk["bedrooms"],
                    "value": bhk["bhk_value"],
                    "description": bhk["full_description"]
                })
        
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

