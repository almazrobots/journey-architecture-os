# Security and privacy

## Reporting a vulnerability

Report security issues privately through GitHub private vulnerability reporting: open the repository's **Security** tab and choose **Report a vulnerability**. Do not open a public issue for a vulnerability.

Include the affected file or script, steps to reproduce, and the impact you expect. The maintainers acknowledge the report in the advisory thread and publish the advisory, with credit unless you ask otherwise, once a fix is released.

In scope: the scripts in `scripts/` (validator, installer, eval runner), the CI workflow, and any skill text that could lead an agent to leak, collect, or mishandle personal data. Findings about a third-party agent runtime belong with that vendor.

## Data in journey artifacts

Journey artifacts may contain sensitive customer, employee, operational, or behavioral data.

Do not commit:

- raw interview recordings or transcripts with personal data;
- credentials or API keys;
- internal system identifiers that create security exposure;
- health, payroll, disciplinary, or other sensitive employee data without appropriate controls;
- customer account data or directly identifying behavioral histories.

Use anonymized or synthetic examples for public contributions. Evidence registers cite sources by reference (`source_reference`); they should never embed the personal data itself.

For private deployments, apply the organization's data-classification, retention, access-control, and research-consent policies before using AI agents with source material.
