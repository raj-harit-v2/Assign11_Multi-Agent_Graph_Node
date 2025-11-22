# Session 10 - Detailed Architecture and Flow Diagrams

## Complete System Architecture

```mermaid
graph TB
    subgraph "Input Layer"
        User[User Query]
        Simulator[Automated Simulator]
        TestFile[Test Files]
    end
    
    subgraph "Core Agent System"
        AgentLoop[Agent Loop<br/>Main Orchestrator]
        ControlManager[Control Manager<br/>MAX_STEPS/MAX_RETRIES]
        HumanLoop[Human-in-Loop<br/>Tool & Plan Recovery]
    end
    
    subgraph "AI Processing Layer"
        Perception[Perception Module<br/>Query Understanding]
        Decision[Decision Module<br/>Planning & Strategy]
        MemorySearch[Memory Search<br/>Context Retrieval]
    end
    
    subgraph "Execution Layer"
        Executor[Action Executor<br/>Code Execution]
        MCP[Multi-MCP Servers<br/>Tool Providers]
        RetryLogic[Retry Logic<br/>MAX_RETRIES]
    end
    
    subgraph "Data Management Layer"
        CSVManager[CSV Manager<br/>Query & Performance Logging]
        SessionLog[Session Log<br/>State Persistence]
        QueryCSV[query_text.csv<br/>Query Master Table]
        PerfCSV[tool_performance.csv<br/>Performance Metrics]
    end
    
    subgraph "Output Layer"
        Statistics[Statistics Generator<br/>Performance Analysis]
        StatsMD[Result_Stats.md<br/>Analysis Report]
        FinalAnswer[Final Answer<br/>To User]
    end
    
    User --> AgentLoop
    Simulator --> AgentLoop
    TestFile --> Simulator
    
    AgentLoop --> ControlManager
    AgentLoop --> Perception
    AgentLoop --> Decision
    AgentLoop --> Executor
    AgentLoop --> CSVManager
    AgentLoop --> MemorySearch
    AgentLoop --> SessionLog
    
    Perception --> MemorySearch
    Decision --> MemorySearch
    
    Executor --> MCP
    Executor --> RetryLogic
    Executor --> HumanLoop
    RetryLogic --> HumanLoop
    
    ControlManager --> HumanLoop
    
    CSVManager --> QueryCSV
    CSVManager --> PerfCSV
    
    SessionLog --> MemorySearch
    
    PerfCSV --> Statistics
    Statistics --> StatsMD
    
    AgentLoop --> FinalAnswer
    
    style AgentLoop fill:#4a90e2,color:#fff
    style HumanLoop fill:#e74c3c,color:#fff
    style ControlManager fill:#f39c12,color:#fff
    style CSVManager fill:#27ae60,color:#fff
    style Executor fill:#9b59b6,color:#fff
    style Perception fill:#3498db,color:#fff
    style Decision fill:#3498db,color:#fff
```

## Complete Agent Loop Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant AgentLoop
    participant CSVManager
    participant MemorySearch
    participant Perception
    participant Decision
    participant ControlManager
    participant Executor
    participant MCP
    participant HumanLoop
    participant SessionLog
    
    User->>AgentLoop: Submit Query
    AgentLoop->>CSVManager: Register Query (Get Query_Id)
    CSVManager-->>AgentLoop: Query_Id (Bigint)
    
    AgentLoop->>MemorySearch: Search Relevant Memory
    MemorySearch-->>AgentLoop: Memory Context
    
    AgentLoop->>Perception: Analyze Query + Memory
    Perception-->>AgentLoop: Perception Result
    
    alt Goal Already Achieved
        AgentLoop->>CSVManager: Log Success (No Steps)
        AgentLoop-->>User: Return Final Answer
    else Need Planning
        AgentLoop->>Decision: Create Initial Plan
        Decision-->>AgentLoop: Plan with Steps
        
        loop For Each Step (Up to MAX_STEPS)
            AgentLoop->>ControlManager: Check Step Limit
            ControlManager-->>AgentLoop: Limit Status
            
            alt Step Limit Reached
                AgentLoop->>Decision: Generate Suggested Plan
                Decision-->>AgentLoop: Suggested Plan
                AgentLoop->>HumanLoop: Request Plan Modification
                HumanLoop->>User: Present Context + Suggestion
                User-->>HumanLoop: Provide New Plan
                HumanLoop-->>AgentLoop: User Plan
                AgentLoop->>AgentLoop: Create CONCLUDE Step
            end
            
            AgentLoop->>Executor: Execute Step
            Executor->>MCP: Call Tool
            
            loop Retry Loop (Up to MAX_RETRIES)
                alt Tool Success
                    MCP-->>Executor: Success Result
                else Tool Failure
                    MCP-->>Executor: Error
                    Executor->>Executor: Increment Retry Count
                    alt Retries Exhausted
                        Executor->>HumanLoop: Request Tool Result
                        HumanLoop->>User: Present Error Context
                        User-->>HumanLoop: Provide Result
                        HumanLoop-->>Executor: User Result
                    end
                end
            end
            
            Executor-->>AgentLoop: Execution Result
            
            AgentLoop->>SessionLog: Update Session State
            AgentLoop->>Perception: Evaluate Step Result
            Perception-->>AgentLoop: Perception Snapshot
            
            alt Goal Achieved
                AgentLoop->>CSVManager: Log Success
                AgentLoop-->>User: Return Final Answer
            else Continue
                AgentLoop->>Decision: Plan Next Step
                Decision-->>AgentLoop: Next Step Plan
            end
        end
    end
    
    AgentLoop->>CSVManager: Log Final Performance
    CSVManager->>PerfCSV: Write Performance Data
