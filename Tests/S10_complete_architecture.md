# Session 10 - Complete Architecture Diagrams

This document contains comprehensive architecture diagrams for the Multi-Agent System.
All diagrams are in Mermaid format and can be used directly in Mermaid Live Editor.

---

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph "User Layer"
        User[User/Query Provider]
    end
    
    subgraph "Agent System"
        AgentLoop[Agent Loop<br/>Orchestrator]
        
        subgraph "Core Modules"
            Perception[Perception Module<br/>Query Understanding]
            Decision[Decision Module<br/>Planning & Strategy]
            Executor[Action Executor<br/>Code Execution]
        end
        
        subgraph "Control & Management"
            ControlMgr[Control Manager<br/>MAX_STEPS/MAX_RETRIES]
            CSVManager[CSV Manager<br/>Performance Logging]
            UserPlanStorage[User Plan Storage<br/>Temporary Storage]
        end
        
        subgraph "Human-in-Loop"
            HILPlan[Plan Failure Handler]
            HILTool[Tool Failure Handler]
        end
    end
    
    subgraph "Tool Layer"
        MultiMCP[Multi-MCP Servers]
        MCP1[MCP Server 1<br/>Math Tools]
        MCP2[MCP Server 2<br/>Documents]
        MCP3[MCP Server 3<br/>Web Search]
    end
    
    subgraph "Memory Layer"
        MemorySearch[Memory Search<br/>Historical Queries]
        SessionLog[Session Log<br/>Current Session]
    end
    
    subgraph "Data Layer"
        CSVFiles[(CSV Files<br/>tool_performance.csv<br/>query_text.csv)]
        MemoryFiles[(Memory Files<br/>Session Logs)]
    end
    
    User -->|Query| AgentLoop
    AgentLoop --> Perception
    AgentLoop --> Decision
    AgentLoop --> Executor
    AgentLoop --> ControlMgr
    AgentLoop --> CSVManager
    AgentLoop --> UserPlanStorage
    
    Perception --> MemorySearch
    Decision --> MemorySearch
    Executor --> MultiMCP
    
    MultiMCP --> MCP1
    MultiMCP --> MCP2
    MultiMCP --> MCP3
    
    ControlMgr -->|Limit Check| HILPlan
    Executor -->|Tool Failure| HILTool
    HILPlan --> UserPlanStorage
    HILTool --> UserPlanStorage
    
    AgentLoop --> SessionLog
    CSVManager --> CSVFiles
    SessionLog --> MemoryFiles
    MemorySearch --> MemoryFiles
    
    style AgentLoop fill:#e1f5ff
    style Perception fill:#ffe6cc
    style Decision fill:#ffe6cc
    style Executor fill:#ffe6cc
    style ControlMgr fill:#fff5e1
    style CSVManager fill:#e1ffe1
    style HILPlan fill:#ffe1f5
    style HILTool fill:#ffe1f5
    style UserPlanStorage fill:#f0e1ff
