# Session 10 Architecture Diagrams

## System Architecture

```mermaid
graph TB
    User[User Query] --> AgentLoop[Agent Loop]
    AgentLoop --> Perception[Perception Module]
    AgentLoop --> Decision[Decision Module]
    AgentLoop --> Executor[Action Executor]
    AgentLoop --> ControlManager[Control Manager]
    AgentLoop --> CSVManager[CSV Manager]
    
    Executor --> MCP[Multi-MCP Servers]
    Executor --> HumanLoop1[Human-in-Loop<br/>Tool Failure]
    
    ControlManager --> HumanLoop2[Human-in-Loop<br/>Plan Failure]
    
    CSVManager --> ToolPerfCSV[tool_performance.csv]
    CSVManager --> QueryCSV[query_text.csv]
    
    AgentLoop --> Memory[Memory Search]
    AgentLoop --> SessionLog[Session Log]
    
    Simulator[Simulator] --> AgentLoop
    Simulator --> SleepManager[Sleep Manager]
    
    Statistics[Statistics Generator] --> ToolPerfCSV
    Statistics --> StatsMD[Result_Stats.md]
    
    style AgentLoop fill:#e1f5ff
    style HumanLoop1 fill:#ffe1f5
    style HumanLoop2 fill:#ffe1f5
    style ControlManager fill:#fff5e1
    style CSVManager fill:#e1ffe1
```

## Agent Loop Flow

```mermaid
sequenceDiagram
    participant User
    participant AgentLoop
    participant Perception
    participant Decision
    participant Executor
    participant ControlManager
    participant HumanLoop
    participant CSVManager
    
    User->>AgentLoop: Query
    AgentLoop->>CSVManager: Add Query (get Query_Id)
    AgentLoop->>Perception: Run Perception
    Perception-->>AgentLoop: Perception Result
    
    alt Goal Achieved
        AgentLoop->>CSVManager: Log Success
        AgentLoop-->>User: Final Answer
    else Need Planning
        AgentLoop->>Decision: Create Plan
        Decision-->>AgentLoop: Plan with Steps
        
        loop For Each Step
            AgentLoop->>ControlManager: Check Step Limit
            alt Limit Reached
                ControlManager->>HumanLoop: Ask for Plan
                HumanLoop-->>AgentLoop: Modified Plan
            end
            
            AgentLoop->>Executor: Execute Step
            Executor->>Executor: Retry (up to MAX_RETRIES)
            
            alt All Retries Failed
                Executor->>HumanLoop: Ask for Result
                HumanLoop-->>Executor: User Result
            end
            
            Executor-->>AgentLoop: Execution Result
            AgentLoop->>Perception: Evaluate Result
            Perception-->>AgentLoop: Perception Snapshot
            
            alt Goal Achieved
                AgentLoop->>CSVManager: Log Success
                AgentLoop-->>User: Final Answer
            else Continue
                AgentLoop->>Decision: Plan Next Step
            end
        end
    end
    
    AgentLoop->>CSVManager: Log Performance
```

## Tool Failure and Retry Flow

```mermaid
flowchart TD
    Start[Start Tool Execution] --> Execute[Execute Tool]
    Execute --> Success{Success?}
    Success -->|Yes| ReturnSuccess[Return Success Result]
    Success -->|No| CheckRetries{Retry Count < MAX_RETRIES?}
    
    CheckRetries -->|Yes| IncrementRetry[Increment Retry Count]
    IncrementRetry --> Sleep[Sleep 1 second]
    Sleep --> Execute
    
    CheckRetries -->|No| AllRetriesFailed[All Retries Exhausted]
    AllRetriesFailed --> HumanLoop[Trigger Human-in-Loop]
    HumanLoop --> UserInput[User Provides Result]
    UserInput --> ReturnUserResult[Return User Result as Success]
    
    ReturnSuccess --> End[End]
    ReturnUserResult --> End
    
    style HumanLoop fill:#ffe1f5
    style AllRetriesFailed fill:#ffe1e1
    style ReturnSuccess fill:#e1ffe1
```

## Plan Failure and Human-in-Loop Flow

