# Security

## Trust boundary

The shipped CLI reads local HTML and JSON fixtures. It makes no network request and stores no credentials. The package includes no phone-provider client, lead database, campaign workflow, or background task.

`validate_public_url` rejects embedded credentials, non-HTTP schemes, unresolved hosts, and any DNS answer that is not globally routable. It does not open a connection. Do not treat a validation result as protection against DNS rebinding in a separate client.

## Sensitive data

Use synthetic data in issues and tests. Phone-intelligence payloads and prospect lists may contain personal data even when they do not contain secrets. Keep generated exports outside the repository and apply your own retention policy.

## Reporting

Report security issues privately to the repository owner. Include a minimal synthetic reproduction and avoid sending live contact data.
