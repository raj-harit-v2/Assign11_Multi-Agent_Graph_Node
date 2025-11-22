# Session 10 - High-Level Conceptual Architecture

## System Overview - Multi-Agent Coordination

```mermaid
graph TB
    subgraph "Human Layer"
        Human[Human User<br/>Query Provider & Supervisor]
    end
    
    subgraph "Intelligence Layer"
        Agent[Intelligent Agent<br/>Autonomous Decision Maker]
        Perception[Understanding<br/>What does the user want?]
        Planning[Strategy<br/>How to achieve the goal?]
    end
    
    subgraph "Execution Layer"
        Tools[Tool Ecosystem<br/>Code Execution & MCP Servers]
        Retry[Resilience<br/>Automatic Recovery]
    end
    
    subgraph "Oversight Layer"
        Limits[Execution Limits<br/>MAX_STEPS & MAX_RETRIES]
        HumanLoop[Human Intervention<br/>When AI Needs Help]
    end
    
    subgraph "Memory Layer"
        Context[Context Memory<br/>Past Experiences]
        Learning[Learning<br/>From History]
    end
    
    subgraph "Observability Layer"
        Logging[Comprehensive Logging<br/>CSV Performance Tracking]
        Analytics[Performance Analytics<br/>Success Rates & Insights]
    end
    
    Human -->|Query| Agent
    Agent --> Perception
    Perception --> Planning
    Planning --> Tools
    
    Tools -->|Failure| Retry
    Retry -->|Exhausted| HumanLoop
    HumanLoop -->|Guidance| Human
    Human -->|Result/Plan| Agent
    
    Agent -->|Check| Limits
    Limits -->|Limit Reached| HumanLoop
    
    Agent --> Context
    Context --> Learning
    Learning --> Agent
    
    Agent --> Logging
    Logging --> Analytics
    Analytics -->|Insights| Human
    
    Agent -->|Final Answer| Human
    
    style Agent fill:#4a90e2,color:#fff
    style HumanLoop fill:#e74c3c,color:#fff
    style Limits fill:#f39c12,color:#fff
    style Logging fill:#27ae60,color:#fff
    style Context fill:#9b59b6,color:#fff
```

## Core Principles - Autonomous with Human Oversight

```mermaid
mindmap
    root((Multi-Agent<br/>System))
        Autonomy
            Self-Directed Execution
            Automatic Retry Logic
            Context-Aware Planning
            Memory-Based Learning
        Human Oversight
            Tool Failure Recovery
            Plan Failure Intervention
            Execution Limit Enforcement
            Quality Assurance
        Resilience
            Retry Mechanisms
            Error Handling
            Graceful Degradation
            Human Fallback
        Observability
            Comprehensive Logging
            Performance Tracking
            Failure Analysis
            Success Metrics
        Intelligence
            Query Understanding
            Strategic Planning
            Context Retrieval
            Adaptive Execution
```

## Agent Lifecycle - From Query to Answer

```mermaid
stateDiagram-v2
    [*] --> QueryReceived: User Submits Query
    
    QueryReceived --> MemorySearch: Register Query
    MemorySearch --> Perception: Retrieve Context
    
    Perception --> GoalCheck: Analyze Intent
    
    GoalCheck --> Planning: Goal Not Achieved
    GoalCheck --> AnswerReady: Goal Already Achieved
    
    Planning --> StepExecution: Create Plan
    
    StepExecution --> StepLimitCheck: Execute Step
    
    StepLimitCheck --> HumanIntervention: Limit Reached
    StepLimitCheck --> StepEvaluation: Within Limits
    
    StepEvaluation --> GoalCheck: Evaluate Result
    
    StepExecution --> RetryCheck: Tool Execution
    
    RetryCheck --> RetryExecution: Retries Available
    RetryCheck --> HumanIntervention: Retries Exhausted
    
    RetryExecution --> RetryCheck: Retry Tool
    
    HumanIntervention --> Planning: User Provides Plan
    HumanIntervention --> AnswerReady: User Provides Result
    
    AnswerReady --> Logging: Prepare Final Answer
    Logging --> [*]: Return Answer
    
    note right of HumanIntervention
        Human-in-Loop
        Tool & Plan Recovery
    end note
    
    note right of StepLimitCheck
        MAX_STEPS = 3
        MAX_RETRIES = 3
    end note
```

## Information Flow - Data Through the System