```

## Tool Execution with Retry and Human-in-Loop

```mermaid
flowchart TD
    Start([Start Tool Execution]) --> Init[Initialize Retry Count = 0]
    Init --> Execute[Execute Tool via MCP]
    
    Execute --> CheckSuccess{Execution<br/>Successful?}
    
    CheckSuccess -->|Yes| LogSuccess[Log Success to CSV]
    LogSuccess --> ReturnSuccess[Return Success Result]
    ReturnSuccess --> End([End])
    
    CheckSuccess -->|No| CatchError[Capture Error]
    CatchError --> IncrementRetry[Increment Retry Count]
    IncrementRetry --> CheckRetryLimit{Retry Count<br/>< MAX_RETRIES?}
    
    CheckRetryLimit -->|Yes| Sleep[Sleep 1 Second]
    Sleep --> Execute
    
    CheckRetryLimit -->|No| AllRetriesFailed[All Retries Exhausted]
    AllRetriesFailed --> BuildContext[Build Error Context:<br/>- Tool Name<br/>- Error Message<br/>- Step Description<br/>- Query]
    
    BuildContext --> TriggerHIL[Trigger Human-in-Loop]
    TriggerHIL --> PresentError[Present to User:<br/>- Tool Name<br/>- Error Details<br/>- Expected Result]
    
    PresentError --> UserInput{User Provides<br/>Result?}
    
    UserInput -->|Yes| GetUserResult[Get User Result]
    GetUserResult --> MarkHumanProvided[Mark as Human-Provided]
    MarkHumanProvided --> LogWithHIL[Log to CSV with<br/>human_provided=True]
    LogWithHIL --> ReturnUserResult[Return User Result as Success]
    ReturnUserResult --> End
    
    UserInput -->|No| ReturnError[Return Error Result]
    ReturnError --> End
    
    style AllRetriesFailed fill:#e74c3c,color:#fff
    style TriggerHIL fill:#e74c3c,color:#fff
    style ReturnSuccess fill:#27ae60,color:#fff
    style ReturnUserResult fill:#27ae60,color:#fff
```

## Plan Failure and Human-in-Loop Flow

```mermaid
flowchart TD
    Start([Agent Loop Running]) --> ExecuteStep[Execute Current Step]
    ExecuteStep --> EvaluateStep[Evaluate Step Result]
    
    EvaluateStep --> CheckGoal{Goal<br/>Achieved?}
    
    CheckGoal -->|Yes| LogSuccess[Log Success to CSV]
    LogSuccess --> ReturnAnswer[Return Final Answer]
    ReturnAnswer --> End([End])
    
    CheckGoal -->|No| CheckUnhelpful{Step<br/>Unhelpful?}
    
    CheckUnhelpful -->|No| Continue[Continue to Next Step]
    Continue --> CheckStepLimit{Step Index<br/>< MAX_STEPS?}
    
    CheckStepLimit -->|Yes| ExecuteStep
    CheckStepLimit -->|No| PlanLimitReached[Step Limit Reached]
    
    CheckUnhelpful -->|Yes| PlanFailed[Plan Failed - Step Unhelpful]
    
    PlanLimitReached --> BuildContext[Build Failure Context:<br/>- Reason<br/>- Current Plan<br/>- Step Count<br/>- Query]
    PlanFailed --> BuildContext
    
    BuildContext --> GetSuggestion[Get Suggested Plan from Decision]
    GetSuggestion --> PresentToUser[Present to User:<br/>- Failure Reason<br/>- Current Plan<br/>- Suggested Plan]
    
    PresentToUser --> UserChoice{User Choice}
    
    UserChoice -->|Accept Suggested| UseSuggested[Use Suggested Plan]
    UserChoice -->|Modify| GetModified[Get Modified Plan from User]
    UserChoice -->|Custom| GetCustom[Get Custom Plan from User]
    UserChoice -->|No Input| UseConclude[Use Default: Conclude]
    
    UseSuggested --> CreateStep[Create CONCLUDE Step]
    GetModified --> CreateStep
    GetCustom --> CreateStep
    UseConclude --> CreateStep
    
    CreateStep --> UpdateSession[Update Session with New Plan]
    UpdateSession --> MarkComplete[Mark Session Complete]
    MarkComplete --> LogToCSV[Log to CSV with Final State]
    LogToCSV --> End
    
    style PlanLimitReached fill:#e74c3c,color:#fff
    style PlanFailed fill:#e74c3c,color:#fff
    style PresentToUser fill:#e74c3c,color:#fff
    style MarkComplete fill:#27ae60,color:#fff
