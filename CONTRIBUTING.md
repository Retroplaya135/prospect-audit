# Contributing

Use synthetic HTML and phone-response fixtures, and keep tests independent of network access. Run:

```bash
python -m pip install .
python -m unittest discover -s tests -v
prospect-audit html tests/fixtures/sample_site.html --elapsed-ms 120
```

Do not commit contact lists or credentials. Keep campaign workflows and CRM writes outside this package, and preserve uncertainty in classification output.
