# ADR: Migrate GEO Database from SQL Server VM to Azure SQL Managed Instance

**Status:** PROPOSED
**Task URL:** [RMASUP-2134](https://saritasa.atlassian.net/browse/RMASUP-2134)
**Date:** 2026-05-22

***

## 1. Current Context

| Area                         | Details                                  |
| ---------------------------- | ---------------------------------------- |
| Task goal                    | Provide setup guidelines for a new modernized SQL Server, plan migration of the GEO database off legacy infrastructure, and resolve recurring performance issues. |
| Change trigger               | - SQL Server 2017 nears end of support. <br> - Running on an unsupported Windows OS — moderate risk. <br> - Recurring performance issues on the current GEO server. |
| Relevant constraints         | - SSRS catalog DB and engine are coupled to the current SQL Server. <br> - Some stored procedures read/write local Windows disk files — incompatible with any Azure SQL PaaS. <br> - DevOps team has no Azure subscription access; client controls the infrastructure. <br> - GEO DB moves first; RMA DB migration likely follows later to reduce dual-server management cost. |
| Existing pattern or baseline | GEO database on SQL Server 2017 running on a single Windows Server VM. Same VM also hosts the SSRS engine and catalog. |

***

## 2. Chosen Direction

- Migrate the GEO database (and later the RMA database) to **Azure SQL Managed Instance** — a fully managed PaaS offering with near-complete SQL Server surface compatibility.
- Move the **SSRS catalog database** to Azure SQL Managed Instance alongside GEO DB.
- Keep the **SSRS engine** on a small dedicated Windows VM — it has no PaaS equivalent anywhere.
- Refactor file I/O out of stored procedures into the application layer.
- Run a **migration assessment** via the SQL IaaS Agent Extension before locking in SKU, cost estimates, and the final migration plan.

***

## 3. Decision Scope

| Scope Type   | Details                                      | Client-friendly explanation    |
| ------------ | -------------------------------------------- | ------------------------------ |
| In scope     | - GEO DB migration to Azure SQL Managed Instance. <br> - SSRS catalog DB migration to Azure SQL Managed Instance. <br> - SSRS engine remains on a small dedicated VM. <br> - Refactoring file I/O out of SQL procedures. <br> - Running a migration assessment for compatibility, SKU sizing, and cost estimates. | We move your main database workload to a fully managed cloud database. Only the reporting engine stays on a small VM because Microsoft does not offer it as a managed service. |
| Out of scope | - RMA DB migration (deferred — planned later). <br> - SSRS engine replacement or migration to Power BI (separate workstream). <br> - Full application refactoring beyond file I/O changes. | Moving the RMA database and replacing the reporting engine are separate future efforts. This decision focuses only on the GEO database move. |
| Assumptions  | - Azure access (Contributor on the resource group) will be granted, or the client will run the assessment themselves. <br> - File I/O refactoring is feasible within the application codebase — devs already confirmed this. <br> - The migration assessment will not reveal hard blockers for Azure SQL Managed Instance. | We assume your team will either give us Azure access or run the compatibility scan yourselves, and that the scan will not find major surprises. |

***

## 4. Decision Reasons

#### Main reasons

- Azure SQL Managed Instance supports the full SQL Server surface (SQL Agent, linked servers, cross-database queries, CLR) — minimizing application rewrites compared to Azure SQL DB.
- Eliminates the Windows Server management layer for the database workload — no OS patching, no SQL Server patching.
- Built-in high availability, automated backups, and point-in-time restore out of the box.
- Can natively host the SSRS catalog database, which Azure SQL DB cannot — unblocking the reporting dependency without extra infrastructure.

<br>

#### Why it fits the current architecture or team direction?

| Category                   | Reason              | Client-friendly explanation    |
| -------------------------- | ------------------- | ------------------------------ |
| PaaS-first strategy        | Shifts the heavy database workload from self-managed VMs to a managed Azure service, reducing operational overhead. | Less time spent on server maintenance, more time on your product. |
| Incremental migration      | GEO DB moves first; RMA DB follows later to the same target platform — consistent, repeatable approach. | We start with one database, learn from it, then move the second one the same way. |
| Compatibility surface      | Azure SQL Managed Instance is the closest PaaS match to on-prem SQL Server, minimizing code changes. | Your existing SQL code needs the fewest changes with this option. |

<br>

#### Why it is better than the likely alternatives for this case?

| Summary                    | Reason              | Client-friendly explanation    |
| -------------------------- | ------------------- | ------------------------------ |
| SSRS catalog compatibility | Azure SQL DB cannot host the SSRS catalog database — Azure SQL Managed Instance can. | The alternative cloud database option would break your reporting. This one works. |
| Operational cost reduction | Eliminates Windows Server and SQL Server patching, OS-level monitoring, and manual backup management. | Less manual work to keep the database running, patched, and backed up. |
| Data-driven migration path | Migration assessment provides an exhaustive compatibility report with concrete object names — no guessing. | We get a detailed report showing exactly what needs to change before we commit. |

***

## 5. Options Considered

| Option                                     | Benefits             | Tradeoffs         | Client-friendly explanation    |
| ------------------------------------------ | -------------------- | ----------------- | ------------------------------ |
| **Option 1 — Azure SQL Managed Instance (chosen)** | - Near-full SQL Server surface compatibility. <br> - No Windows OS management. <br> - Built-in HA and automated backups. <br> - SSRS catalog DB supported natively. <br> - Migration assessment available for data-driven planning. | - Higher per-hour cost than a VM. <br> - Still requires a small VM for SSRS engine. <br> - File I/O from SQL must be refactored (same as any PaaS). | A managed database that handles most of the heavy lifting. You still need a small reporting server, but the main database is fully managed. |
| Option 2 — New SQL Server on a newer Windows VM | - Full SQL Server feature set — no application changes needed. <br> - Full control over server configuration. | - OS and SQL Server patching overhead continues. <br> - Manual HA and backup setup required. <br> - Same operational burden as today — not a modernization step. | Stay on a virtual machine with a newer SQL Server version. Same level of manual management you have today. |
| Option 3 — Azure SQL DB (single database) | - Lowest management overhead. <br> - Cheapest PaaS option. | - No SQL Agent, no linked servers, no cross-DB queries. <br> - Cannot host SSRS catalog DB — blocks the reporting dependency outright. <br> - Likely requires significant application rewrites. | The simplest cloud database, but it does not support many SQL Server features you rely on. Would require rebuilding parts of the application. |

***

## 6. Change Impact

| Area                 | Impact                                                    |
| -------------------- | --------------------------------------------------------- |
| Code impact          | - Stored procedures that read/write local disk files must be refactored to the application layer. <br> - Connection strings change to point to Azure SQL Managed Instance. |
| Data / schema impact | - GEO database and SSRS catalog database migrated to Azure SQL Managed Instance. <br> - No schema changes required by the platform itself. |
| Security impact      | - Authentication moves to Azure SQL Managed Instance auth model (Entra ID or SQL auth). <br> - Network security: private endpoint or VNet integration. <br> - Credential rotation and access control shift to Azure-managed patterns. |
| Performance impact   | - SKU sizing must be based on migration assessment and workload profiling. <br> - Recommended: collect 1 week of perf data covering a business peak before locking in SKU. <br> - Latency profile changes: app-to-database network path may differ from current intra-VM communication. |
| Operational impact   | - No more Windows Server or SQL Server patching for the database. <br> - Backups become Azure-managed (automated, configurable retention). <br> - Monitoring shifts to Azure portal and Azure SQL analytics. <br> - Small SSRS VM still requires patching and maintenance. |
| Testing impact       | - Migration assessment validates compatibility before migration. <br> - Application regression testing for connection string changes and file I/O refactoring. <br> - Performance testing to validate SKU choice under real workload. |

***

## 7. Expected Outcomes

| Area           | Details                                                | Client-friendly explanation    |
| -------------- | ------------------------------------------------------ | ------------------------------ |
| Benefits       | - Eliminates Windows Server management for the database layer. <br> - Built-in high availability and automated backups. <br> - Modern, supported platform with a clear upgrade path. <br> - Consistent target for future RMA DB migration — same platform, same approach. | Less operational work, built-in reliability features, and a modern platform that will be supported for years. |
| Tradeoffs      | - SSRS engine still requires a small VM — not fully VM-free. <br> - File I/O stored procedures must be refactored. <br> - Less direct control over SQL Server internals compared to a VM. <br> - Monthly cost may be higher than a comparable VM depending on the recommended SKU. | You still need one small server for reporting, and some database code that touches files needs updating. |
| Follow-up work | - Obtain Azure access or have client run the migration assessment. <br> - Register SQL IaaS Agent Extension and run assessment (a couple of days of work). <br> - Collect perf data for 1 week before finalizing SKU. <br> - Refactor file I/O procedures. <br> - Plan and execute GEO DB migration. <br> - Plan RMA DB migration as a separate phase. | After this decision, we run a compatibility scan, update some database code, then move the database. Later, we repeat the process for the RMA database. |
| Risks          | - Migration assessment may reveal hard blockers for Azure SQL Managed Instance. <br> - File I/O refactoring scope may be larger than estimated. <br> - Azure access delays may stall the assessment phase — speed depends on the client. <br> - Cost may exceed client expectations depending on the recommended SKU. | There is a small chance the compatibility scan finds issues we cannot easily fix, or that costs are higher than expected. The scan is designed to catch these before we commit. |

***

## 8. Pending Items

| Type                 | Details                                                                       |
| -------------------- | ----------------------------------------------------------------------------- |
| Pending validations  | - Migration assessment report: compatibility blockers, SKU recommendation, cost estimates. <br> - 1-week workload perf data collection to validate SKU sizing. <br> - Full list of databases and services affected (currently only high-level picture known; report will reveal hidden details). |
| Pending dependencies | - Azure subscription access (Contributor on the resource group) or client-run assessment. <br> - Client approval of the Azure SQL Managed Instance approach. <br> - Developer availability for file I/O refactoring. |
| Deferred decisions   | - RMA DB migration timing and scope. <br> - SSRS engine long-term direction: stay on VM vs. migrate paginated reports to Power BI. <br> - Whether GEO and RMA databases consolidate on a single Azure SQL Managed Instance or use separate instances. |

***

## 9. Open Questions

- **Q1:** Will the client grant Azure Contributor access, or will they run the migration assessment themselves?
  **A1:** Either path works. Direct access is faster. Client-run assessment requires clear step-by-step instructions.

- **Q2:** What is the expected timeline for the GEO DB migration after the assessment is complete?
  **A2:** To be determined after the assessment report and SKU recommendation are available.

- **Q3:** Should the eventual RMA DB migration target the same Azure SQL Managed Instance or a separate one?
  **A3:** Consolidating on one instance reduces cost and management overhead. The migration assessment should evaluate this option.

- **Q4:** Is the client open to refactoring SSRS paginated reports to Power BI in the future, which would eliminate the SSRS VM entirely?
  **A4:** Not yet discussed. A separate workstream if the client shows interest.

***

## 10. Supporting Evidence

- **Task evidence:** RMASUP-2134 — DevOps recommendation by Maxim Omelchenko to use Azure SQL Managed Instance. Rationale documented in Jira comments (2026-05-19 through 2026-05-21). Confluence report at [2134 - New SQL Server and GEO Database Migration](https://saritasa.atlassian.net/wiki/spaces/RC/pages/3924426753/2134+-+New+SQL+Server+and+GEO+Database+Migration).
- **Plan evidence:** None — no formal `plan.md` exists yet.
- **Review evidence:** None — no `review.md` exists yet.
- **Related ADRs / prior tasks:** None.

***

## 11. Future Review Guidance

- Future changes in this area should follow the PaaS-first principle: prefer Azure SQL Managed Instance over VMs for SQL Server workloads unless a specific incompatibility is proven by the migration assessment.
- Revisit this ADR if the migration assessment reveals a hard blocker for Azure SQL Managed Instance that cannot be resolved within acceptable effort.
- Revisit this ADR if the recommended SKU cost exceeds the client's budget by more than 50% of the current VM cost.
- Revisit when the RMA DB migration is planned — the decision to consolidate on one instance vs. separate instances should be made at that time.
- Revisit if the full list of databases and services from the assessment report reveals components not accounted for in the current scope.
