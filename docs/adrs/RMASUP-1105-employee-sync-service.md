# ADR: Introduce Azure AD Employee Sync Service

**Status:** ACCEPTED
**Task URL:** [RMASUP-1105](https://saritasa.atlassian.net/browse/RMASUP-1105)
**Date:** 2026-05-24

***

## 1. Current Context

The RMA system manages employee data but has no automated synchronization with Azure AD. Employees must exist in Azure AD for authentication and identity management, but provisioning them is manual — creating inconsistency and administrative overhead as the employee base grows.

| Area                         | Details                                  |
| ---------------------------- | ---------------------------------------- |
| Task goal                    | Automatically sync employee data from RMA to Azure AD (create and update). |
| Change trigger               | Manual employee provisioning in Azure AD is unsustainable. |
| Relevant constraints         | - Must use Microsoft Graph API.<br>- Must run as a background process.<br>- Must detect duplicate emails across companies.<br>- Must support a test mode for development. |
| Existing pattern or baseline | No automated sync. Employees are created/updated manually in Azure AD. |

***

## 2. Chosen Direction

- Introduce a background sync service that periodically synchronizes employee records from RMA to Azure AD.
- Use **Microsoft Graph API** as the integration point.
- Implement a **Reader/Writer abstraction** to decouple Graph API access from sync orchestration.
- Run sync operations in parallel. Detect duplicate emails and notify administrators.

***

## 3. Decision Scope

Establishes the integration pattern and service boundary for syncing employee data to Azure AD. Does not cover UI, authentication flows, or other Azure AD features beyond employee CRUD.

| Scope Type   | Details                                      | Client-friendly explanation    |
| ------------ | -------------------------------------------- | ------------------------------ |
| In scope     | Background sync service, Microsoft Graph integration, reader/writer abstraction, duplicate email detection, test mode. | How employees get created and updated in Azure AD automatically. |
| Out of scope | UI for managing sync, other Azure AD features (groups, roles, policies), authentication flow changes. | Not changing the login experience or admin screens. |
| Assumptions  | RMA employee data is the source of truth. Azure AD is the target. Graph API permissions are provisioned. | The RMA system knows what employees exist, and Azure AD has API access configured. |

***

## 4. Decision Reasons

#### Main reasons

- **Microsoft Graph API** is the only supported REST API for Azure AD management — no viable alternative.
- A **background service** decouples sync from user requests, avoiding latency and failure propagation.
- The **Reader/Writer abstraction** enables unit testing and allows future migration to a different identity provider without rewriting sync orchestration.

#### Why it fits the current architecture or team direction?

| Category                   | Reason              | Client-friendly explanation    |
| -------------------------- | ------------------- | ------------------------------ |
| Tech stack fit             | The project is .NET; `Microsoft.Graph` is the official .NET SDK. | Uses Microsoft's own library for Azure AD. |
| Background service pattern | The project already uses `BackgroundService` for scheduled tasks. | Follows the same pattern as other automated jobs. |
| Abstraction pattern        | Reader/Writer follows existing repository/service abstractions. | Same coding style — easier to maintain. |

#### Why it is better than the likely alternatives for this case?

| Summary                    | Reason              | Client-friendly explanation    |
| -------------------------- | ------------------- | ------------------------------ |
| Direct API calls without abstraction | Harder to test and swap providers, mixes orchestration with API details. | More risky and harder to change later. |
| Synchronous sync on user request | Blocks requests, fails visibly on Azure AD outages, poor UX. | Users would see errors when Azure AD is slow. |
| Third-party sync tool | Adds external dependency, less control over sync logic. | Another service to manage and pay for. |

***

## 5. Options Considered

All viable approaches converge on Microsoft Graph API. The decision is about how to wrap it.

| Option                                     | Benefits             | Tradeoffs         | Client-friendly explanation    |
| ------------------------------------------ | -------------------- | ----------------- | ------------------------------ |
| **Option 1 — Reader/Writer abstraction over Microsoft Graph** | Testable, swappable, clean separation of concerns. | Slightly more code than direct calls. | More work upfront, but safer and easier to change later. |
| Option 2 — Direct Microsoft Graph calls in the sync service | Less code, faster to implement. | Hard to test, tightly coupled to Graph SDK. | Quicker now, but risky and hard to change later. |
| Option 3 — Not needed | N/A | N/A | N/A |

***

## 6. Change Impact

The change introduces a new background service, configuration, and external API dependency. No database schema changes.

| Area                 | Impact                                                    |
| -------------------- | --------------------------------------------------------- |
| Code impact          | New `EmployeeSyncService`, `AzureAdEmployeeReader`, `DryAzureAdEmployeeWriter`, configuration settings. |
| Data / schema impact | None — reads from existing employee data, writes to Azure AD via API. |
| Security impact      | Requires Microsoft Graph API permissions. Credentials stored in app configuration. |
| Performance impact   | Background service runs on a schedule with parallel sync. No impact on user-facing requests. |
| Operational impact   | New configuration for company codes, Graph credentials, test mode. Monitoring needed for sync failures. |
| Testing impact       | Reader/Writer abstraction enables unit testing. Test mode allows running without real Azure AD calls. |

***

## 7. Expected Outcomes

Employee data stays consistent between RMA and Azure AD without manual work. Operational complexity increases with the new background service.

| Area           | Details                                                | Client-friendly explanation    |
| -------------- | ------------------------------------------------------ | ------------------------------ |
| Benefits       | Employee data stays consistent between RMA and Azure AD without manual work. | No more manual employee setup in Azure AD. |
| Tradeoffs      | New background service adds operational complexity. | Someone needs to monitor sync errors. |
| Follow-up work | Configure Graph API permissions, set up monitoring alerts. | IT grants API access and sets up alerts. |
| Risks          | Graph API rate limits may slow large syncs. Duplicate email logic depends on correct company code mapping. | Very large companies might sync slowly; email matching needs correct data. |

***

## 8. Pending Items

| Type                 | Details                                                                       |
| -------------------- | ----------------------------------------------------------------------------- |
| Pending validations  | Graph API rate limit impact under full employee load. Duplicate email logic with real multi-company data. |
| Pending dependencies | Microsoft Graph API permissions must be granted in the target Azure AD tenant. |
| Deferred decisions   | Extending sync to cover Azure AD groups, roles, or login policies. |

***

## 9. Open Questions

The sync service architecture is settled, but operational details need confirmation with the Azure AD admin.

- **Q1:** What Graph API permissions are required — `User.ReadWrite.All` or a more scoped application permission?  
  **A1:** Likely `User.ReadWrite.All` for full create/update; confirm with Azure AD admin before production.

- **Q2:** What is the sync schedule (interval and timing)?  
  **A2:** Configurable via settings. Default interval TBD with stakeholders based on propagation requirements.

- **Q3:** Should the sync also handle employee deletion/deactivation in Azure AD?  
  **A3:** Not in current scope. Can be added later if needed.

***

## 10. Supporting Evidence

- **Task evidence:**
    - [RMASUP-1105](https://saritasa.atlassian.net/browse/RMASUP-1105) — employee sync service from RMA to Azure AD.
- **PR evidence:**
    - [PR #645](https://github.com/saritasa-nest/rma-authentication/pull/645) — main implementation: `EmployeeSyncService`, reader/writer abstraction, background service, parallel sync, test mode, duplicate email detection (30+ commits).
    - [PR #749](https://github.com/saritasa-nest/rma-authentication/pull/749) — follow-up: null property checks, temp password, principal name assignment.
    - [PR #747](https://github.com/saritasa-nest/rma-authentication/pull/747) — dependency updates for the sync service.
    - [PR #781](https://github.com/saritasa-nest/rma-authentication/pull/781) — fix for mail nickname retrieval.
- **Plan evidence:**
    None — no local plan file available.
- **Review evidence:**
    PR #749 reviewed and approved with corrections for employee field handling.
- **Related ADRs / prior tasks:**
    None — first Azure AD integration ADR in this repository.

***

## 11. Future Review Guidance

- Future changes to employee sync must follow the Reader/Writer abstraction — do not bypass it with direct Graph API calls.
- Revisit this ADR if another identity provider is introduced, if Graph API costs or rate limits become a problem, or if sync scope expands to groups/roles.