```

---

## 2. Detailed Component Architecture

```mermaid
graph TB
    subgraph "Agent Loop (agent_loop2.py)"
        AL[AgentLoop Class]
        ALInit[__init__<br/>- Perception<br/>- Decision<br/>- MultiMCP<br/>- ControlManager<br/>- CSVManager]
        ALRun[run Method<br/>- Query Processing<br/>- Step Execution<br/>- CSV Logging]
        ALEval[evaluate_step Method<br/>- Goal Check<br/>- Plan Failure Handling]
        ALExec[execute_step Method<br/>- Code Execution<br/>- Perception Evaluation]
    end
    
    subgraph "Perception Module (perception.py)"
        Percept[Perception Class]
        PerceptBuild[build_perception_input<br/>- Memory Integration<br/>- Context Building]
        PerceptRun[run Method<br/>- LLM Call<br/>- ERORLL Output]
    end
    
    subgraph "Decision Module (decision.py)"
        Dec[Decision Class]
        DecRun[run Method<br/>- Initial Planning<br/>- Mid-Session Planning<br/>- Plan Generation]
    end
    
    subgraph "Action Executor (executor.py)"
        Exec[run_user_code Function]
        ExecRetry[Retry Logic<br/>- MAX_RETRIES Check<br/>- Error Handling]
        ExecSandbox[Code Sandbox<br/>- Safe Execution<br/>- Tool Access<br/>- completed_steps]
        ExecHIL[Human-in-Loop<br/>- Tool Failure Handling]
    end
    
    subgraph "Control Manager (control_manager.py)"
        CM[ControlManager Class]
        CMStep[check_step_limit<br/>- MAX_STEPS Enforcement]
        CMRetry[check_retry_limit<br/>- MAX_RETRIES Enforcement]
    end
    
    subgraph "CSV Manager (csv_manager.py)"
        CSV[CSVManager Class]
        CSVAdd[add_query<br/>- Query Registration]
        CSVLog[log_tool_performance<br/>- Performance Logging]
    end
    
    subgraph "User Plan Storage (user_plan_storage.py)"
        UPS[UserPlanStorage Class]
        UPSStore[store_user_plan<br/>- Temporary Storage]
        UPSGet[get_user_plan<br/>- Plan Retrieval]
        UPSClear[clear_user_plan<br/>- Memory Cleanup]
    end
    
    AL --> ALInit
    AL --> ALRun
    ALRun --> ALEval
    ALRun --> ALExec
    
    ALRun --> Percept
    ALRun --> Dec
    ALExec --> Exec
    
    ALEval --> CM
    ALExec --> CM
    ALRun --> CSV
    ALEval --> UPS
    
    Percept --> PerceptBuild
    Percept --> PerceptRun
    
    Dec --> DecRun
    
    Exec --> ExecRetry
    Exec --> ExecSandbox
    Exec --> ExecHIL
    
    CM --> CMStep
    CM --> CMRetry
    
    CSV --> CSVAdd
    CSV --> CSVLog
    
    UPS --> UPSStore
    UPS --> UPSGet
    UPS --> UPSClear
    
    style AL fill:#e1f5ff
    style Percept fill:#ffe6cc
    style Dec fill:#ffe6cc
    style Exec fill:#ffe6cc
    style CM fill:#fff5e1
    style CSV fill:#e1ffe1
    style UPS fill:#f0e1ff
```

---

## 3. Block-Level Architecture

```mermaid
graph LR
    subgraph "Input Block"
        Query[User Query]
        TestID[Test ID]
        QueryName[Query Name]
    end
    
    subgraph "Processing Block"
        subgraph "Query Processing"
            Parse[Query Parser<br/>- BHK Extraction<br/>- Currency Parsing]
            MemSearch[Memory Search<br/>- Historical Queries<br/>- Similar Patterns]
        end
        
        subgraph "Agent Processing"
            PerceptBlock[Perception Block<br/>- Entity Extraction<br/>- Goal Assessment<br/>- ERORLL Output]
            DecisionBlock[Decision Block<br/>- Plan Generation<br/>- Step Creation<br/>- Strategy Application]
            ExecBlock[Execution Block<br/>- Code Execution<br/>- Tool Invocation<br/>- Result Processing]
        end
        
        subgraph "Control Block"
            StepControl[Step Control<br/>- Step Limit Check<br/>- Step Indexing]
            RetryControl[Retry Control<br/>- Retry Count<br/>- Retry Logic]
            PlanControl[Plan Control<br/>- Plan Versioning<br/>- Plan Failure Detection]
        end
    end
    
    subgraph "Storage Block"
        SessionStorage[Session Storage<br/>- AgentSession<br/>- Plan Versions<br/>- Step History]
        UserPlanStorage[User Plan Storage<br/>- Temporary Plans<br/>- JSON Plans]
        CSVStorage[CSV Storage<br/>- Performance Logs<br/>- Query Registry]
        MemoryStorage[Memory Storage<br/>- Session Logs<br/>- Historical Data]
    end
    
    subgraph "Output Block"
        FinalAnswer[Final Answer]
        ResultStatus[Result Status<br/>- success/failure]
        CSVLog[CSV Log Entry]
        SessionLog[Session Log File]
    end
    
    Query --> Parse
    Query --> MemSearch
    Parse --> PerceptBlock
    MemSearch --> PerceptBlock
    
    PerceptBlock --> DecisionBlock
    DecisionBlock --> ExecBlock
    
    ExecBlock --> StepControl
    ExecBlock --> RetryControl
    DecisionBlock --> PlanControl
    
    StepControl --> SessionStorage
    RetryControl --> SessionStorage
    PlanControl --> UserPlanStorage
    
    SessionStorage --> CSVStorage
    UserPlanStorage --> CSVStorage
    SessionStorage --> MemoryStorage
    
    SessionStorage --> FinalAnswer
    SessionStorage --> ResultStatus
    CSVStorage --> CSVLog
    MemoryStorage --> SessionLog
    
    style PerceptBlock fill:#ffe6cc
    style DecisionBlock fill:#ffe6cc
    style ExecBlock fill:#ffe6cc
    style StepControl fill:#fff5e1
    style RetryControl fill:#fff5e1
    style PlanControl fill:#fff5e1
    style UserPlanStorage fill:#f0e1ff
