# SQL/NoSQLInjection
English: SQL/NoSQL Injection
- Entry Count: 17
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## MySQLInjection - Basic detection
- ID: sqli-mysql-basic
- Difficulty: beginner
- Subcategory: MySQL
- Tags: sqli, mysql, injection, database
- Original Extracted Source: original extracted web-security-wiki source/sqli-mysql-basic.md
Description:
MySQLBasic Detection and Data Extraction Techniques for Database Injection
Prerequisites:
- Target existsSQLInjection point
- Backend database isMySQL
- Understand the basicsSQLSyntax
Execution Outline:
1. 1. Detect Injection Points
2. 2. Determine the number of columns
3. 3. Determine display position
4. 4. Obtain database information
## MySQLInjection - Advanced technology
- ID: sqli-mysql-advanced
- Difficulty: advanced
- Subcategory: MySQL
- Tags: sqli, mysql, advanced, file-read, rce
- Original Extracted Source: original extracted web-security-wiki source/sqli-mysql-advanced.md
Description:
MySQLAdvanced injection techniques: File read/write、UDFPrivilege escalation、Command execution
Prerequisites:
- MySQLThe user hasFILEPermissions
- Knowing the website's absolute path
- secure_file_privConfiguration allowed
Execution Outline:
1. 1. DetectionFILEPermissions
2. 2. Obtain website path
3. 3. Read sensitive files
4. 4. WriteWebShell
## MSSQLInjection - Basic detection
- ID: sqli-mssql-basic
- Difficulty: intermediate
- Subcategory: MSSQL
- Tags: sqli, mssql, sqlserver, injection
- Original Extracted Source: original extracted web-security-wiki source/sqli-mssql-basic.md
Description:
Microsoft SQL ServerDatabase injection techniques
Prerequisites:
- Target existsSQLInjection point
- Backend UsageMSSQLDatabase
Execution Outline:
1. 1. Detect Injection Points
2. 2. Obtain version information
3. 3. Retrieve user information
4. 4. Obtain database information
## MSSQLInjection - Advanced technology
- ID: sqli-mssql-advanced
- Difficulty: advanced
- Subcategory: MSSQL
- Tags: sqli, mssql, xp_cmdshell, rce
- Original Extracted Source: original extracted web-security-wiki source/sqli-mssql-advanced.md
Description:
MSSQLAdvanced injection:xp_cmdshell、SP_OACREATECommand execution
Prerequisites:
- MSSQLHigh privileges
- xp_cmdshellAvailable or can be enabled
Execution Outline:
1. 1. Detectionxp_cmdshellStatus
2. 2. Enablexp_cmdshell
3. 3. Execute system commands.
4. 4. WriteWebShell
## OracleInjection - Basic detection
- ID: sqli-oracle-basic
- Difficulty: intermediate
- Subcategory: Oracle
- Tags: sqli, oracle, injection
- Original Extracted Source: original extracted web-security-wiki source/sqli-oracle-basic.md
Description:
OracleBasic technology of database injection
Prerequisites:
- Target existsSQLInjection point
- Backend UsageOracleDatabase
Execution Outline:
1. 1. Detect Injection Points
2. 2. Obtain version information
3. 3. Retrieve user information
4. 4. Get Table Name
## OracleInjection - Advanced technology
- ID: sqli-oracle-advanced
- Difficulty: advanced
- Subcategory: Oracle
- Tags: sqli, oracle, advanced, rce
- Original Extracted Source: original extracted web-security-wiki source/sqli-oracle-advanced.md
Description:
OracleAdvanced injection techniques:JavaStored Procedure、UTL_FILEFile operation
Prerequisites:
- OracleHigh privileges
- JavaVirtual machine available
Execution Outline:
1. 1. DetectionJavaPermissions
2. 2. CreateJavaExecute function
3. 3. UTL_FILERead file
## PostgreSQLInjection - Basic detection
- ID: sqli-postgres-basic
- Difficulty: intermediate
- Subcategory: PostgreSQL
- Tags: sqli, postgresql, postgres, injection
- Original Extracted Source: original extracted web-security-wiki source/sqli-postgres-basic.md
Description:
PostgreSQLDatabase injection techniques
Prerequisites:
- Target existsSQLInjection point
- Backend UsagePostgreSQL
Execution Outline:
1. 1. Detect Injection Points
2. 2. Obtain version information
3. 3. Get Table Name
4. 4. Obtain Column Name
## SQLiteInjection
- ID: sqli-sqlite-basic
- Difficulty: intermediate
- Subcategory: SQLite
- Tags: sqli, sqlite
- Original Extracted Source: original extracted web-security-wiki source/sqli-sqlite-basic.md
Description:
SQLiteSQL injection attack
Prerequisites:
- SQLiteDatabase
- Exists injection point
Execution Outline:
1. 1. Detect Injection Points
2. 2. Get version
3. 3. Get Table Name
4. 4. Obtain table structure
## MongoDBInjection
- ID: sqli-mongodb-basic
- Difficulty: intermediate
- Subcategory: MongoDB
- Tags: nosql, mongodb, injection
- Original Extracted Source: original extracted web-security-wiki source/sqli-mongodb-basic.md
Description:
NoSQLDatabase Injection Attack Techniques
Prerequisites:
- Target usageMongoDB
- User input concatenates queries
Execution Outline:
1. 1. Detect Injection Points
2. 2. bypassing authentication
3. 3. Logical Operation Injection
4. 4. Regular injection
## RedisUnauthorized access
- ID: sqli-redis
- Difficulty: intermediate
- Subcategory: Redis
- Tags: redis, nosql, injection
- Original Extracted Source: original extracted web-security-wiki source/sqli-redis.md
Description:
RedisUnauthorized access and command injection
Prerequisites:
- RedisService accessibility
- Unauthorized or Weak Passwords
Execution Outline:
1. 1. DetectionRedis
2. 2. Unauthorized access
3. 3. WriteWebshell
4. 4. WriteSSHPublic key
## Boolean blind injection.
- ID: sqli-blind
- Difficulty: intermediate
- Subcategory: Blind injection
- Tags: sqli, blind, boolean
- Original Extracted Source: original extracted web-security-wiki source/sqli-blind.md
Description:
Based on Boolean conditionsSQLBlind injection techniques
Prerequisites:
- ExistenceSQLInjection
- The page is real/False two different responses
Execution Outline:
1. 1. Confirm blind injection
2. 2. Obtain database name length
3. 3. Character-by-character enumeration of database name
4. 4. Automate using tools
## Time-based blind injection
- ID: sqli-time-based
- Difficulty: intermediate
- Subcategory: Blind injection
- Tags: sqli, blind, time
- Original Extracted Source: original extracted web-security-wiki source/sqli-time-based.md
Description:
Time delay basedSQLBlind injection techniques
Prerequisites:
- ExistenceSQLInjection
- Page response time controllable
Execution Outline:
1. 1. Confirm time blind injection
2. 2. Obtain database name length
3. 3. Character-by-character extraction
4. 4. Different database delay functions
## Error injection
- ID: sqli-error-based
- Difficulty: intermediate
- Subcategory: Error injection
- Tags: sqli, error, extractvalue
- Original Extracted Source: original extracted web-security-wiki source/sqli-error-based.md
Description:
Extracting data using error messagesSQLInjection
Prerequisites:
- ExistenceSQLInjection
- Error messages will be displayed on the page.
Execution Outline:
1. 1. Confirm error injection
2. 2. Obtain database information
3. 3. Get Table Name
4. 4. Acquire data
## Second-orderSQLInjection
- ID: sqli-second-order
- Difficulty: advanced
- Subcategory: Second-order injection
- Tags: sqli, second-order, stored
- Original Extracted Source: original extracted web-security-wiki source/sqli-second-order.md
Description:
Triggered after storageSQLInjection attack
Prerequisites:
- Presence of Data Storage Function
- Stored data reused
Execution Outline:
1. 1. Detecting Second-order Injection
2. 2. Username injection
3. 3. Password reset injection
4. 4. Order/Comment Injection
## Union query injection
- ID: sqli-union
- Difficulty: beginner
- Subcategory: Union query
- Tags: sqli, union, select
- Original Extracted Source: original extracted web-security-wiki source/sqli-union.md
Description:
UseUNION SELECTExtract data
Prerequisites:
- Exists injection point
- Can display query results
Execution Outline:
1. 1. Determine the number of columns
2. 2. Determine display columns
3. 3. Extract data
4. 4. Bypass filter
## Stacked query injection
- ID: sqli-stacked
- Difficulty: intermediate
- Subcategory: Stacked Query
- Tags: sqli, stacked, queries
- Original Extracted Source: original extracted web-security-wiki source/sqli-stacked.md
Description:
Execute MultipleSQLInjection of statements
Prerequisites:
- Support multi-statement execution
- MySQL/PostgreSQL/MSSQL
Execution Outline:
1. 1. Probe stacked queries
2. 2. MySQLStacked Query
3. 3. MSSQLStacked Query
4. 4. PostgreSQLStacked Query
## SQLInjectionWAFBypass
- ID: sqli-waf-bypass
- Difficulty: advanced
- Subcategory: WAFBypass
- Tags: sqli, waf, bypass
- Original Extracted Source: original extracted web-security-wiki source/sqli-waf-bypass.md
Description:
BypassWebApplication firewall technologies
Prerequisites:
- Target existsSQLInjection point
- ExistenceWAFProtection
Execution Outline:
1. Chunked transfer encoding
2. HTTPParameter pollution(HPP)
3. Equivalent function replacement
4. No comma injection

