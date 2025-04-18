# Banking System Documentation

## 1. Project Overview

### 1.1 Purpose  
The Banking System is designed to manage bank accounts and transactions, supporting operations like deposits, withdrawals, transfers, and account creation. It ensures robust business rule validation (e.g., minimum balance checks), data persistence, and auditability, following a clean, layered architecture for maintainability and scalability.

### 1.2 Scope  
The system supports:  
- Creating and managing accounts (Checking and Savings).  
- Performing transactions (deposits, withdrawals, and transfers between owned accounts).  
- Enforcing business rules (e.g., minimum balance for Savings accounts, withdrawal restrictions).  
- Persisting account and transaction data via repositories.  
- Sending automatic notifications (email/SMS) for transactions.  
- Logging transactions for auditability without cluttering core logic.

---

## 2. System Architecture

The system follows a layered architecture with four distinct layers: Domain, Application, Infrastructure, and Presentation. Each layer has a specific role and interacts with others through well-defined interfaces.

### 2.1 Layers and Their Roles

#### 2.1.1 Domain Layer  
- **Role**: Contains the core business logic, entities, and rules, focusing solely on the business domain without defining persistence interfaces.  

- **Interaction**:  
  - Encapsulates business logic and state.  
  - Used by the Application Layer to perform operations.  
  - `Account` generates `Transaction` objects during deposits, withdrawals, and transfers.  
  - Transfers are treated as atomic operations, ensuring both source withdrawal and destination deposit succeed or fail together.

**UML Diagram**:  
![DomainLayer.png](UML%20diagrams/week2/DomainLayer.png)

#### 2.1.2 Application Layer  
- **Role**: Orchestrates business operations by coordinating between the Domain and Infrastructure Layers, defining interfaces for persistence and external services that the Infrastructure Layer implements.  

- **Interaction**:  
  - Uses Domain Layer entities (`Account`, `Transaction`) for business logic.  
  - Depends on interfaces (`IAccountRepository`, `ITransactionRepository`, `INotificationAdapter`) for persistence and external services, implemented by the Infrastructure Layer.  
  - Employs a logging decorator or service to log operations without modifying core logic.

**UML Diagram**:  
![ApplicationLayer.png](UML%20diagrams/week2/ApplicationLayer.png)

#### 2.1.3 Infrastructure Layer  
- **Role**: Provides concrete implementations of persistence and external service interfaces defined by the Application Layer.  
-
- **Interaction**:  
  - Implements persistence logic using a relational database with tables for `accounts` and `transactions`.  
  - Uses database transactions to handle concurrency in transfers.  
  - Integrates with external services for notifications and logging.

**UML Diagram**:  
![InfrastuctureLayer.png](UML%20diagrams/week2/InfrastuctureLayer.png)

#### 2.1.4 Presentation Layer  
- **Role**: Handles incoming requests and outgoing responses via REST API endpoints.  
- **Components**: REST API endpoints for account creation, deposits, withdrawals, transfers, and notification subscriptions.  
- **Endpoints**:  
  - `POST /account`: Creates a new account.  
  - `POST /deposit`: Deposits funds into an account.  
  - `POST /withdraw`: Withdraws funds from an account.  
  - `POST /accounts/transfer`: Transfers funds between accounts.  
  - `POST /notifications/subscribe`: Subscribes an account to notifications.  
  - `POST /notifications/unsubscribe`: Unsubscribes an account from notifications.  
  - `GET /accounts/{account_id}/logs`: Retrieves transaction logs (optional, for admins).  
- **Interaction**:  
  - Receives HTTP requests from clients.  
  - Forwards requests to Application Layer services (e.g., `FundTransferService.transfer_funds()`).  
  - Returns JSON responses with transaction details or error messages.

**UML Diagram**:  
![PresentationLayer.png](UML%20diagrams/week2/PresentationLayer.png)

### 2.2 Layer Integration  
- **Domain ↔ Application**: The Domain Layer provides business logic and entities (`Account`, `Transaction`) that the Application Layer uses to perform operations. `FundTransferService` uses `BusinessRuleService` for transfer validation.  
- **Application ↔ Infrastructure**: The Application Layer defines interfaces (`IAccountRepository`, `ITransactionRepository`, `INotificationAdapter`) implemented by the Infrastructure Layer for persistence, notifications, and logging.  
- **Application ↔ Presentation**: The Presentation Layer calls Application Layer services via REST endpoints (e.g., `POST /accounts/transfer` → `FundTransferService.transfer_funds()`).  
- **Presentation ↔ External Clients**: The Presentation Layer receives HTTP requests and returns responses, acting as the system’s entry point.  
- **Cross-Cutting Concerns**: Logging is applied via a decorator or `LoggingService`, and notifications are triggered post-transaction via `NotificationService`, ensuring separation of concerns.

![CompleteLayer.png](UML%20diagrams/week2/CompleteLayer.png)