```

## Data Flow and CSV Logging

```mermaid
flowchart LR
    subgraph "Input"
        Query[User Query<br/>Query Text]
        TestId[Test ID<br/>Sequential Number]
    end
    
    subgraph "CSV Manager"
        Register[Register Query]
        GenerateId[Generate Query_Id<br/>Bigint Sequential]
        LogPerf[Log Performance]
    end
    
    subgraph "CSV Files"
        QueryCSV[query_text.csv<br/>- Query_Id<br/>- Query_Name<br/>- Query_Text<br/>- Create_Datetime<br/>- Update_Datetime<br/>- Active_Flag]
        PerfCSV[tool_performance.csv<br/>- Test_Id<br/>- Query_Id<br/>- Query_Name<br/>- Query_Text<br/>- Query_Answer<br/>- Plan_Used<br/>- Result_Status<br/>- Start_Datetime<br/>- End_Datetime<br/>- Elapsed_Time<br/>- Plan_Step_Count<br/>- Tool_Name<br/>- Retry_Count<br/>- Error_Message<br/>- Final_State]
    end
    
    subgraph "Statistics"
        StatsGen[Statistics Generator]
        StatsMD[Result_Stats.md<br/>- Success Rate<br/>- Tool Performance<br/>- Failure Analysis<br/>- Query Analysis]
    end
    
    Query --> Register
    TestId --> Register
    Register --> GenerateId
    GenerateId --> QueryCSV
    
    Query --> LogPerf
    TestId --> LogPerf
    GenerateId --> LogPerf
    LogPerf --> PerfCSV
    
    PerfCSV --> StatsGen
    StatsGen --> StatsMD
    
    style QueryCSV fill:#27ae60,color:#fff
    style PerfCSV fill:#27ae60,color:#fff
    style StatsMD fill:#f39c12,color:#fff
```

## Simulator and Batch Testing Flow

```mermaid
flowchart TD
    Start([Start Simulator]) --> LoadConfig[Load Configuration:<br/>- Test Count<br/>- Query Types<br/>- Sleep Intervals]
    
    LoadConfig --> LoadQueries[Load Queries from File<br/>or Generate Test Queries]
    
    LoadQueries --> InitMCP[Initialize MCP Servers]
    InitMCP --> InitAgent[Initialize Agent Loop]
    
    InitAgent --> InitCSV[Initialize CSV Files:<br/>- query_text.csv<br/>- tool_performance.csv]
    
    InitCSV --> LoopStart[For Each Test: 1 to N]
    
    LoopStart --> GetQuery[Get Next Query<br/>with Query Type]
    
    GetQuery --> RunAgent[Run Agent Loop:<br/>- test_id<br/>- query<br/>- query_name]
    
    RunAgent --> CheckResult{Execution<br/>Result?}
    
    CheckResult -->|Success| IncrementSuccess[Increment Success Count]
    CheckResult -->|Failure| IncrementFailure[Increment Failure Count]
    CheckResult -->|Error| IncrementError[Increment Error Count]
    
    IncrementSuccess --> SleepTest[Sleep 1-3 seconds<br/>Random Interval]
    IncrementFailure --> SleepTest
    IncrementError --> SleepTest
    
    SleepTest --> CheckBatch{Test Number<br/>% 10 == 0?}
    
    CheckBatch -->|Yes| SleepBatch[Sleep 3-10 seconds<br/>Longer Interval]
    CheckBatch -->|No| NextTest[Next Test]
    
    SleepBatch --> NextTest
    
    NextTest --> MoreTests{More Tests<br/>Remaining?}
    
    MoreTests -->|Yes| LoopStart
    MoreTests -->|No| GenerateStats[Generate Statistics]
    
    GenerateStats --> ReadCSV[Read tool_performance.csv]
    ReadCSV --> CalculateMetrics[Calculate Metrics:<br/>- Success Rate<br/>- Average Steps<br/>- Tool Performance<br/>- Failure Reasons]
    
    CalculateMetrics --> SaveStats[Save to Result_Stats.md]
    SaveStats --> PrintSummary[Print Summary to Console]
    PrintSummary --> End([End])
    
    style RunAgent fill:#4a90e2,color:#fff
    style GenerateStats fill:#f39c12,color:#fff
    style SaveStats fill:#27ae60,color:#fff