```

---

## 4. Complete Execution Flow

```mermaid
flowchart TD
    Start([Start: User Query]) --> InitSession[Initialize AgentSession<br/>Generate Query_ID]
    
    InitSession --> CSVAdd[CSV: Add Query<br/>Register in query_text.csv]
    
    CSVAdd --> MemSearch[Memory Search<br/>Find Similar Queries]
    
    MemSearch --> Perception[Perception Module<br/>Run Initial Perception]
    
    Perception --> CheckGoal{Goal<br/>Achieved?}
    
    CheckGoal -->|Yes| Success1[Mark Success<br/>Set final_answer]
    CheckGoal -->|No| Decision[Decision Module<br/>Create Initial Plan]
    
    Decision --> PlanVersion[Add Plan Version<br/>Create Step 0]
    
    PlanVersion --> StepLoop{More Steps?}
    
    StepLoop -->|Yes| CheckStepLimit{Step Index<br/>>= MAX_STEPS?}
    
    CheckStepLimit -->|Yes| HILStepLimit[Human-in-Loop<br/>Step Limit Reached]
    CheckStepLimit -->|No| ExecuteStep[Execute Step]
    
    HILStepLimit --> CheckUserPlan{User Plan<br/>Stored?}
    CheckUserPlan -->|Yes| UseStoredPlan[Use Stored Plan<br/>Mark as FAILED]
    CheckUserPlan -->|No| AskUserPlan[Ask User for Plan<br/>Store if JSON]
    
    UseStoredPlan --> ConcludeStep[Create CONCLUDE Step]
    AskUserPlan --> StorePlan[Store User Plan<br/>Temporary Storage]
    StorePlan --> ConcludeStep
    
    ExecuteStep --> CheckRetry{Retry Count<br/>< MAX_RETRIES?}
    
    CheckRetry -->|Yes| ExecuteCode[Execute Code<br/>Access completed_steps]
    CheckRetry -->|No| HILToolFail[Human-in-Loop<br/>Tool Failure]
    
    ExecuteCode --> CheckToolResult{Tool<br/>Success?}
    
    CheckToolResult -->|Error| IncrementRetry[Increment Retry<br/>Retry Code]
    CheckToolResult -->|Success| StepPerception[Run Perception<br/>on Step Result]
    
    IncrementRetry --> CheckRetry
    
    HILToolFail --> GetUserResult[Get User Result<br/>Continue Execution]
    GetUserResult --> StepPerception
    
    StepPerception --> EvalStep[Evaluate Step<br/>Check Goal Achievement]
    
    EvalStep --> CheckGoalStep{Goal<br/>Achieved?}
    
    CheckGoalStep -->|Yes| Success2[Mark Success<br/>Set final_answer]
    CheckGoalStep -->|No| CheckLocalGoal{Local Goal<br/>Achieved?}
    
    CheckLocalGoal -->|Yes| CheckStepLimit
    CheckLocalGoal -->|No| PlanFailed[Plan Failed<br/>Trigger Human-in-Loop]
    
    PlanFailed --> CheckUserPlan2{User Plan<br/>Stored?}
    CheckUserPlan2 -->|Yes| UseStoredPlan2[Use Stored Plan<br/>Mark as FAILED]
    CheckUserPlan2 -->|No| AskUserPlan2[Ask User for Plan<br/>Store if JSON]
    
    UseStoredPlan2 --> NewPlan[Create New Plan<br/>Continue Execution]
    AskUserPlan2 --> StorePlan2[Store User Plan]
    StorePlan2 --> NewPlan
    
    NewPlan --> PlanVersion
    
    ConcludeStep --> StepLoop
    StepLoop -->|No| DetermineStatus[Determine Result Status<br/>Check User Plan/Goal]
    
    Success1 --> DetermineStatus
    Success2 --> DetermineStatus
    
    DetermineStatus --> CheckUserProvided{User Provided<br/>Answer?}
    
    CheckUserProvided -->|Yes| MarkFailed[Result Status = FAILURE<br/>User-provided answer]
    CheckUserProvided -->|No| CheckActualGoal{Actual Goal<br/>Achieved?}
    
    CheckActualGoal -->|Yes| MarkSuccess[Result Status = SUCCESS]
    CheckActualGoal -->|No| MarkFailed
    
    MarkFailed --> CSVLog[CSV: Log Performance<br/>Include User Plan in final_state]
    MarkSuccess --> CSVLog
    
    CSVLog --> Cleanup[Cleanup: Remove User Plan<br/>from Memory]
    
    Cleanup --> End([End: Return Session])
    
    style Perception fill:#ffe6cc
    style Decision fill:#ffe6cc
    style ExecuteStep fill:#ffe6cc
    style HILStepLimit fill:#ffe1f5
    style HILToolFail fill:#ffe1f5
    style CheckUserPlan fill:#f0e1ff
    style CheckUserPlan2 fill:#f0e1ff
    style StorePlan fill:#f0e1ff
    style StorePlan2 fill:#f0e1ff
    style MarkFailed fill:#ffcccc
    style MarkSuccess fill:#ccffcc
    style CSVLog fill:#e1ffe1