### 2.3 Technical Explanation of Workflows  
The new features (transfers, notifications, and logging) integrate seamlessly into the existing architecture while adhering to the same design principles (e.g., Separation of Concerns, Dependency Inversion).  

- **Fund Transfers**:  
  - **Integration**: The `FundTransferService` is a new Application Layer service that orchestrates transfers by fetching source and destination accounts, validating the transfer with `BusinessRuleService`, and performing an atomic operation (withdraw from source, deposit to destination). The `IAccountRepository.update_accounts_atomically()` ensures both accounts are updated consistently in a single database transaction, preventing partial updates. A `TRANSFER` transaction is saved with `source_account_id` and `destination_account_id` to track the operation.  
  - **Architecture Fit**: The transfer logic is encapsulated in the Application Layer, using Domain entities and rules, with persistence handled by the Infrastructure Layer. The `POST /accounts/transfer` endpoint exposes this functionality to clients.  
  - **Concurrency**: Optimistic locking or database transactions prevent race conditions during transfers.  

- **Notifications**:  
  - **Integration**: The `NotificationService` is invoked by `TransactionService` and `FundTransferService` after a transaction is committed. It uses the `INotificationAdapter` to send email/SMS notifications to the account owner(s). For transfers, notifications are sent to both source and destination account owners. The `POST /notifications/subscribe` and `POST /notifications/unsubscribe` endpoints allow users to configure notification preferences.  
  - **Architecture Fit**: Notifications are decoupled from transaction logic, ensuring the core business logic remains uncluttered. The Infrastructure Layer handles external integrations (e.g., email/SMS providers), while the Application Layer orchestrates the process.  
  - **Extensibility**: The `INotificationAdapter` interface allows easy swapping of providers (e.g., SendGrid for email, Twilio for SMS).  

- **Logging**:  
  - **Integration**: The `LoggingService` logs all operations (deposits, withdrawals, transfers) using a decorator pattern or direct calls from services. Logs include operation details (e.g., transaction ID, amount, timestamp) and are persisted to a file or external system (e.g., ELK stack). The optional `GET /accounts/{account_id}/logs` endpoint exposes logs for auditing.  
  - **Architecture Fit**: Logging is a cross-cutting concern applied without modifying core transaction logic, adhering to the Single Responsibility Principle. The Infrastructure Layer handles log persistence, while the Application Layer triggers logging.  
  - **Flexibility**: The logging mechanism supports selective logging (e.g., by transaction type) and can be extended to integrate with advanced logging solutions.

---

## 3. Key Workflows

### 3.1 Deposit Workflow  
1. The client sends a `POST /deposit` request with `account_id` and `amount`.  
2. The Presentation Layer forwards the request to `TransactionService.deposit()`.  
3. `TransactionService`:  
   - Fetches the account using `IAccountRepository.get_account_by_id()`.  
   - Calls `Account.deposit(amount)` to create a `Transaction` and update the balance.  
   - Saves the transaction using `ITransactionRepository.save_transaction()`.  
   - Updates the account using `IAccountRepository.update_account()`.  
   - Calls `NotificationService.notify()` to send email/SMS.  
   - Logs the operation via `LoggingService`.  
4. The response (transaction ID, new balance) is returned to the client.

### 3.2 Withdrawal Workflow  
1. The client sends a `POST /withdraw` request with `account_id` and `amount`.  
2. The Presentation Layer forwards the request to `TransactionService.withdraw()`.  
3. `TransactionService`:  
   - Fetches the account using `IAccountRepository.get_account_by_id()`.  
   - Calls `BusinessRuleService.check_withdraw_allowed()` to validate the withdrawal.  
   - Calls `Account.withdraw(amount)` to create a `Transaction` and update the balance.  
   - Saves the transaction using `ITransactionRepository.save_transaction()`.  
   - Updates the account using `IAccountRepository.update_account()`.  
   - Calls `NotificationService.notify()` to send email/SMS.  
   - Logs the operation via `LoggingService`.  
4. The response (transaction ID, new balance) is returned to the client.

### 3.3 Account Creation Workflow  
1. The client sends a `POST /account` request with `account_type`, `initial_deposit`, and `owner_id`.  
2. The Presentation Layer forwards the request to `AccountCreationService.create_account()`.  
3. `AccountCreationService`:  
   - Creates a new `Account` (or `CheckingAccount`/`SavingsAccount` based on `account_type`).  
   - Calls `Account.deposit(initial_deposit)` to set the initial balance.  
   - Persists the account using `IAccountRepository.create_account()`.  
   - Logs the operation via `LoggingService`.  
4. The response (account ID) is returned to the client.