```mermaid
flowchart TD
    subgraph "Input"
        I1[User Query<br/>Natural Language]
    end
    
    subgraph "Understanding"
        U1[Perception<br/>Intent Extraction]
        U2[Memory Search<br/>Context Retrieval]
        U3[Goal Analysis<br/>Achievement Check]
    end
    
    subgraph "Planning"
        P1[Decision Module<br/>Strategy Selection]
        P2[Plan Generation<br/>Step Sequence]
        P3[Plan Validation<br/>Feasibility Check]
    end
    
    subgraph "Execution"
        E1[Tool Selection<br/>MCP Server Choice]
        E2[Code Execution<br/>Python Runtime]
        E3[Result Capture<br/>Output Collection]
    end
    
    subgraph "Evaluation"
        V1[Step Assessment<br/>Helpfulness Check]
        V2[Goal Progress<br/>Achievement Status]
        V3[Plan Adjustment<br/>Replanning Decision]
    end
    
    subgraph "Recovery"
        R1[Retry Logic<br/>Automatic Retry]
        R2[Human Intervention<br/>Tool Recovery]
        R3[Plan Modification<br/>Human Guidance]
    end
    
    subgraph "Output"
        O1[Final Answer<br/>User Response]
        O2[Performance Log<br/>CSV Records]
        O3[Statistics<br/>Analytics Report]
    end
    
    I1 --> U1
    I1 --> U2
    U2 --> U1
    U1 --> U3
    
    U3 --> P1
    P1 --> P2
    P2 --> P3
    
    P3 --> E1
    E1 --> E2
    E2 --> E3
    
    E3 --> V1
    V1 --> V2
    V2 --> V3
    
    V3 -->|Continue| E1
    V3 -->|Retry Needed| R1
    V3 -->|Recovery Needed| R2
    V3 -->|Plan Change| R3
    
    R1 --> E2
    R2 --> E3
    R3 --> P2
    
    V2 -->|Goal Achieved| O1
    V2 -->|Complete| O2
    O2 --> O3
    
    style U1 fill:#3498db,color:#fff
    style P1 fill:#9b59b6,color:#fff
    style E2 fill:#e74c3c,color:#fff
    style R2 fill:#e74c3c,color:#fff
    style R3 fill:#e74c3c,color:#fff
    style O1 fill:#27ae60,color:#fff
```

## Human-in-Loop Integration Points

```mermaid
graph LR
    subgraph "Autonomous Operation"
        A1[Agent Executes]
        A2[Tools Run]
        A3[Plans Execute]
    end
    
    subgraph "Failure Detection"
        F1[Tool Failure]
        F2[Plan Failure]
        F3[Limit Reached]
    end
    
    subgraph "Human Intervention"
        H1[Tool Recovery<br/>User Provides Result]
        H2[Plan Modification<br/>User Provides Plan]
        H3[Execution Control<br/>User Approves/Modifies]
    end
    
    subgraph "Recovery"
        R1[Continue with<br/>User Input]
        R2[Resume Execution]
    end
    
    A1 --> A2
    A2 --> A3
    A3 --> A1
    
    A2 -->|Error| F1
    A3 -->|Unhelpful| F2
    A1 -->|Max Steps| F3
    
    F1 --> H1
    F2 --> H2
    F3 --> H3
    
    H1 --> R1
    H2 --> R1
    H3 --> R1
    
    R1 --> R2
    R2 --> A1
    
    style H1 fill:#e74c3c,color:#fff
    style H2 fill:#e74c3c,color:#fff
    style H3 fill:#e74c3c,color:#fff
    style R1 fill:#27ae60,color:#fff
```

## Execution Limits - Safety and Control

```mermaid
graph TD
    subgraph "Limit Configuration"
        LC1[MAX_STEPS = 3<br/>Maximum Plan Steps]
        LC2[MAX_RETRIES = 3<br/>Maximum Tool Retries]
    end
    
    subgraph "Enforcement Points"
        EP1[Before Each Step<br/>Check Step Count]
        EP2[After Each Tool Call<br/>Check Retry Count]
    end
    
    subgraph "Limit Actions"
        LA1[Allow Execution<br/>Within Limits]
        LA2[Trigger Human-in-Loop<br/>Limit Reached]
    end
    
    subgraph "Human Response"
        HR1[Provide Plan<br/>Continue Execution]
        HR2[Provide Result<br/>Skip Tool]
        HR3[Conclude Session<br/>End Execution]
    end
    
    LC1 --> EP1
    LC2 --> EP2
    
    EP1 -->|Count < MAX| LA1
    EP1 -->|Count >= MAX| LA2
    EP2 -->|Count < MAX| LA1
    EP2 -->|Count >= MAX| LA2
    
    LA2 --> HR1
    LA2 --> HR2
    LA2 --> HR3
    
    HR1 --> LA1
    HR2 --> LA1
    HR3 --> End[End Session]
    
    style LC1 fill:#f39c12,color:#fff
    style LC2 fill:#f39c12,color:#fff
    style LA2 fill:#e74c3c,color:#fff
```

## Memory and Learning - Context-Aware Intelligence

```mermaid
graph TB
    subgraph "Memory Sources"
        MS1[Session Logs<br/>Past Executions]
        MS2[Query History<br/>Similar Queries]
        MS3[Tool Results<br/>Previous Outcomes]
    end
    
    subgraph "Memory Search"
        MS[Memory Search Module<br/>Fuzzy Matching]
        Context[Context Retrieval<br/>Relevant History]
    end
    
    subgraph "Learning Application"
        LA1[Query Understanding<br/>Use Similar Contexts]
        LA2[Planning<br/>Learn from Past Plans]
        LA3[Tool Selection<br/>Use Successful Tools]
    end
    
    subgraph "Memory Storage"
        Store[Session Log<br/>Save Current Execution]
        Update[Update Memory<br/>Add New Experiences]
    end
    
    MS1 --> MS
    MS2 --> MS
    MS3 --> MS
    
    MS --> Context
    
    Context --> LA1
    Context --> LA2
    Context --> LA3
    
    LA1 --> Store
    LA2 --> Store
    LA3 --> Store
    
    Store --> Update
    Update --> MS1
    
    style MS fill:#9b59b6,color:#fff
    style Context fill:#3498db,color:#fff
    style Store fill:#27ae60,color:#fff
```

