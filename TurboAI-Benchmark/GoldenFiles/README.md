# Golden Files

These files define the deterministic observable expectations for the TurboAI benchmark workload.

- `Input/`: valid or mixed CSV scenarios.
- `Invalid/`: fatal inputs that must not publish final JSON.
- `Expected/`: authoritative deterministic JSON.
- `manifest.json`: scenario mapping and expected exit codes.

Do not regenerate expected files automatically during normal test runs. Any golden update requires an explicit contract decision and semantic review.
