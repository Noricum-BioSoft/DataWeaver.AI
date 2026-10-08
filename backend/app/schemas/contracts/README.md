# Platform contract schemas (snapshot)

JSON Schemas of the shared Noricum platform contracts, exported from
`Helix.AI/backend/contracts/` via `python -m backend.contracts.schema_export`
and copied here. DataWeaver validates Context API request bodies against them
(Phase 6). Do not edit by hand; refresh by re-running the export in Helix and
copying `Helix.AI/shared/schemas/contracts/*.json` into this directory.

Source commit is recorded in the Helix worklog; a shared package replaces this
copy at Phase 7.
