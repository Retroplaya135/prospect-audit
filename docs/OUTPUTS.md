# Output semantics

The HTML command prints the supplied URL, status, elapsed time, HTML byte count, title, text length, boolean checks, findings, verdict, and score. HTTPS is inferred from the URL string; status and timing are supplied by the caller. HTML is inspected without rendering it.

HTTP errors yield an `unavailable` verdict and a score of zero. Placeholder-page markers yield `placeholder` and five. Other pages start at 100 and lose points for missing checks or slow supplied timing: `strong` is 80 or above, `review` is 60–79, and `weak` is below 60. This score is a review aid, not a conversion estimate.

Phone-line results preserve uncertainty:

- `resolved` means the payload contained line-type intelligence without a reported error. The type may still be `unknown`.
- `invalid` means the provider payload marked the number invalid. Invalid input numbers raise `ValueError` in the classifier; the row-enrichment helper converts that error into an `invalid` result.
- `provider_error` means the supplied response could not support a classification.
- `textable` is `yes`, `likely`, `no`, or `unknown`; callers should not collapse uncertainty.

These labels describe the supplied response. They do not establish deliverability or permission to contact the number.
