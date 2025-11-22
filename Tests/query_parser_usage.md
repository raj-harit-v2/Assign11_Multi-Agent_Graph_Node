# Query Parser Usage Guide

## Overview

The Query Parser utility extracts structured information from queries, specifically:
1. **Property Units (BHK)**: Bedroom, Hall, Kitchen units (2BHK, 3BHK, etc.)
2. **Currency (Rs/INR)**: Indian Rupee amounts with full length formatting

## Features

### Property Unit Parsing (BHK)

- Extracts BHK patterns: `2BHK`, `3BHK`, `4BHK`, etc.
- Handles variations: `2 BHK`, `2-BHK`, `2bhk`
- Returns:
  - Number of bedrooms
  - Full description (e.g., "2 Bedrooms, Hall, Kitchen")
  - Original BHK value

### Currency Parsing (Rs/INR)

- Extracts currency patterns: `Rs 50 lakh`, `₹ 1 crore`, `INR 2 crores`
- Converts to numeric values
- Formats in:
  - Full length format: `50,00,000`
  - Indian number system: `50 Lakh`
- Handles units: hundreds, thousands, lakhs, crores

## Usage Examples

### Basic Usage

```python
from utils.query_parser import (
    PropertyUnitParser,
    CurrencyParser,
    QueryParser
)

# Parse property units
query1 = "Find 3BHK apartments in DLF Camelia"
bhk_info = PropertyUnitParser.parse_bhk(query1)
# Returns: {
#   "bedrooms": 3,
#   "bhk_value": "3BHK",
#   "full_description": "3 Bedrooms, Hall, Kitchen",
#   "found": True
# }

# Parse currency
query2 = "Properties costing Rs 50 lakh"
currency_info = CurrencyParser.parse_currency(query2)
# Returns: {
#   "amount": 5000000.0,
#   "original_text": "Rs 50 lakh",
#   "formatted_full": "5,000,000",
#   "formatted_indian": "50 Lakh",
#   "unit": "lakh",
#   "found": True
# }

# Combined parsing
query3 = "Find 3BHK apartments costing Rs 50 lakh"
result = QueryParser.parse(query3)
# Returns: {
#   "property": {...},
#   "currency": {...},
#   "has_property": True,
#   "has_currency": True
# }
```

### Integration with Perception Module

```python
from utils.query_parser import QueryParser

# In perception module, extract entities before processing
def build_perception_input(self, raw_input: str, ...):
    # Parse query for entities
    parsed = QueryParser.parse(raw_input)
    
    # Add extracted entities to perception input
    entities = []
    if parsed["has_property"]:
        bhk = parsed["property"]["bhk"]
        entities.append(f"Property: {bhk['full_description']}")
    
    if parsed["has_currency"]:
        currency = parsed["currency"]["currency"]
        entities.append(f"Budget: {currency['formatted_indian']}")
    
    # Use entities in perception prompt
    ...
```

### Integration with Decision Module

```python
from utils.query_parser import QueryParser

# In decision module, use parsed info for planning
def run(self, decision_input: dict):
    query = decision_input["original_query"]
    parsed = QueryParser.parse(query)
    
    # Use property info in plan
    if parsed["has_property"]:
        bhk = parsed["property"]["bhk"]
        # Plan to search for specific BHK type
        plan_text = f"Search for {bhk['full_description']} properties..."
    
    # Use currency info in plan
    if parsed["has_currency"]:
        currency = parsed["currency"]["currency"]
        # Plan to filter by price range
        plan_text += f" within budget of {currency['formatted_indian']}"
    
    ...
```

## Property Unit Patterns

| Pattern | Matches | Example |
|---------|---------|---------|
| `\d+BHK` | Standard | `2BHK`, `3BHK`, `4BHK` |
| `\d+ BHK` | With space | `2 BHK`, `3 BHK` |
| `\d+-BHK` | With hyphen | `2-BHK`, `3-BHK` |
| Case insensitive | Any case | `2bhk`, `3BHK`, `4Bhk` |

## Currency Patterns

| Pattern | Matches | Example |
|---------|---------|---------|
| `Rs \d+` | Basic | `Rs 50000` |
| `Rs. \d+` | With dot | `Rs. 50 lakh` |
| `₹ \d+` | Rupee symbol | `₹ 25 lakh` |
| `INR \d+` | ISO code | `INR 2 crore` |

## Currency Units

| Unit | Multiplier | Example |
|------|------------|---------|
| Hundred | 100 | `Rs 5 hundred` = 500 |
| Thousand | 1,000 | `Rs 50 thousand` = 50,000 |
| Lakh | 100,000 | `Rs 50 lakh` = 5,000,000 |
| Crore | 10,000,000 | `Rs 1 crore` = 10,000,000 |

## Indian Number Formatting

The parser formats numbers in Indian numbering system:

- **Units**: `500` → `500`
- **Hundreds**: `500` → `5 Hundred`
- **Thousands**: `5,000` → `5 Thousand`
- **Lakhs**: `5,00,000` → `5 Lakh`
- **Crores**: `1,00,00,000` → `1 Crore`
- **Combined**: `1,50,00,000` → `1 Crore 50 Lakh`

## Testing

Run the test file to verify functionality:

```bash
python Tests/test_query_parser.py
```

## Integration Points

### 1. Perception Module
- Extract entities before LLM processing
- Add structured entities to perception input
- Improve entity recognition accuracy

### 2. Decision Module
- Use parsed entities for planning
- Create more specific tool calls with extracted values
- Filter results based on property/currency criteria

### 3. Tool Execution
- Pass extracted values to property search tools
- Use currency amounts for price filtering
- Validate query requirements

## Example Integration

```python
# In agent_loop2.py or similar
from utils.query_parser import QueryParser

async def run(self, query: str, ...):
    # Parse query at the start
    parsed = QueryParser.parse(query)
    
    # Add to session state
    session.state["parsed_entities"] = parsed
    
    # Use in perception
    if parsed["has_property"]:
        # Add property filter to perception
        ...
    
    # Use in decision
    if parsed["has_currency"]:
        # Add budget constraint to decision
        ...
    
    # Use in tool execution
    if parsed["has_property"] and parsed["has_currency"]:
        # Search for specific BHK in price range
        ...
```

## Error Handling

The parser returns `None` if no pattern is found, so always check:

```python
result = PropertyUnitParser.parse_bhk(query)
if result:
    # Use result
    bedrooms = result["bedrooms"]
else:
    # No BHK found in query
    pass
```

## Future Enhancements

- Support for more property types (studio, penthouse, etc.)
- Support for other currencies (USD, EUR, etc.)
- Price range parsing (e.g., "Rs 20-50 lakh")
- Location extraction
- Amenity extraction

