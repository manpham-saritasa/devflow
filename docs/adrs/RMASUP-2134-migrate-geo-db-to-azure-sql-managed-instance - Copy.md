# ADR: GEO Database Migration Target and SQL Platform Direction

**Status:** PROPOSED
**Task URL:** [RMASUP-2134](https://saritasa.atlassian.net/browse/RMASUP-2134)
**Date:** 2026-05-22

***

## 1. Current Context

| Area                         | Details                                                                                                                                                                                                                                                                                                            |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Task goal                    | Give the client setup guidance and best practices for the new modernized SQL server.                                                                                                                                                                                                                               |
| Change trigger               | The current GEO database is running on SQL Server 2017 on soon-to-be unsupported operating systems, and the current GEO server has recurring performance issues.                                                                                                                                                   |
| Relevant constraints         | - GEO moves first.<br>- RMA may move later to the same target.<br>- SQL Server feature compatibility is important.<br>- Some procedures use local Windows disk.<br>- SSRS is part of the current setup.<br>- Final cost still needs validation.<br>- Final migration scope still depends on the assessment report. |
| Existing pattern or baseline | The current solution uses server-based SQL Server infrastructure, and SQL Server plus reporting are tied to Windows Server management overhead.                                                                                                                                                                    |

***

## 2. Chosen Direction

- Recommend Azure SQL Managed Instance as the target database platform.
- Treat GEO migration as phase 1 and keep the path open for a later RMA migration into the same environment.
- Keep SSRS engine hosting as a separate workstream, and do not treat this ADR as final cost approval, final sizing, or full migration approval.

***

## 3. Decision Scope

| Scope Type   | Details                                                                                                                                           | Client-friendly explanation                                                                            |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| In scope     | Select the preferred platform direction for the new SQL environment.                                                                              | This ADR decides the recommended target direction, not every technical detail of the final migration.  |
| Out of scope | - Final cost approval.<br>- Exact SKU sizing.<br>- Exact migration runbook.<br>- Full component inventory.<br>- Final SSRS engine hosting design. | These items still depend on the migration assessment and later planning work.                          |
| Assumptions  | - The client needs a recommendation now.<br>- Detailed validation will come after access and assessment.<br>- GEO is the first migration target.  | The team needs a clear recommendation first, while keeping room for validation before final execution. |

***

## 4. Decision Reasons

#### Main decision

- Azure SQL Managed Instance was chosen because it best matches the current SQL Server feature set, reduces rewrite risk, and provides a better long-term operating model than the likely alternatives.
- It is also the most practical balance between compatibility, modernization, and future GEO plus RMA consolidation.

<br>

#### Why it fits the current architecture or team direction?

| Category          | Reason                                                                                                                        | Client-friendly explanation                                                                                       |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| SQL compatibility | It supports SQL Agent, linked servers, cross-database queries, and other SQL Server features used in the current environment. | This lowers migration risk and reduces the amount of application or database rewrite work.                        |
| Reporting support | It can host SSRS catalog databases, which fits the current reporting setup better than Azure SQL Database.                    | The reporting data layer can move with the rest of the SQL workload, even if the SSRS engine remains on a VM.     |
| Operating model   | It removes the Windows Server layer and reduces overhead around patching, backups, and built-in high availability.            | This simplifies long-term maintenance and reduces the amount of infrastructure the team needs to manage directly. |

<br>

#### Why it is better than the likely alternatives for this case?

| Summary                   | Reason                                                                                                                        | Client-friendly explanation                                                                                  |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Better than Azure SQL DB  | Azure SQL Database would likely require more rewrite work and has a known SSRS catalog limitation.                            | It is less suitable for the current workload because it creates more migration risk and feature gaps.        |
| Better than staying on VM | Managed Instance modernizes the main database workload while avoiding the larger Windows and SQL Server VM management burden. | The heavier SQL workload moves to a managed platform, while only a smaller and simpler reporting VM remains. |
| Better for long-term path | It supports GEO migration now while leaving room for a later RMA move into the same managed environment.                      | This creates a cleaner long-term consolidation path without forcing all migration work into one phase.       |

***

## 5. Options Considered

| Option                                    | Benefits                                                                                                                                                                                                                                                                                           | Tradeoffs                                                                                                                                                                                                              | Client-friendly explanation                                                                                                                 |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Option 1 — Azure SQL Managed Instance** | - High SQL Server compatibility.<br>- Supports SQL Agent, linked servers, and cross-database queries.<br>- Supports SSRS catalog databases.<br>- Reduces Windows Server overhead.<br>- Includes high availability and backups.<br>- Supports GEO-first migration and possible later RMA migration. | - Still needs assessment before cost and sizing are trusted.<br>- Some file-based procedures must be refactored.<br>- SSRS engine still needs separate hosting, typically on a Windows VM. | This is the best fit for the current system because it keeps strong SQL Server compatibility while improving the long-term operating model. |
| Option 2 — Azure SQL Database             | - Managed PaaS database service.<br>- Less infrastructure to manage than a VM.                                                                                                                                                                                                                     | - Lower SQL Server compatibility.<br>- Cannot host SSRS catalog databases.<br>- Likely needs more rewrite work.                                                                                                        | This is simpler as a pure platform service, but it creates more migration risk for the current system.                                      |
| Option 3 — New SQL Server on VM           | - High short-term compatibility.<br>- Easier lift-and-shift path.                                                                                                                                                                                                                                  | - Keeps Windows Server overhead.<br>- Keeps more maintenance burden.<br>- Gives less modernization benefit.                                                                                                            | This is safer short term, but weaker as a long-term platform choice.                                                                        |

***

## 6. Change Impact

| Area                 | Impact                                                                                                                                                                                                                                         |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Code impact          | - Procedures that read or write files on local Windows disk must be refactored.<br>- The cleanest approach is to move file handling into the app layer.                                                                                        |
| Data / schema impact | - GEO database moves first.<br>- SSRS catalog databases can move to Azure SQL Managed Instance.<br>- Full compatibility still needs assessment.<br>- The full final list of databases and services still depends on the assessment report.     |
| Security impact      | Azure access and permissions must be coordinated to run the assessment and manage the target environment.                                                                                                                                      |
| Performance impact   | The target should improve operations and reliability, but final sizing depends on workload data and assessment output.                                                                                                                         |
| Operational impact   | - The team needs Azure access or help from the client team to run the assessment.<br>- The SSRS engine remains on a smaller VM for now.<br>- The assessment may need about one week of performance data to support better SKU recommendations. |
| Testing impact       | - Migration needs compatibility checks.<br>- Migration needs workload checks.<br>- Migration needs reporting checks.<br>- Migration needs post-migration verification.                                                                         |

***

## 7. Expected Outcomes

| Area           | Details                                                                                                                                                                                                                                                                           | Client-friendly explanation                                                                           |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Benefits       | - Clear platform direction now.<br>- Lower long-term infrastructure overhead.<br>- Better SQL Server compatibility than Azure SQL Database.<br>- Room for future GEO and RMA consolidation.                                                                                       | The team can move forward with planning now while still keeping a practical long-term direction.      |
| Tradeoffs      | - Some decisions remain open.<br>- Azure access is still a blocker.<br>- Some refactoring may be needed.<br>- The reporting engine remains on a VM in the short term.                                                                                                             | This is a strong direction, but it still depends on assessment results and a few follow-up decisions. |
| Follow-up work | - Get the first assessment report.<br>- Review cost estimates.<br>- Review SKU recommendation.<br>- Collect about one week of performance data if possible.<br>- Align the plan with Dmitry before wider sharing.<br>- Confirm the SSRS plan.<br>- Prepare the migration runbook. | The next step is validation and planning, not immediate full execution.                               |
| Risks          | - Hidden compatibility issues may appear in the assessment.<br>- Access delays may slow planning.<br>- Actual cost may change after real sizing data is available.                                                                                                                | The recommendation is strong, but it still needs assessment data to reduce surprise risks.            |

***

## 8. Pending Items

| Type                 | Details                                                                                                                                                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pending validations  | - Migration assessment report.<br>- Compatibility blockers.<br>- Affected objects.<br>- Full component inventory.<br>- SKU recommendation.<br>- Workload-based sizing.<br>- Cost estimates.                               |
| Pending dependencies | - Azure subscription or VM-level access to register the SQL IaaS Agent extension and run the assessment.<br>- Or the client team running it and sharing the report.<br>- Alignment with Dmitry before wider team sharing. |
| Deferred decisions   | - Final SSRS engine hosting approach.<br>- Final migration runbook details.<br>- Final decision on GEO and RMA sharing one managed instance.<br>- Possible future move from SSRS to another reporting approach if needed. |

