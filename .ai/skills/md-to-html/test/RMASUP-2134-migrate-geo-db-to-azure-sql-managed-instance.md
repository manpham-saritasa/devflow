# ADR: Migrate GEO Database from SQL Server VM to Azure SQL Managed Instance

**Status:** PROPOSED
**Task URL:** [RMASUP-2134](https://saritasa.atlassian.net/browse/RMASUP-2134)
**Date:** 2026-05-22

***

## 1. Current Context

The GEO database and SSRS run on a single aging SQL Server 2017 VM. The client needs a modernization plan that resolves performance issues and sets a foundation for future RMA migration.

| Area                         | Details                                  |
| ---------------------------- | ---------------------------------------- |
| Task goal                    | Plan migration of the GEO database off legacy infrastructure to a modern SQL platform. Provide setup guidelines and best practices for the new SQL server to Don Piliero (Certerra team). Resolve recurring performance issues on the current GEO server. |
| Change trigger               | - SQL Server 2017 nearing end of support. <br> - Running on an unsupported Windows OS — moderate risk. <br> - Recurring performance issues on the current GEO server. <br> - Client meeting (Wed 2026-05-20) required a high-level recommendation. |
| Relevant constraints         | - SSRS catalog DB and engine are coupled to the current SQL Server on the same VM. <br> - Some stored procedures read/write local Windows disk files — incompatible with any Azure SQL PaaS. <br> - DevOps team has no Azure subscription access; client (Certerra) controls the infrastructure. <br> - GEO DB moves first; RMA DB migration likely follows later to reduce dual-server management cost. |
| Existing pattern or baseline | GEO database on SQL Server 2017 running on a single Windows Server VM. Same VM also hosts the SSRS engine and its catalog database. |

***

## 2. Chosen Direction

- Migrate the **GEO database** (and later the **RMA database**) to **Azure SQL Managed Instance** — a managed PaaS offering with near-full SQL Server surface compatibility.
- Move the **SSRS catalog database** to Azure SQL Managed Instance alongside the GEO DB.
- Keep the **SSRS engine** on a small dedicated Windows VM — SSRS has no PaaS equivalent.
- Refactor file I/O out of stored procedures into the application layer.
- Run a **migration assessment** via the SQL IaaS Agent Extension before locking in SKU, cost estimates, and the final migration plan.

***

## 3. Decision Scope

This ADR decides the target platform and migration approach for the GEO database. It does not prescribe the full implementation plan or the separate documentation deliverables.

| Scope Type   | Details                                      | Client-friendly explanation    |
| ------------ | -------------------------------------------- | ------------------------------ |
| In scope     | - GEO DB and SSRS catalog DB migration to Azure SQL Managed Instance. <br> - SSRS engine stays on a small dedicated VM. <br> - Refactoring file I/O out of stored procedures. <br> - Running a migration assessment for compatibility blockers, SKU sizing, and cost estimates. | Your main database workload moves to a fully managed cloud database. Only the reporting engine stays on a small VM because Microsoft doesn't offer it as a managed service. |
| Out of scope | - RMA DB migration (deferred — separate phase). <br> - SSRS engine replacement or paginated report migration to Power BI (separate workstream). <br> - Application refactoring beyond file I/O changes. <br> - "Recommended Settings" and "SQL Server Setup Documentation" deliverables (separate output docs, not decided here). | Moving the RMA database and replacing the reporting engine are separate future efforts. This ADR decides the target platform and migration approach only. |
| Assumptions  | - Azure access (Contributor on the resource group containing the VM) will be granted, or the client will run the assessment steps themselves. <br> - File I/O refactoring is feasible — devs already confirmed. <br> - Migration assessment will not reveal hard blockers for Azure SQL Managed Instance. | We assume your team will either grant us Azure access or run the compatibility scan yourselves, and that the scan won't find major surprises. |

***

## 4. Decision Reasons

#### Main reasons

- Azure SQL Managed Instance supports the full SQL Server surface (SQL Agent, linked servers, cross-database queries, CLR) — minimizing rewrites compared to Azure SQL DB.
- Eliminates the Windows Server management layer for the database workload — no OS or SQL Server patching.
- Built-in high availability, automated backups, and point-in-time restore out of the box.
- Natively hosts the SSRS catalog database — Azure SQL DB cannot, which would block the reporting dependency.

<br>

#### Why it fits the current architecture or team direction?

| Category                   | Reason              | Client-friendly explanation    |
| -------------------------- | ------------------- | ------------------------------ |
| PaaS-first strategy        | Shifts the heavy database workload from self-managed VMs to a managed Azure service, reducing operational overhead. | Less time spent on server maintenance — more time on your product. |
| Incremental migration      | GEO DB moves first; RMA DB follows later to the same target platform — consistent, repeatable approach. | Start with one database, learn from it, then move the second one the same way. |
| Compatibility surface      | Azure SQL Managed Instance is the closest PaaS match to on-prem SQL Server — least code change required. | Your existing SQL code needs the fewest changes with this option. |

<br>

#### Why it is better than the likely alternatives for this case?

| Summary                    | Reason              | Client-friendly explanation    |
| -------------------------- | ------------------- | ------------------------------ |
| SSRS catalog compatibility | Azure SQL DB cannot host the SSRS catalog database — Azure SQL Managed Instance can. | The cheaper cloud database option would break your reporting. This one works. |
| Operational cost reduction | Eliminates Windows Server and SQL Server patching, OS-level monitoring, and manual backup management. | Less manual work to keep the database running, patched, and backed up. |
| Data-driven migration path | Migration assessment provides an exhaustive compatibility report with concrete object names — no guessing. | A detailed report shows exactly what needs to change before we commit. |

***

## 5. Options Considered

Three options were evaluated against compatibility, operational cost, and long-term maintainability.

| Option                                     | Benefits             | Tradeoffs         | Client-friendly explanation    |
| ------------------------------------------ | -------------------- | ----------------- | ------------------------------ |
| **Option 1 — Azure SQL Managed Instance (chosen)** | - Near-full SQL Server surface compatibility. <br> - No Windows OS management. <br> - Built-in HA and automated backups. <br> - SSRS catalog DB supported natively. <br> - Migration assessment available. | - Higher per-hour cost than a VM (SKU-dependent). <br> - Still needs a small VM for SSRS engine. <br> - File I/O from SQL must be refactored (same as any PaaS). | A managed database that handles most of the heavy lifting. You still need a small reporting server, but the main database is fully managed. |
| Option 2 — New SQL Server on a newer Windows VM | - Full SQL Server feature set — no application changes. <br> - Full control over server configuration. | - OS and SQL Server patching overhead continues. <br> - Manual HA and backup setup required. <br> - Same operational burden as today — not a modernization step. | Stay on a virtual machine with a newer SQL Server version. Same level of manual management you have today. |
| Option 3 — Azure SQL DB (single database) | - Lowest management overhead. <br> - Cheapest PaaS option. | - No SQL Agent, linked servers, or cross-DB queries. <br> - Cannot host SSRS catalog DB — blocks the reporting dependency outright. <br> - Likely requires significant application rewrites. | The simplest cloud database, but it does not support many SQL Server features you rely on. Would require rebuilding parts of the application. |

***

## 6. Change Impact

Moving from a self-managed VM to Azure SQL Managed Instance affects code, operations, security, and performance. The migration assessment will quantify these impacts.

| Area                 | Impact                                                    |
| -------------------- | --------------------------------------------------------- |
| Code impact          | - Stored procedures that read/write local disk files must be refactored to the application layer. <br> - Connection strings change to point to Azure SQL Managed Instance. |
| Data / schema impact | - GEO database and SSRS catalog database migrated to Azure SQL Managed Instance. <br> - No schema changes required by the platform. |
| Security impact      | - Authentication moves to Azure SQL Managed Instance auth model (Entra ID or SQL auth). <br> - Network security: private endpoint or VNet integration required. <br> - Credential rotation and access control shift to Azure-managed patterns. |
| Performance impact   | - SKU sizing must be based on migration assessment and workload profiling. <br> - Recommended: collect 1 week of perf data covering a business peak before locking in SKU. <br> - App-to-database network path may differ from current intra-VM communication — latency profile changes. |
| Operational impact   | - No more Windows Server or SQL Server patching for the database layer. <br> - Backups become Azure-managed (automated, configurable retention). <br> - Monitoring shifts to Azure portal and Azure SQL analytics. <br> - Small SSRS VM still requires patching and maintenance. |
| Testing impact       | - Migration assessment validates compatibility before migration. <br> - Application regression testing for connection string changes and file I/O refactoring. <br> - Performance testing to validate SKU choice under real workload. |

***

## 7. Expected Outcomes

If accepted, this decision reduces operational burden, provides built-in reliability, and creates a repeatable pattern for the RMA migration. It also introduces new cost and refactoring requirements.

| Area           | Details                                                | Client-friendly explanation    |
| -------------- | ------------------------------------------------------ | ------------------------------ |
| Benefits       | - Eliminates Windows Server management for the database layer. <br> - Built-in high availability and automated backups. <br> - Modern, supported platform with a clear upgrade path. <br> - Consistent target for future RMA DB migration — same platform, same approach. | Less operational work, built-in reliability features, and a modern platform supported for years. |
| Tradeoffs      | - SSRS engine still requires a small VM — not fully VM-free. <br> - File I/O stored procedures must be refactored. <br> - Less direct control over SQL Server internals vs. a VM. <br> - Monthly cost may be higher than a comparable VM depending on the recommended SKU. | You still need one small server for reporting, and some database code that touches files needs updating. |
| Follow-up work | - Obtain Azure access or have client run the migration assessment. <br> - Register SQL IaaS Agent Extension and run assessment (~2 days of work). <br> - Collect perf data for 1 week before finalizing SKU. <br> - Refactor file I/O procedures. <br> - Plan and execute GEO DB migration. <br> - Plan RMA DB migration as a separate phase. | After this decision, we run a compatibility scan, update some database code, then move the database. Later, repeat for the RMA database. |
| Risks          | - Migration assessment may reveal hard blockers for Azure SQL Managed Instance. <br> - File I/O refactoring scope may be larger than estimated. <br> - Azure access delays may stall the assessment — speed depends on the client. <br> - Cost may exceed client expectations depending on the recommended SKU. | There is a small chance the compatibility scan finds issues we cannot easily fix, or that costs are higher than expected. The scan is designed to catch these before we commit. |

***

## 8. Pending Items

Several items must be resolved before migration can proceed. The migration assessment is the critical first step — it will answer most of the open validation questions below.

| Type                 | Details                                                                       |
| -------------------- | ----------------------------------------------------------------------------- |
| Pending validations  | - Migration assessment report: compatibility blockers, SKU recommendation, cost estimates. <br> - 1-week workload perf data collection to validate SKU sizing. <br> - Full list of databases and services affected (currently only high-level picture known; report reveals hidden details). |
| Pending dependencies | - Azure subscription access (Contributor on the resource group) or client-run assessment. <br> - Client (Certerra / Don Piliero) approval of the Azure SQL Managed Instance approach. <br> - Developer availability for file I/O refactoring. |
| Deferred decisions   | - RMA DB migration timing and scope. <br> - SSRS engine long-term direction: stay on VM vs. migrate paginated reports to Power BI. <br> - Whether GEO and RMA databases consolidate on a single Azure SQL Managed Instance or use separate instances. |

***

## 9. Open Questions

These questions need answers from the client or team before finalizing the migration plan. Prefilled answers suggest the likely direction.

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

- **Task evidence:** RMASUP-2134 — DevOps recommendation by Maxim Omelchenko to use Azure SQL Managed Instance. Rationale documented in Jira comments (2026-05-19 through 2026-05-21). Confluence report at [2134 - New SQL Server and GEO Database Migration](https://saritasa.atlassian.net/wiki/spaces/RC/pages/3924426753/2134+-+New+SQL+Server+and+GEO+Database+Migration). Client: Don Piliero (Certerra team).
- **Plan evidence:** None — no formal `plan.md` exists.
- **Review evidence:** None — no `review.md` exists.
- **Related ADRs / prior tasks:** None.

***

## 11. Future Review Guidance

- Future changes in this area should follow the PaaS-first principle: prefer Azure SQL Managed Instance over VMs for SQL Server workloads unless a specific incompatibility is proven by the migration assessment.
- Revisit this ADR if the migration assessment reveals a hard blocker for Azure SQL Managed Instance that cannot be resolved within acceptable effort.
- Revisit this ADR if the recommended SKU cost exceeds the client's budget by more than 50% of the current VM cost.
- Revisit when the RMA DB migration is planned — the decision to consolidate on one instance vs. separate instances should be made at that time.
- Revisit if the full list of databases and services from the assessment report reveals components not accounted for in the current scope.