### 3.4 Fund Transfer Workflow  
1. The client sends a `POST /accounts/transfer` request with `source_account_id`, `destination_account_id`, and `amount`.  
2. The Presentation Layer forwards the request to `FundTransferService.transfer_funds()`.  
3. `FundTransferService`:  
   - Fetches both accounts using `IAccountRepository.get_account_by_id()`.  
   - Calls `BusinessRuleService.check_transfer_allowed()` to validate the transfer (e.g., same owner, sufficient balance).  
   - Calls `Account.withdraw(amount)` on the source account to create a `Transaction`.  
   - Calls `Account.deposit(amount)` on the destination account to create a `Transaction`.  
   - Saves the transfer transaction (with `source_account_id` and `destination_account_id`) using `ITransactionRepository.save_transaction()`.  
   - Updates both accounts atomically using `IAccountRepository.update_accounts_atomically()`.  
   - Calls `NotificationService.notify()` to send email/SMS to both account owners.  
   - Logs the operation via `LoggingService`.  
4. The response (transaction ID, updated balances) is returned to the client.

### 3.5 Error Handling  
- **Invalid Inputs**: If `amount` is negative or accounts are invalid, a 400 Bad Request response is returned with a descriptive error message (e.g., `{"error": "Amount must be positive", "code": "INVALID_AMOUNT"}`).  
- **Insufficient Balance**: If a withdrawal or transfer fails due to insufficient funds, a 400 Bad Request response is returned (e.g., `{"error": "Insufficient balance", "code": "INSUFFICIENT_BALANCE"}`).  
- **Account Not Found**: If an `account_id` is invalid, a 404 Not Found response is returned.  
- **Concurrency Conflicts**: If optimistic locking fails during a transfer, the operation is retried or a 409 Conflict response is returned.

---

## 4. REST API Specifications

### POST /deposit  
Initiates a deposit into an account.  
**Request**:  
```json
{
  "account_id": "acc_123",
  "amount": 100.00
}
```  
**Response (Success, HTTP 200)**:  
```json
{
  "transaction_id": "txn_456",
  "new_balance": 1100.00,
  "timestamp": "2025-04-18T10:00:00Z"
}
```  
**Response (Error, HTTP 400)**:  
```json
{
  "error": "Invalid amount: Amount must be positive",
  "code": "INVALID_AMOUNT"
}
```

### POST /withdraw  
Initiates a withdrawal from an account.  
**Request**:  
```json
{
  "account_id": "acc_123",
  "amount": 50.00
}
```  
**Response (Success, HTTP 200)**:  
```json
{
  "transaction_id": "txn_457",
  "new_balance": 1050.00,
  "timestamp": "2025-04-18T10:01:00Z"
}
```  
**Response (Error, HTTP 400)**:  
```json
{
  "error": "Insufficient balance",
  "code": "INSUFFICIENT_BALANCE"
}
```

### POST /account  
Creates a new account.  
**Request**:  
```json
{
  "account_type": "CHECKING",
  "initial_deposit": 1000.00,
  "owner_id": "user_789"
}
```  
**Response (Success, HTTP 201)**:  
```json
{
  "account_id": "acc_123",
  "balance": 1000.00,
  "timestamp": "2025-04-18T10:02:00Z"
}
```

### POST /accounts/transfer  
Transfers funds between accounts.  
**Request**:  
```json
{
  "source_account_id": "acc_123",
  "destination_account_id": "acc_124",
  "amount": 100.00
}
```  
**Response (Success, HTTP 200)**:  
```json
{
  "transaction_id": "txn_458",
  "source_new_balance": 900.00,
  "destination_new_balance": 1100.00,
  "timestamp": "2025-04-18T10:03:00Z"
}
```  
**Response (Error, HTTP 400)**:  
```json
{
  "error": "Accounts must have the same owner",
  "code": "INVALID_TRANSFER"
}
```

### POST /notifications/subscribe  
Subscribes an account to notifications.  
**Request**:  
```json
{
  "account_id": "acc_123",
  "notify_type": "email"
}
```  
**Response (Success, HTTP 200)**:  
```json
{
  "message": "Subscribed to email notifications"
}
```

### POST /notifications/unsubscribe  
Unsubscribes an account from notifications.  
**Request**:  
```json
{
  "account_id": "acc_123",
  "notify_type": "email"
}
```  
**Response (Success, HTTP 200)**:  
```json
{
  "message": "Unsubscribed from email notifications"
}
```

### GET /accounts/{account_id}/logs  
Retrieves transaction logs for an account (admin only).  
**Request**: `GET /accounts/acc_123/logs`  
**Response (Success, HTTP 200)**:  
```json
[
  {
    "operation": "DEPOSIT",
    "transaction_id": "txn_456",
    "amount": 100.00,
    "timestamp": "2025-04-18T10:00:00Z"
  },
  {
    "operation": "TRANSFER",
    "transaction_id": "txn_458",
    "amount": 100.00,
    "timestamp": "2025-04-18T10:03:00Z"
  }
]
```