```mermaid
flowchart TD
    Start[Agent Loop Running] --> CheckStep[Check Current Step Index]
    CheckStep --> LimitCheck{Step Index >= MAX_STEPS?}
    
    LimitCheck -->|No| Continue[Continue Normal Execution]
    LimitCheck -->|Yes| PlanFailed[Plan Limit Reached]
    
    PlanFailed --> GetContext[Build Context:<br/>- Current Plan<br/>- Step Count<br/>- Failure Reason]
    GetContext --> GetSuggestion[Get Suggested Plan from Decision]
    GetSuggestion --> HumanLoop[Trigger Human-in-Loop]
    
    HumanLoop --> PresentInfo[Present to User:<br/>- Current Failed Plan<br/>- Suggested New Plan]
    PresentInfo --> UserChoice{User Choice}
    
    UserChoice -->|Accept| UseSuggested[Use Suggested Plan]
    UserChoice -->|Modify| GetModified[Get Modified Plan from User]
    UserChoice -->|Custom| GetCustom[Get Custom Plan from User]
    
    UseSuggested --> CreateStep[Create CONCLUDE Step]
    GetModified --> CreateStep
    GetCustom --> CreateStep
    
    CreateStep --> MarkComplete[Mark Session Complete]
    MarkComplete --> LogCSV[Log to CSV]
    LogCSV --> End[End]
    
    Continue --> End
    
    style HumanLoop fill:#ffe1f5
    style PlanFailed fill:#ffe1e1
    style MarkComplete fill:#e1ffe1
```

## Data Flow Diagram

```mermaid
graph LR
    Query[User Query] --> QueryCSV[query_text.csv<br/>Query_Id Generated]
    QueryCSV --> AgentLoop[Agent Loop]
    
    AgentLoop --> Execution[Step Execution]
    Execution --> ToolResult[Tool Result]
    
    ToolResult --> PerfCSV[tool_performance.csv<br/>- Test_Id<br/>- Query_Id<br/>- Plan_Used<br/>- Result_Status<br/>- Retry_Count<br/>- Error_Message]
    
    PerfCSV --> Statistics[Statistics Generator]
    Statistics --> StatsMD[Result_Stats.md<br/>- Success Rate<br/>- Tool Performance<br/>- Failure Analysis]
    
    style QueryCSV fill:#e1ffe1
    style PerfCSV fill:#e1ffe1
    style StatsMD fill:#fff5e1
```

## Simulator Flow

```mermaid
flowchart TD
    Start[Start Simulator] --> LoadQueries[Load Queries from File]
    LoadQueries --> InitMCP[Initialize MCP Servers]
    InitMCP --> InitAgent[Initialize Agent Loop]
    
    InitAgent --> LoopStart[For Each Test: 1 to N]
    LoopStart --> GetQuery[Get Query]
    GetQuery --> RunAgent[Run Agent Loop]
    
    RunAgent --> CheckResult{Success?}
    CheckResult -->|Yes| IncrementSuccess[Increment Success Count]
    CheckResult -->|No| IncrementFailure[Increment Failure Count]
    
    IncrementSuccess --> SleepTest[Sleep 1-3 seconds]
    IncrementFailure --> SleepTest
    
    SleepTest --> CheckBatch{Test % 10 == 0?}
    CheckBatch -->|Yes| SleepBatch[Sleep 3-10 seconds]
    CheckBatch -->|No| NextTest[Next Test]
    SleepBatch --> NextTest
    
    NextTest --> MoreTests{More Tests?}
    MoreTests -->|Yes| LoopStart
    MoreTests -->|No| GenerateStats[Generate Statistics]
    
    GenerateStats --> SaveStats[Save to Result_Stats.md]
    SaveStats --> End[End]
    
    style RunAgent fill:#e1f5ff
    style GenerateStats fill:#fff5e1
```

## Component Interaction

```mermaid
graph TB
    subgraph "Core Modules"
        HumanLoop[Human-in-Loop]
        ControlManager[Control Manager]
    end
    
    subgraph "Agent Layer"
        AgentLoop[Agent Loop]
        Perception[Perception]
        Decision[Decision]
    end
    
    subgraph "Execution Layer"
        Executor[Executor]
        MCP[Multi-MCP]
    end
    
    subgraph "Data Layer"
        CSVManager[CSV Manager]
        Memory[Memory Search]
        SessionLog[Session Log]
    end
    
    subgraph "Testing Layer"
        Simulator[Simulator]
        Statistics[Statistics]
    end
    
    AgentLoop --> HumanLoop
    AgentLoop --> ControlManager
    AgentLoop --> Perception
    AgentLoop --> Decision
    AgentLoop --> Executor
    AgentLoop --> CSVManager
    AgentLoop --> Memory
    AgentLoop --> SessionLog
    
    Executor --> MCP
    Executor --> HumanLoop
    Executor --> ControlManager
    
    Decision --> HumanLoop
    
    Simulator --> AgentLoop
    Statistics --> CSVManager
    
    style HumanLoop fill:#ffe1f5
    style ControlManager fill:#fff5e1
    style CSVManager fill:#e1ffe1
```

