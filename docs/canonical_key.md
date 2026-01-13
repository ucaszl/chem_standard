# Canonical Key for Chemical Reactions

## 1. Problem Definition

In reaction datasets, the same chemical reaction can be represented in multiple
syntactically different forms:
- different molecule ordering
- different atom ordering
- different metadata or logging sources

A canonical representation is required to define **reaction equivalence**.

## 2. Definition of Reaction Equivalence

Two reactions are considered equivalent if:
1. They contain the same set of reactant molecules
2. They contain the same set of product molecules
3. Each molecule is equivalent up to atom permutation
4. Stoichiometry is preserved
5. Conditions and metadata do not affect chemical identity

## 3. Canonicalization Strategy

The canonical key is constructed by:
- canonicalizing each molecule into a deterministic atom-level representation
- sorting reactant molecules
- sorting product molecules
- concatenating reactants and products with directional markers
- hashing the resulting string

This ensures:
- order invariance
- permutation invariance
- deterministic equivalence

## 4. Practical Validation

Applying canonical_key to logged reactions shows:
- identical reactions converge to a single key
- no spurious splitting observed in test data
- stable behavior under repeated logging

## 5. Design Implications

The canonical_key defines the **reaction identity layer** of the system.
All downstream tasks (deduplication, statistics, learning) operate on this layer.
