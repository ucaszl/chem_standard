# Canonical Stability Contract

## Scope

This document defines the stability guarantees of the canonical reaction identity.

## Canonical Scheme

- Scheme name: canonical
- Current version: v1

## Stability Guarantees

The following changes MUST NOT affect canonical_key in v1:
- Ordering of reactants or products
- Metadata fields (reaction_id, source, conditions, notes)
- Serialization order
- Whitespace or formatting differences

The following changes REQUIRE a version bump:
- Element normalization rules
- Stoichiometry handling
- Directionality rules
- Formula canonicalization logic

## Versioning Policy

- canonical:v1 keys are immutable once released
- Any breaking change requires canonical:v2
- v1 and v2 may coexist

## Rationale

Stable reaction identity is required for:
- Dataset deduplication
- Long-term model training
- Cross-system reaction alignment
