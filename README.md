
---

# Banking System Documentation

## 1. Project Overview

### 1.1 Purpose  
The Banking System is designed to manage bank accounts and transactions, supporting operations like deposits, withdrawals, and account creation. It ensures robust business rule validation (e.g., minimum balance checks) and persistence of data, following a clean, layered architecture for maintainability and scalability.

### 1.2 Scope  
The system supports:  
- Creating and managing accounts (Checking and Savings).  
- Performing transactions (deposits and withdrawals).  
- Enforcing business rules (e.g., minimum balance for Savings accounts, withdrawal restrictions).  
- Persisting account and transaction data via repositories.

---

## 2. System Architecture

The system follows a layered architecture with four distinct layers: Domain, Application, Infrastructure, and Presentation. Each layer has a specific role and interacts with others through well-defined interfaces.

### 2.1 Layers and Their Roles

#### 2.1.1 Domain Layer  
- **Role**: Contains the core business logic, entities, and rules, focusing solely on the business domain without defining persistence interfaces.  
- **Components**:  
  - **Entities**:  
    - `Account`: Represents a bank account with attributes like `account_id`, `account_type`, `balance`, `status`, and `creation_date`.  
      - Methods: `deposit(amount: float)`, `withdraw(amount: float)`, `update_balance(amount: float)`, `get_balance()`.  
    - `Transaction`: Represents a transaction with attributes like `trans_id`, `trans_type`, `amount`, `timestamp`, and `account_id`.  
      - Methods: `get_trans_id()`, `get_amount()`, `get_transaction_type()`.  
    - `CheckingAccount` and `SavingsAccount`: Subclasses of `Account` with specific behaviors (e.g., `SavingsAccount` enforces a `minimum_balance`).  
  - **Business Rules**:  
    - `BusinessRuleService`: Validates operations.  
      - `check_withdraw_allowed(account: Account, amount: float)`: Ensures withdrawals are allowed based on account type and balance.  
      - `validate_deposit_amount(amount: float)`: Ensures deposits are valid (e.g., positive amounts).  
  - **Enumerations**:  
    - `AccountType`: `CHECKING`, `SAVINGS`.  
    - `AccountStatus`: `ACTIVE`, `CLOSED`.  
    - `TransactionType`: `DEPOSIT`, `WITHDRAW`.  
- **Interaction**:  
  - Encapsulates business logic and state.  
  - Used by the Application Layer to perform operations.  
  - `Account` generates `Transaction` objects during deposits/withdrawals.

![domainLayerUML.png](UML%20diagrams/domainLayerUML.png)

#### 2.1.2 Application Layer  
- **Role**: Orchestrates business operations by coordinating between the Domain and Infrastructure Layers, defining interfaces for persistence that the Infrastructure Layer implements.  
- **Components**:  
  - `TransactionService`: Manages deposit and withdrawal operations.  
    - `deposit(account_id: str, amount: float)`: Fetches the account, calls `deposit()` on the `Account` domain object, saves the transaction, and updates the account.  
    - `withdraw(account_id: str, amount: float)`: Fetches the account, calls `withdraw()` on the `Account` domain object, saves the transaction, and updates the account.  
  - `AccountCreationService`: Handles account creation.  
    - `create_account(account_type: AccountType, initial_deposit: float)`: Creates a new account and persists it.  
  - **Interfaces Defined**:  
    - `IAccountRepository`:  
      - `create_account(account: Account)`: Persists a new account.  
      - `get_account_by_id(account_id: str)`: Retrieves an account by ID.  
      - `update_account(account: Account)`: Updates an existing account.  
    - `ITransactionRepository`:  
      - `save_transaction(transaction: Transaction)`: Persists a transaction.  
      - `get_transactions_for_account(account_id: str)`: Retrieves all transactions for an account.  
- **Interaction**:  
  - Uses Domain Layer entities (`Account`, `Transaction`) for business logic.  
  - Depends on the interfaces (`IAccountRepository`, `ITransactionRepository`) for persistence, which are implemented by the Infrastructure Layer.

![applicationLayerUML.png](UML%20diagrams/applicationLayerUML.png)

