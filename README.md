# Group5_SWConstruction
## UML Diagram

+-------------------+       +-------------------+       +-------------------+
|    Account        |       |   Transaction     |       | AccountCreation   |
|-------------------|       |-------------------|       |      Service      |
| - account_id: str |       | - transaction_id  |       |-------------------|
| - account_type    |       | - type            |       | + create_account()|
| - balance         |       | - amount          |       +-------------------+
| - status          |       | - timestamp       |
| - creation_date   |       | - account_id      |       +-------------------+
|-------------------|       +-------------------+       |  Transaction      |
| + can_withdraw()  |                                   |      Service      |
+-------------------+       +-------------------+       |-------------------|
        ^                  | AccountRepository  |       | + deposit()       |
        |                  |-------------------|       | + withdraw()      |
+-------+-------+          | + create_account()|       +-------------------+
|               |          | + get_account()   |
| Checking      |          | + update_account()|       +-------------------+
| Account       |          +-------------------+       | Transaction       |
+---------------+                                      | Repository        |
|               |          +-------------------+       |-------------------|
+---------------+          | Transaction       |       | + save_tx()       |
        ^                  | Repository        |       | + get_txs_for()   |
        |                  |-------------------|       +-------------------+
+-------+-------+          | + save_tx()       |
|               |          | + get_txs_for()   |
| Savings       |          +-------------------+
| Account       |
|---------------|
| - MIN_BALANCE |
+---------------+