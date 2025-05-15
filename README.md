# Banking System Capstone Project

## 1. Project Overview

### 1.1 Purpose
The Banking System is a Python-based application designed to manage bank accounts and transactions, supporting operations such as account creation, deposits, withdrawals, transfers, interest calculations, transaction limits, and monthly statement generation. It adheres to Clean Architecture and SOLID principles, ensuring maintainability, scalability, and separation of concerns.

### 1.2 Scope
The system supports:
- Creating and managing Checking and Savings accounts.
- Performing transactions (deposits, withdrawals, transfers between owned accounts).
- Calculating interest based on account type.
- Enforcing transaction limits (daily/monthly).
- Generating monthly statements in PDF/CSV format.
- Sending automatic notifications (email/SMS) for transactions.
- Logging transactions for auditability.
- Enforcing business rules (e.g., minimum balance, withdrawal restrictions).

## 2. System Architecture

The system follows a layered architecture with four distinct layers: Domain, Application, Infrastructure, and Presentation. Each layer has a specific role and interacts through well-defined interfaces to maintain separation of concerns.

### 2.1 Domain Layer
- **Role**: Encapsulates core business logic, entities (`Account`, `Transaction`), and rules (e.g., minimum balance, interest calculations, transaction limits).
- **Key Features**: Manages account types, transaction operations (deposit, withdraw, transfer), interest strategies, and statement data preparation.
- **UML Diagram**:  
  ![DomainLayer.png](UML%20diagrams/week3/DomainLayer.png)

### 2.2 Application Layer
- **Role**: Orchestrates business operations by coordinating Domain entities and Infrastructure services, defining interfaces for persistence and external integrations.
- **Key Features**: Handles account creation, transactions, fund transfers, interest calculations, limit enforcement, and statement generation via services like `AccountCreationService`, `TransactionService`, `FundTransferService`, `InterestService`, and `StatementService`.
- **UML Diagram**:  
  ![ApplicationLayer.png](UML%20diagrams/week3/ApplicationLayer.png)

### 2.3 Infrastructure Layer
- **Role**: Provides concrete implementations for persistence (e.g., database), notifications (email/SMS), logging, and statement generation (PDF/CSV).
- **Key Features**: Implements repositories (`IAccountRepository`, `ITransactionRepository`), notification adapters, logging mechanisms, and statement builders using libraries like ReportLab (PDF) and CSV.
- **UML Diagram**:  
  ![InfrastructureLayer.png](UML%20diagrams/week3/InfrastructureLayer.png)

### 2.4 Presentation Layer
- **Role**: Exposes functionality via REST API endpoints, handling HTTP requests and responses.
- **Key Features**: Provides endpoints for account management, transactions, transfers, notifications, interest calculations, limit configurations, and statement generation.

## 3. Key Workflows

- **Account Creation**: Users create Checking or Savings accounts with an initial deposit, validated by business rules.
- **Deposits/Withdrawals**: Users deposit or withdraw funds, subject to balance and limit checks, with notifications and logging.
- **Fund Transfers**: Users transfer funds between owned accounts atomically, with notifications sent to both account owners.
- **Interest Calculation**: Periodic interest is applied based on account type, using configurable strategies.
- **Transaction Limits**: Daily/monthly limits are enforced to prevent overspending or fraud.
- **Monthly Statements**: Users receive PDF/CSV statements summarizing transactions, interest, and balances.
- **Notifications**: Email/SMS notifications are sent post-transaction, configurable via subscription endpoints.
- **Logging**: All operations are logged for auditability without cluttering core logic.