```

---

## 5. Data Flow Architecture

```mermaid
flowchart LR
    subgraph "Input Data"
        UserQuery[User Query Text]
        TestID[Test ID]
        QueryName[Query Name]
    end
    
    subgraph "Processing Data"
        ParsedQuery[Parsed Query<br/>- BHK Info<br/>- Currency Info]
        PerceptionData[Perception Data<br/>- Entities<br/>- Goal Status<br/>- ERORLL]
        DecisionData[Decision Data<br/>- Plan Text<br/>- Step Code<br/>- Step Type]
        ExecutionData[Execution Data<br/>- Tool Results<br/>- Retry Count<br/>- Error Messages]
    end
    
    subgraph "Storage Data"
        SessionData[Session Data<br/>- Plan Versions<br/>- Step History<br/>- State]
        UserPlanData[User Plan Data<br/>- JSON Plan<br/>- Final Answer<br/>- Goal Status]
        CSVData[CSV Data<br/>- Query_ID<br/>- Performance Metrics<br/>- Result Status]
    end
    
    subgraph "Output Data"
        FinalState[Final State<br/>- final_answer<br/>- result_status<br/>- confidence]
        CSVRow[CSV Row<br/>- All Fields<br/>- User Plan in final_state]
        SessionFile[Session File<br/>- JSON Format<br/>- Complete Session]
    end
    
    UserQuery --> ParsedQuery
    ParsedQuery --> PerceptionData
    PerceptionData --> DecisionData
    DecisionData --> ExecutionData
    
    ExecutionData --> SessionData
    UserPlanData --> SessionData
    SessionData --> CSVData
    
    SessionData --> FinalState
    CSVData --> CSVRow
    SessionData --> SessionFile
    
    style ParsedQuery fill:#e1f5ff
    style PerceptionData fill:#ffe6cc
    style DecisionData fill:#ffe6cc
    style ExecutionData fill:#ffe6cc
    style UserPlanData fill:#f0e1ff
    style FinalState fill:#ccffcc
    style CSVRow fill:#e1ffe1
