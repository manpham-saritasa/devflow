<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Devflow Plugin — Shared Configuration</title>
  <style>
:root {
    --bg: #e2e8f0;
    --surface: #ffffff;
    --surface-2: #f1f4f8;
    --text: #1f2937;
    --muted: #5b6574;
    --border: #d9e0e7;
    --accent: #0f766e;
    --accent-soft: #e6f4f1;
    --warning: #9a3412;
    --shadow: 0 6px 15px rgba(15, 23, 42, 0.2);
    --radius: 9px;
    --title: #1e3a5f;
    --th-bg: #e6f4f8;
    --th-title: #1e3a5f;
    --h2-border-line: rgb(13, 148, 136);
    --table-even-row: #f8fafc;
    --table-border: #e5e7eb;
}
* {
    box-sizing: border-box;
}
body {
    margin: 0;
    font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif;
    font-size: 17px;
    color: var(--text);
    background: var(--bg);
    line-height: 1.65;
}
.page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 32px 20px 56px;
}
.header {
    background: linear-gradient(180deg, #ffffff 0%, #f7fbfb 100%);
    border: 1px solid var(--border);
    border-radius: 9px;
    box-shadow: var(--shadow);
    padding: 28px;
    margin-bottom: 26px;
    overflow: hidden;
}
.eyebrow {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 9px;
    background: var(--accent-soft);
    color: var(--accent);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 12px;
}
h1 {
    margin: 0 0 10px;
    font-size: 38px;
    line-height: 1.15;
    color: var(--title);
}
.meta {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
    margin-top: 18px;
}
.meta-item {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 9px;
    padding: 12px 14px;
}
.meta-label {
    display: block;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--muted);
    margin-bottom: 4px;
    font-weight: 700;
}
.section {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 9px;
    box-shadow: var(--shadow);
    padding: 24px;
    margin-bottom: 26px;
    overflow: hidden;
}
h2 {
    margin: 0 0 16px;
    font-size: 28px;
    color: var(--title);
    border-bottom: 2px solid var(--h2-border-line);
}
h3 {
    margin: 24px 0 10px;
    font-size: 20px;
    color: var(--title);
}
h4 {
    color: var(--title);
}
p.note {
    margin: 0 0 14px;
    color: var(--muted);
}
ul.clean {
    margin: 0;
    padding-left: 20px;
}
ul,
ol {
    margin: -5px 0 1em 0;
}
ul.clean li {
    margin: 6px 0;
}
table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border: 1px solid var(--table-border);
    border-radius: 9px;
    overflow: hidden;
    background: #fff;
}
th,
td {
    border-bottom: 1px solid var(--table-border);
    border-right: 1px solid var(--table-border);
    vertical-align: top;
    text-align: left;
    padding: 16px 16px;
    font-size: 15px;
}
th {
    background: var(--th-bg);
    font-size: 15px;
    color: var(--th-title);
}
tr:last-child td,
tr:last-child th {
    border-bottom: none;
}
td:last-child,
th:last-child {
    border-right: none;
}
tbody tr:nth-child(even) td {
    background: var(--table-even-row);
}
td ul {
    margin: 0;
    padding-left: 18px;
}
td li {
    margin: 4px 0;
}
pre {
    margin: 0 0 20px;
    padding: 16px;
    overflow-x: auto;
    border: 1px solid var(--border);
    border-radius: 9px;
    background: #0f172a;
    color: #e5eefc;
}
code {
    font-family:
        "Cascadia Code", "SFMono-Regular", Consolas, "Liberation Mono", Menlo,
        monospace;
}
p li pre code,
p pre code,
li pre code,
td pre code {
    color: inherit;
    background: transparent;
    padding: 0;
}
pre.mermaid {
    background: #f8fafc;
}
p code,
li code,
td code {
    background: #eef3f7;
    padding: 2px 6px;
    border-radius: 9px;
}
p li pre code,
p pre code,
li pre code,
td pre code {
    background: transparent;
    padding: 0;
}
.block-card {
    border: 1px solid var(--border);
    background: #fbfcfd;
    border-radius: 9px;
    padding: 14px 16px;
    overflow: hidden;
}
.example-box {
    border: 1px solid var(--border);
    background: #fbfcfd;
    border-radius: 9px;
    padding: 14px 16px;
    margin: 12px 0;
}
.example-box p {
    margin: 0;
}
.example-box.good-box {
    border-left: 4px solid #0f766e;
}
.example-box.bad-box {
    border-left: 4px solid #9a3412;
}
.blockquotes {
    border: 1px solid var(--border);
    background: #fbfcfd;
    border-radius: 9px;
    padding: 14px 16px;
    margin: 12px 0;
    border-left: 4px solid #e67e22;
}
.blockquotes p {
    margin: 0;
}
.block-grid {
    display: grid;
    gap: 14px;
}
.q {
    font-weight: 700;
    margin: 0 0 8px;
    color: var(--text);
}
.a {
    color: var(--muted);
    margin: 0;
}
strong,
h2,
h3,
h4 {
    color: var(--title);
}
a,
h1 {
    color: var(--accent);
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
@media (max-width: 760px) {
    .page {
        padding: 18px 12px 36px;
    }
    .header,
    .section {
        padding: 16px;
    }
    h1 {
        font-size: 32px;
    }
    h2 {
        font-size: 24px;
    }
    table,
    thead,
    tbody,
    th,
    td,
    tr {
        display: block;
    }
    thead {
        display: none;
    }
    tr {
        border: 1px solid var(--table-border);
        padding: 10px 0;
    }
    td {
        border: none;
        padding: 8px 0;
    }
    td::before {
        content: attr(data-label);
        display: block;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 4px;
    }
}

  </style>

</head>
<body>
  <main class="page">
<section class="header">
  <h1>Devflow Plugin — Shared Configuration</h1>
</section>
<section class="section">
<p>All skills and agents in this plugin reference these paths. Resolve relative to the plugin root.  </p>
</section>
<section class="section">
<h2>Paths</h2>
<table>
<thead>
<tr>
<th>Variable</th>
<th>Value</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Variable"><code>TASKS_ROOT</code></td>
<td data-label="Value"><code>.local/tasks</code></td>
<td data-label="Description">Task evidence folder (repo-relative)</td>
</tr>
<tr>
<td data-label="Variable"><code>TASK_DIR</code></td>
<td data-label="Value"><code>[TASKS_ROOT]/[KEY]</code></td>
<td data-label="Description">Per-task folder</td>
</tr>
<tr>
<td data-label="Variable"><code>ADR_DIR</code></td>
<td data-label="Value"><code>docs/adrs</code></td>
<td data-label="Description">Architecture Decision Records folder</td>
</tr>
</tbody>
</table>
</section>
<section class="section">
<h2>Work Mode</h2>
<table>
<thead>
<tr>
<th>Variable</th>
<th>Value</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Variable"><code>WORK_MODE</code></td>
<td data-label="Value"><code>default</code></td>
<td data-label="Description"><code>default</code> (full file pipeline), <code>manual</code> (chat only, no artifact files)</td>
</tr>
</tbody>
</table>
</section>
<section class="section">
<h2>Templates</h2>
<p>Located in <code>templates/</code> relative to the plugin root.</p>
<table>
<thead>
<tr>
<th>Variable</th>
<th>File</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Variable"><code>PLAN_TEMPLATE</code></td>
<td data-label="File"><code>templates/plan-template.md</code></td>
</tr>
<tr>
<td data-label="Variable"><code>PROGRESS_TEMPLATE</code></td>
<td data-label="File"><code>templates/progress-template.md</code></td>
</tr>
<tr>
<td data-label="Variable"><code>CHANGELOG_TEMPLATE</code></td>
<td data-label="File"><code>templates/changelog-template.md</code></td>
</tr>
<tr>
<td data-label="Variable"><code>REVIEW_TEMPLATE</code></td>
<td data-label="File"><code>templates/review-template.md</code></td>
</tr>
</tbody>
</table>
</section>
<section class="section">
<h2>Merge Strategy</h2>
<table>
<thead>
<tr>
<th>Variable</th>
<th>Value</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td data-label="Variable"><code>MERGE_STRATEGY</code></td>
<td data-label="Value"><code>--merge</code></td>
<td data-label="Description">Strategy passed to <code>gh pr merge</code>. Options: <code>--merge</code> (preserve history), <code>--rebase</code>, <code>--squash</code>.</td>
</tr>
</tbody>
</table>
</section>
  </main>
</body>
</html>