#### 2.1.3 Infrastructure Layer  
- **Role**: Provides concrete implementations of the persistence interfaces defined by the Application Layer and handles external service interactions.  
- **Components**:  
  - `AccountRepository`: Implements `IAccountRepository`.  
    - `create_account(account: Account)`: Persists a new account.  
    - `get_account_by_id(account_id: str)`: Retrieves an account by ID.  
    - `update_account(account: Account)`: Updates an existing account.  
  - `TransactionRepository`: Implements `ITransactionRepository`.  
    - `save_transaction(transaction: Transaction)`: Persists a transaction.  
    - `get_transactions_for_account(account_id: str)`: Retrieves all transactions for an account.  
- **Interaction**:  
  - Implements the persistence logic for the interfaces defined in the Application Layer.  
  - Used by the Application Layer to store and retrieve data.

![InfrastructureLayerUML.png](UML%20diagrams/InfrastructureLayerUML.png)

#### 2.1.4 Presentation Layer  
- **Role**: Handles incoming requests and outgoing responses via REST API endpoints.  
- **Components**: REST API endpoints for account creation, deposits, and withdrawals.  
- **Interaction**:  
  - Receives HTTP requests from clients.  
  - Forwards requests to the Application Layer services (e.g., `TransactionService`, `AccountCreationService`).  
  - Returns responses to clients.

### 2.2 Layer Integration  
- **Domain ↔ Application**: The Domain Layer provides business logic and entities that the Application Layer uses to perform operations.  
- **Application ↔ Infrastructure**: The Application Layer uses the interfaces (`IAccountRepository`, `ITransactionRepository`) it defines, which are implemented by the Infrastructure Layer, to persist and retrieve data.  
- **Application ↔ Presentation**: The Presentation Layer calls Application Layer services via REST endpoints (e.g., `POST /deposit` → `TransactionService.deposit()`).  
- **Presentation ↔ External Clients**: The Presentation Layer receives HTTP requests from clients and returns responses, acting as the entry point to the system.

![completeLayerUML.png](UML%20diagrams/completeLayerUML.png)

## 3. Key Workflows

### 3.1 Deposit Workflow  
1. The client sends a `POST /deposit` request with `account_id` and `amount`.  
2. The Presentation Layer forwards the request to `TransactionService.deposit()`.  
3. `TransactionService`:  
   - Fetches the account using `IAccountRepository.get_account_by_id()`.  
   - Calls `Account.deposit(amount)` to create a `Transaction` and update the balance.  
   - Saves the transaction using `ITransactionRepository.save_transaction()`.  
   - Updates the account using `IAccountRepository.update_account()`.  
4. The response (e.g., transaction ID) is returned to the client.

### 3.2 Withdrawal Workflow  
1. The client sends a `POST /withdraw` request with `account_id` and `amount`.  
2. The Presentation Layer forwards the request to `TransactionService.withdraw()`.  
3. `TransactionService`:  
   - Fetches the account using `IAccountRepository.get_account_by_id()`.  
   - Calls `BusinessRuleService.check_withdraw_allowed()` to validate the withdrawal.  
   - Calls `Account.withdraw(amount)` to create a `Transaction` and update the balance.  
   - Saves the transaction using `ITransactionRepository.save_transaction()`.  
   - Updates the account using `IAccountRepository.update_account()`.  
4. The response (e.g., transaction ID) is returned to the client.

### 3.3 Account Creation Workflow  
1. The client sends a `POST /account` request with `account_type` and `initial_deposit`.  
2. The Presentation Layer forwards the request to `AccountCreationService.create_account()`.  
3. `AccountCreationService`:  
   - Creates a new `Account` (or `CheckingAccount`/`SavingsAccount` based on `account_type`).  
   - Calls `Account.deposit(initial_deposit)` to set the initial balance.  
   - Persists the account using `IAccountRepository.create_account()`.  
4. The response (e.g., account ID) is returned to the client.

---

## 4. Design Principles and Patterns

- **Separation of Concerns**: Each layer has a distinct responsibility (e.g., domain for business logic, application for orchestration).  
- **Dependency Inversion**: The Application Layer defines repository interfaces (`IAccountRepository`, `ITransactionRepository`), which the Infrastructure Layer implements.  
- **Single Responsibility Principle**: Classes like `Account`, `TransactionService`, and `BusinessRuleService` have focused responsibilities.  
- **Repository Pattern**: Used to abstract persistence logic in the Infrastructure Layer.

---

## 5. Future Enhancements

- Add support for additional account types (e.g., Credit Accounts).  
- Implement transaction rollback for failed operations.  
- Introduce caching in the Infrastructure Layer for faster data retrieval.  
- Add audit logging for all transactions.

---