```

---

## 6. Component Interaction Sequence

```mermaid
sequenceDiagram
    participant User
    participant AgentLoop
    participant Perception
    participant Decision
    participant Executor
    participant ControlManager
    participant CSVManager
    participant UserPlanStorage
    participant MultiMCP
    participant Memory
    
    User->>AgentLoop: Query + Test_ID
    AgentLoop->>CSVManager: add_query()
    CSVManager-->>AgentLoop: Query_ID
    
    AgentLoop->>Memory: search_memory()
    Memory-->>AgentLoop: Similar Queries
    
    AgentLoop->>Perception: run_perception()
    Perception-->>AgentLoop: ERORLL Result
    
    alt Goal Achieved
        AgentLoop->>CSVManager: log_tool_performance(SUCCESS)
        AgentLoop-->>User: Final Answer
    else Need Planning
        AgentLoop->>Decision: create_plan()
        Decision-->>AgentLoop: Plan + Steps
        
        loop For Each Step (up to MAX_STEPS)
            AgentLoop->>ControlManager: check_step_limit()
            ControlManager-->>AgentLoop: Limit Status
            
            alt Step Limit Reached
                AgentLoop->>UserPlanStorage: get_user_plan()
                alt Plan Stored
                    UserPlanStorage-->>AgentLoop: Stored Plan
                    AgentLoop->>AgentLoop: Mark as FAILED
                else No Plan
                    AgentLoop->>User: ask_user_for_plan()
                    User-->>AgentLoop: User Plan (JSON/Text)
                    AgentLoop->>UserPlanStorage: store_user_plan()
                    AgentLoop->>AgentLoop: Mark as FAILED
                end
            else Continue
                AgentLoop->>Executor: execute_step()
                
                loop Retry Loop (up to MAX_RETRIES)
                    Executor->>MultiMCP: call_tool()
                    MultiMCP-->>Executor: Tool Result
                    
                    alt Tool Success
                        Executor-->>AgentLoop: Success Result
                    else Tool Failure
                        Executor->>ControlManager: check_retry_limit()
                        ControlManager-->>Executor: Retry Status
                        
                        alt Retries Exhausted
                            Executor->>User: ask_user_for_tool_result()
                            User-->>Executor: User Result
                            Executor-->>AgentLoop: User Result
                        else Retry
                            Executor->>Executor: Retry Tool
                        end
                    end
                end
                
                AgentLoop->>Perception: evaluate_step_result()
                Perception-->>AgentLoop: Step Evaluation
                
                alt Goal Achieved
                    AgentLoop->>CSVManager: log_tool_performance(SUCCESS)
                    AgentLoop-->>User: Final Answer
                else Plan Failed
                    AgentLoop->>UserPlanStorage: get_user_plan()
                    alt Plan Stored
                        UserPlanStorage-->>AgentLoop: Stored Plan
                    else No Plan
                        AgentLoop->>User: ask_user_for_plan()
                        User-->>AgentLoop: User Plan
                        AgentLoop->>UserPlanStorage: store_user_plan()
                    end
                    AgentLoop->>Decision: replan()
                    Decision-->>AgentLoop: New Plan
                end
            end
        end
        
        AgentLoop->>CSVManager: log_tool_performance()
        CSVManager->>UserPlanStorage: Include in final_state
        AgentLoop->>UserPlanStorage: clear_user_plan()
        AgentLoop-->>User: Final Result
    end
```

---

## 7. State Management Flow

```mermaid
stateDiagram-v2
    [*] --> QueryReceived: User Query
    
    QueryReceived --> PerceptionRunning: Initialize Session
    PerceptionRunning --> GoalCheck: Perception Complete
    
    GoalCheck --> Success: Goal Achieved
    GoalCheck --> Planning: Goal Not Achieved
    
    Planning --> StepExecution: Plan Created
    StepExecution --> StepLimitCheck: Step Executed
    
    StepLimitCheck --> StepLimitReached: MAX_STEPS
    StepLimitCheck --> RetryCheck: Continue
    
    RetryCheck --> ToolExecution: Retries Available
    RetryCheck --> ToolFailure: MAX_RETRIES
    
    ToolExecution --> ToolSuccess: Tool Works
    ToolExecution --> ToolError: Tool Fails
    
    ToolError --> RetryCheck: Increment Retry
    ToolFailure --> HumanInLoopTool: Ask User
    
    StepLimitReached --> HumanInLoopPlan: Ask User
    HumanInLoopPlan --> UserPlanStored: Store Plan
    HumanInLoopTool --> ContinueExecution: User Result
    
    UserPlanStored --> UseStoredPlan: Next Lifeline
    UseStoredPlan --> MarkFailed: Mark as FAILED
    
    ToolSuccess --> StepEvaluation: Evaluate Result
    StepEvaluation --> GoalCheck: Check Goal
    
    ContinueExecution --> StepEvaluation
    
    MarkFailed --> CSVLogging: Log to CSV
    Success --> CSVLogging: Log to CSV
    
    CSVLogging --> Cleanup: Remove User Plan
    Cleanup --> [*]: Session Complete
```

---

## Usage Instructions

1. **Copy any diagram code** (the content between ```mermaid and ```)
2. **Go to Mermaid Live Editor**: https://mermaid.live/
3. **Paste the diagram code** into the editor
4. **View and edit** the diagram as needed
5. **Export** as PNG/SVG if needed

## Diagram Descriptions

1. **High-Level System Architecture**: Overview of all major components and their relationships
2. **Detailed Component Architecture**: Internal structure of each module with methods
3. **Block-Level Architecture**: Functional blocks and data flow between them
4. **Complete Execution Flow**: Step-by-step flow of query processing
5. **Data Flow Architecture**: How data moves through the system
6. **Component Interaction Sequence**: Sequence diagram showing component interactions
7. **State Management Flow**: State transitions during execution

All diagrams are compatible with Mermaid Live Editor and can be used directly.