## Observability and Analytics - System Intelligence

```mermaid
graph LR
    subgraph "Data Collection"
        DC1[Query Registration<br/>query_text.csv]
        DC2[Performance Logging<br/>tool_performance.csv]
        DC3[Execution Metrics<br/>Steps, Retries, Time]
    end
    
    subgraph "Data Storage"
        DS1[CSV Files<br/>Structured Data]
        DS2[Session Logs<br/>JSON State]
    end
    
    subgraph "Analytics"
        A1[Success Rate<br/>Percentage]
        A2[Tool Performance<br/>Success by Tool]
        A3[Failure Analysis<br/>Error Patterns]
        A4[Query Analysis<br/>Query Type Performance]
    end
    
    subgraph "Reporting"
        R1[Statistics Report<br/>Result_Stats.md]
        R2[Console Output<br/>Real-time Feedback]
    end
    
    DC1 --> DS1
    DC2 --> DS1
    DC3 --> DS1
    DC3 --> DS2
    
    DS1 --> A1
    DS1 --> A2
    DS1 --> A3
    DS1 --> A4
    
    A1 --> R1
    A2 --> R1
    A3 --> R1
    A4 --> R1
    
    R1 --> R2
    
    style DS1 fill:#27ae60,color:#fff
    style A1 fill:#3498db,color:#fff
    style R1 fill:#f39c12,color:#fff
```

## System Resilience - Failure Recovery Strategy

```mermaid
graph TD
    Start([System Operation]) --> Normal[Normal Execution]
    
    Normal --> Failure{Failure<br/>Detected?}
    
    Failure -->|No| Continue[Continue Execution]
    Continue --> Normal
    
    Failure -->|Yes| Classify[Classify Failure Type]
    
    Classify --> ToolFailure[Tool Execution Failure]
    Classify --> PlanFailure[Plan Execution Failure]
    Classify --> LimitFailure[Execution Limit Reached]
    
    ToolFailure --> Retry[Automatic Retry<br/>Up to MAX_RETRIES]
    Retry --> RetrySuccess{Retry<br/>Successful?}
    
    RetrySuccess -->|Yes| Continue
    RetrySuccess -->|No| ToolHIL[Human-in-Loop<br/>Tool Recovery]
    
    PlanFailure --> PlanHIL[Human-in-Loop<br/>Plan Modification]
    LimitFailure --> LimitHIL[Human-in-Loop<br/>Execution Control]
    
    ToolHIL --> UserTool[User Provides<br/>Tool Result]
    PlanHIL --> UserPlan[User Provides<br/>New Plan]
    LimitHIL --> UserControl[User Provides<br/>Control Decision]
    
    UserTool --> Continue
    UserPlan --> Continue
    UserControl --> Continue
    
    Continue --> Log[Log Recovery Action]
    Log --> Normal
    
    style ToolHIL fill:#e74c3c,color:#fff
    style PlanHIL fill:#e74c3c,color:#fff
    style LimitHIL fill:#e74c3c,color:#fff
    style Continue fill:#27ae60,color:#fff
```

## Multi-Agent Coordination Model

```mermaid
graph TB
    subgraph "Agent Components"
        A1[Perception Agent<br/>Understanding Specialist]
        A2[Decision Agent<br/>Planning Specialist]
        A3[Execution Agent<br/>Action Specialist]
        A4[Evaluation Agent<br/>Quality Specialist]
    end
    
    subgraph "Coordination"
        C1[Agent Loop<br/>Orchestrator]
        C2[Control Manager<br/>Resource Controller]
        C3[Human-in-Loop<br/>Supervisor]
    end
    
    subgraph "Shared Resources"
        R1[Memory Pool<br/>Shared Context]
        R2[Tool Pool<br/>Shared Tools]
        R3[State Pool<br/>Shared Session State]
    end
    
    C1 --> A1
    C1 --> A2
    C1 --> A3
    C1 --> A4
    
    A1 --> R1
    A2 --> R1
    A3 --> R2
    A4 --> R3
    
    C2 --> C1
    C3 --> C1
    
    A1 -->|Query Understanding| A2
    A2 -->|Plan| A3
    A3 -->|Results| A4
    A4 -->|Feedback| A2
    
    A4 -->|Needs Help| C3
    A3 -->|Needs Help| C3
    
    style C1 fill:#4a90e2,color:#fff
    style C3 fill:#e74c3c,color:#fff
    style C2 fill:#f39c12,color:#fff
```

