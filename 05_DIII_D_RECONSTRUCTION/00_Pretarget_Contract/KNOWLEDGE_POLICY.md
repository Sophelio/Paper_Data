# S7.2 — Scientific knowledge policy `H_rec`

How domain knowledge may enter the ontology, and where it may not.

## Allowed inputs

Signal meaning · units · diagnostic family · known physical type · known
algebraic definitions · documented provenance · known symmetries · known
dimensional constraints · known measurement/actuation roles · known sampling
limitations.

All of these are properties of the **observational object**, established in
S7.1, independent of any target and of any result.

## Allowed uses

Knowledge may:

- **admit or reject** a constructor (dimensional rules, semantic rules);
- **assign a type** to a coordinate;
- **identify a known dependency** for boundary closure;
- **prioritise a search family** — direct the order in which candidates are
  explored.

## Forbidden use

> **Knowledge may not count as validation evidence.**

That a coordinate is physically sensible is a reason to *construct* it. It is
never a reason to *believe* it. Utility is established only by the frozen
protocol in `UTILITY_AND_QUALIFICATION_POLICY.md` and
`VALIDATION_PROTOCOL.md`.

Prioritisation is a search-efficiency device. Because the search bound is
finite, prioritisation changes which candidates are *reached*, so S7.7 must
report the frontier explicitly — `NOT SEARCHED != INADMISSIBLE`.

---

## The seeding firewall

This is the most important part of this policy.

> **The historical q_desc seven-coordinate support may NOT seed q_rec.**
>
> **The retired q_rec support may NOT seed q_rec.**
>
> **The dFL target-conditioned export may NOT seed q_rec.**

None of the three may be used to:

- propose candidate coordinates;
- restrict the candidate space;
- initialise or warm-start a search;
- set a representation-size bound;
- choose a constructor family;
- break a tie between representations;
- select the target.

### Why each is firewalled

**q_desc's seven coordinates** were selected for a *different task contract*
against a different target. Importing them would smuggle a solved problem's
answer into an unsolved one and destroy the claim that the representation was
discovered under this contract.

**The retired q_rec support** was retired for two independent reasons — six of
ten features carried plasma-current ancestry, and a constant predictor beat it.
Reusing it would reintroduce exactly the failure this contract is built to
prevent.

**The dFL export** is *target-conditioned*: its directory is named for the
target it was built against (`pcdiamag3_none_…`). Its features are z-scored
derived coordinates, not primitive observations. Using them would import both a
target decision and a derived representation.

Relatedly and separately: **dFL-derived features may not be used as primitive
observations** anywhere in this study. O is the 95 archived quantities.

### When prior results may be mentioned

Only **after** the new ontology and search are frozen and hashed, and then only
as **historical context** in discussion. A prior result may never be cited as
evidence for a choice made in this study, and never appear in a decision made
before the freeze.

### The "10" trap

The retired model was called REL10. **The representation-size bound must not be
set to 10 because of that name.** `SEARCH_BOUND_POLICY.md` sets the range on
independent grounds, and the coincidence is recorded there explicitly so the
choice can be audited.

---

## Auditability

Every knowledge-derived decision records: the knowledge used, its S7.1 source,
whether it admitted / rejected / typed / prioritised, and confirmation that it
did not consult any result.

## Deferred

- **S7.5:** the instantiated constructor set and the knowledge justifying each.
- **S7.7:** the prioritisation actually applied, and the resulting frontier.
