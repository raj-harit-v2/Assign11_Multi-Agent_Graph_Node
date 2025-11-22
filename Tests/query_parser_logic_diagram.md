# Query Parser Logic Flow Diagram

## Overall Flow

```mermaid
flowchart TD
    Start[Query Input] --> Parse[QueryParser.parse]
    
    Parse --> PropParser[PropertyUnitParser]
    Parse --> CurrParser[CurrencyParser]
    
    PropParser --> CheckBHK{Find BHK Pattern?}
    CheckBHK -->|Yes| ExtractBHK[Extract Number<br/>e.g., 2 from '2BHK']
    CheckBHK -->|No| NoBHK[No Property Found]
    
    ExtractBHK --> BuildDesc[Build Description<br/>'2 Bedrooms, Hall, Kitchen']
    BuildDesc --> BHKResult[BHK Result]
    
    CurrParser --> CheckCurrency{Find Currency Pattern?}
    CheckCurrency -->|Yes| ExtractAmount[Extract Amount<br/>e.g., '50 lakh']
    CheckCurrency -->|No| NoCurrency[No Currency Found]
    
    ExtractAmount --> CheckUnit{Has Unit?<br/>lakh/crore/thousand}
    CheckUnit -->|Yes| ApplyMultiplier[Apply Multiplier<br/>50 * 100000 = 5000000]
    CheckUnit -->|No| UseAmount[Use Amount As-Is]
    
    ApplyMultiplier --> FormatIndian[Format Indian Number<br/>'50 Lakhs']
    UseAmount --> FormatIndian
    FormatIndian --> FormatFull[Format Full Number<br/>'5,000,000']
    FormatFull --> CurrencyResult[Currency Result]
    
    BHKResult --> Combine[Combine Results]
    CurrencyResult --> Combine
    NoBHK --> Combine
    NoCurrency --> Combine
    
    Combine --> FinalResult[Final Parsed Result]
    
    style ExtractBHK fill:#ccffcc
    style ExtractAmount fill:#ccffcc
    style FormatIndian fill:#ffe6cc
    style FinalResult fill:#e1f5ff
```

## Property Unit Parsing (BHK)

```mermaid
flowchart LR
    Input[Query: 'Find 3BHK apartments'] --> Pattern[Regex Pattern<br/>\d+BHK]
    
    Pattern --> Match{Match Found?}
    Match -->|Yes| Extract[Extract Number: 3]
    Match -->|No| ReturnNone[Return None]
    
    Extract --> Build[Build Description<br/>'3 Bedrooms, Hall, Kitchen']
    Build --> Return[Return Result]
    
    style Extract fill:#ccffcc
    style Build fill:#ffe6cc
    style Return fill:#e1f5ff
```

## Currency Parsing (Rs/INR)

```mermaid
flowchart TD
    Input[Query: 'Rs 50 lakh'] --> Pattern1[Try Pattern 1<br/>Rs\.?\s*\d+]
    Pattern1 --> Match1{Match?}
    
    Match1 -->|No| Pattern2[Try Pattern 2<br/>₹\s*\d+]
    Match2{Match?} -->|No| Pattern3[Try Pattern 3<br/>INR\s*\d+]
    Pattern3 --> Match3{Match?}
    
    Match1 -->|Yes| Extract[Extract: '50 lakh']
    Match2 -->|Yes| Extract
    Match3 -->|Yes| Extract
    
    Extract --> ParseNum[Parse Number: 50]
    Extract --> ParseUnit[Parse Unit: 'lakh']
    
    ParseUnit --> CheckUnit{Unit in<br/>MULTIPLIERS?}
    CheckUnit -->|Yes| Multiply[50 * 100000<br/>= 5000000]
    CheckUnit -->|No| UseNum[Use Number: 50]
    
    Multiply --> Format1[Format Indian<br/>'50 Lakhs']
    UseNum --> Format1
    Format1 --> Format2[Format Full<br/>'5,000,000']
    Format2 --> Return[Return Result]
    
    style Multiply fill:#ccffcc
    style Format1 fill:#ffe6cc
    style Format2 fill:#ffe6cc
    style Return fill:#e1f5ff
```

## Indian Number Formatting Logic

```mermaid
flowchart TD
    Amount[Amount: 15000000] --> CheckCrore{>= 1 Crore?}
    
    CheckCrore -->|Yes| CalcCrore[Calculate Crores<br/>15000000 / 10000000 = 1]
    CalcCrore --> CalcRemainder[Remainder: 5000000]
    CalcRemainder --> CheckLakh{Remainder >= 1 Lakh?}
    
    CheckLakh -->|Yes| CalcLakh[Calculate Lakhs<br/>5000000 / 100000 = 50]
    CalcLakh --> Format[Format: '1 Crore 50 Lakh']
    
    CheckCrore -->|No| CheckLakh2{>= 1 Lakh?}
    CheckLakh2 -->|Yes| CalcLakh2[Calculate Lakhs]
    CalcLakh2 --> Format2[Format: 'X Lakhs']
    
    CheckLakh2 -->|No| CheckThousand{>= 1 Thousand?}
    CheckThousand -->|Yes| Format3[Format: 'X Thousands']
    CheckThousand -->|No| Format4[Format: 'X']
    
    Format --> Return[Return Formatted String]
    Format2 --> Return
    Format3 --> Return
    Format4 --> Return
    
    style CalcCrore fill:#ccffcc
    style CalcLakh fill:#ccffcc
    style Return fill:#e1f5ff
```

## Example: Combined Parsing

```mermaid
sequenceDiagram
    participant Query as Query Input
    participant Parser as QueryParser
    participant Prop as PropertyUnitParser
    participant Curr as CurrencyParser
    participant Result as Final Result
    
    Query->>Parser: "Find 3BHK costing Rs 50 lakh"
    Parser->>Prop: parse_bhk(query)
    Prop->>Prop: Match pattern "3BHK"
    Prop->>Prop: Extract: bedrooms=3
    Prop->>Prop: Build: "3 Bedrooms, Hall, Kitchen"
    Prop-->>Parser: {bedrooms: 3, ...}
    
    Parser->>Curr: parse_currency(query)
    Curr->>Curr: Match pattern "Rs 50 lakh"
    Curr->>Curr: Extract: amount=50, unit="lakh"
    Curr->>Curr: Calculate: 50 * 100000 = 5000000
    Curr->>Curr: Format: "50 Lakhs" / "5,000,000"
    Curr-->>Parser: {amount: 5000000, ...}
    
    Parser->>Parser: Combine results
    Parser-->>Result: {
        has_property: true,
        has_currency: true,
        property: {...},
        currency: {...}
    }
```

## Integration Points

```mermaid
graph TB
    Query[User Query] --> Parser[QueryParser]
    
    Parser --> Entities[Extracted Entities]
    
    Entities --> Perception[Perception Module<br/>Better Entity Recognition]
    Entities --> Decision[Decision Module<br/>Specific Planning]
    Entities --> Tools[Tool Execution<br/>Filtered Search]
    
    Perception --> LLM[LLM Processing]
    Decision --> Plan[Plan Generation]
    Tools --> Results[Search Results]
    
    style Parser fill:#e1f5ff
    style Entities fill:#ccffcc
    style Perception fill:#ffe6cc
    style Decision fill:#ffe6cc
    style Tools fill:#ffe6cc
```