```

## Component Interaction Matrix

```mermaid
graph TB
    subgraph "Control & Coordination"
        CM[Control Manager<br/>MAX_STEPS: 3<br/>MAX_RETRIES: 3]
        HIL[Human-in-Loop<br/>Tool & Plan Recovery]
    end
    
    subgraph "Agent Core"
        AL[Agent Loop<br/>Main Orchestrator]
        PER[Perception<br/>Query Understanding]
        DEC[Decision<br/>Planning]
    end
    
    subgraph "Execution"
        EXE[Executor<br/>Code Execution]
        MCP[Multi-MCP<br/>Tool Servers]
    end
    
    subgraph "Data & Memory"
        CSV[CSV Manager<br/>Logging]
        MEM[Memory Search<br/>Context]
        LOG[Session Log<br/>State]
    end
    
    AL <--> CM
    AL <--> HIL
    AL --> PER
    AL --> DEC
    AL --> EXE
    AL --> CSV
    AL --> MEM
    AL --> LOG
    
    PER --> MEM
    DEC --> MEM
    
    EXE <--> CM
    EXE --> MCP
    EXE --> HIL
    
    CSV --> CSVFiles[(CSV Files)]
    LOG --> MEM
    
    style AL fill:#4a90e2,color:#fff
    style HIL fill:#e74c3c,color:#fff
    style CM fill:#f39c12,color:#fff
    style CSV fill:#27ae60,color:#fff
```

## Execution Limits Enforcement

```mermaid
flowchart TD
    Start([Agent Execution Starts]) --> InitStepCount[Initialize Step Count = 0]
    
    InitStepCount --> LoopStart[Start Step Loop]
    
    LoopStart --> IncrementStep[Increment Step Count]
    IncrementStep --> CheckStepLimit{Step Count<br/>>= MAX_STEPS?}
    
    CheckStepLimit -->|No| ExecuteStep[Execute Step]
    CheckStepLimit -->|Yes| TriggerHIL[Trigger Human-in-Loop<br/>for Plan Modification]
    
    ExecuteStep --> InitRetryCount[Initialize Retry Count = 0]
    InitRetryCount --> ExecuteTool[Execute Tool]
    
    ExecuteTool --> CheckToolSuccess{Tool<br/>Success?}
    
    CheckToolSuccess -->|Yes| StepComplete[Step Complete]
    CheckToolSuccess -->|No| IncrementRetry[Increment Retry Count]
    
    IncrementRetry --> CheckRetryLimit{Retry Count<br/>>= MAX_RETRIES?}
    
    CheckRetryLimit -->|No| RetryTool[Retry Tool<br/>Sleep 1s]
    RetryTool --> ExecuteTool
    
    CheckRetryLimit -->|Yes| TriggerToolHIL[Trigger Human-in-Loop<br/>for Tool Result]
    
    TriggerToolHIL --> GetUserResult[Get User Result]
    GetUserResult --> StepComplete
    
    StepComplete --> EvaluateStep[Evaluate Step Result]
    
    EvaluateStep --> CheckGoal{Goal<br/>Achieved?}
    
    CheckGoal -->|Yes| EndExecution[End Execution]
    CheckGoal -->|No| CheckUnhelpful{Step<br/>Unhelpful?}
    
    CheckUnhelpful -->|No| LoopStart
    CheckUnhelpful -->|Yes| TriggerPlanHIL[Trigger Human-in-Loop<br/>for Plan Failure]
    
    TriggerHIL --> GetUserPlan[Get User Plan]
    TriggerPlanHIL --> GetUserPlan
    
    GetUserPlan --> CreateConclude[Create CONCLUDE Step]
    CreateConclude --> EndExecution
    
    EndExecution --> LogResults[Log Results to CSV]
    LogResults --> End([End])
    
    style TriggerHIL fill:#e74c3c,color:#fff
    style TriggerToolHIL fill:#e74c3c,color:#fff
    style TriggerPlanHIL fill:#e74c3c,color:#fff
    style EndExecution fill:#27ae60,color:#fff
```

