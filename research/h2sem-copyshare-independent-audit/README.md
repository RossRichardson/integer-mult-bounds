# Independent PR1805 invoice audit and verifier repair

**The finite invoice is corroborated; one negative control is ineffective.**
This audits Wentao Li's [PR1805](https://github.com/CrocSwap/integer-mult-bounds/pull/1805)
at `b34e0620bd92af49c9095e0eeb885f601fffd137`. The construction, savings and
semantic-D interface belong to its predecessors. This package adds independent
reconstruction, a reproducible verification defect, and a tested repair proposal.
It makes no new kappa or supplier-adoption claim.

## Independently corroborated finite claims

| Word | Complete ADDs | D ADDs | Forward F | Reverse B | Local / nine-stage bits |
|---|---:|---:|---:|---:|---:|
| PR589 baseline | 24,305 | 18,085 | 49,347 | 1,113,070 | 93 / 177 |
| Single 277→434 wrap | 24,240 | 18,020 | 50,535 | 1,113,070 | 94 / 177 |
| Seed42, 205 disjoint wraps | 18,074 | 11,854 | 75,381 | 1,196,402 | 95 / 180 |

All three words have the same D/A boundary and complete forward/reverse
arbitrary-dirty F2 map. Each of the 661 input basis columns is executed
separately. The allocated COPY temporary is clean at entry and erased at exit;
arbitrary dirt refers to the 661 original registers. They retain every ordered register frame path, nine rank7 COPYs
and nine ERASEs. The profile is `{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`,
rank mass5129. The exact positive integers satisfy both strict inequalities
`64 F^3 B^2 < 2^104` and `2^18 F^5 B^4 < 2^192`; RESULT.json records their
positive slacks. Fewer ADDs do not improve this unchanged recursive profile.

`audit.py` imports no predecessor mathematics. It derives the pair scores from
helper-incidence bitsets: `2 |I_a intersect I_b| - |I_a| - 2`. The retained
Random(42) tie rule then reconstructs the same matching. Exact integer row
elimination computes rational frame ranks, and a separate literal interpreter
executes individual input columns and positive envelopes. The four semantic
controls expose a missing single restoration, a missing two-pair restoration,
premature restoration and a missing body source. The matching and receipt are
stored; neither supplies the computed answer. This is code independence from
PR1805, not independent human review.

## Reproduced verifier findings

1. **The two-pair restoration control reports success if its detector is removed.**
   Original `verify.py` lines300–304 call `semantic_n`, then raise
   `ValueError("partial matching unrestored accepted")` on unexpected acceptance.
   The same `except ValueError` catches that failure assertion and records the
   control as rejected. Replacing only line301 with `pass` leaves the complete
   verifier passing, with the unchanged certificate and `controls=7`, normally
   and under `-O`. All original `test_package.py` tests also pass on this mutant.
   Other candidate and mutation checks still execute. The unmodified semantic
   detector does reject the malformed word: this finding concerns regression
   sensitivity, not an invalid accepted construction.
2. **The default verification entrypoint recreates a missing certificate.**
   At lines443–448, absence of CERTIFICATE.json selects generation and still
   prints PASS. Removing that file in an isolated copy recreates its exact
   original bytes. Thus a successful default invocation alone does not prove
   comparison against a pre-existing committed certificate. This is an
   acceptance-mode observation, not a counterexample to the computed invoice.

`reproduce_controls.py` preserves the original source and exercises these
behaviors in disposable minimal exports. It intentionally runs predecessor code
to test its control flow; that part is not presented as independent mathematics.

## Concrete repair, not yet applied upstream

[repair.patch](repair.patch) is against the exact PR1805 head. It moves the
unexpected-acceptance error into `try/except/else`, checks the intended rejection
reason, and requires a pre-existing certificate unless explicit `--write` is
requested. The patch does not change candidate generation, mathematical
predicates, numerical receipts or source pins.

The repaired positive replay matches the original certificate byte-for-byte.
The same removed-detector mutant now fails both normally and under `-O`.
Missing-certificate verification fails without writing; explicit `--write`
recreates the identical receipt. CONTROL-RESULT.json records these outcomes.
The repaired source exists only in temporary test exports; no predecessor file
or upstream branch was edited.

## Reproduce

Python3.12, standard library only, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/h2sem-copyshare-independent-audit
```

Expected markers: `PASS_COPYSHARE_INDEPENDENT_AUDIT`,
`PASS_COPYSHARE_CONTROL_AUDIT`, `PASS_COPYSHARE_AUDIT_PACKAGE_CONTROLS`, and
`PASS_REGISTERED_RESEARCH_PACKAGE`. Normal audit verification is read-only;
the upstream mutation experiments write only disposable temporary exports.
Own-package tests include optimized read-only relocation and five actual
corruptions: changed bill, integer substituted for Boolean, missing receipt,
altered source bytes and missing source inventory entry. `--write` on the two
audit scripts explicitly regenerates their respective receipts.

The exact sources, Git blobs and hashes are in SOURCES.json and PINS.json.
The original PR1805 files are retained unchanged in inputs/pr1805; the selected
record and catalogue copies used for its historical replay are in inputs/context.
The generic launcher resolves historical provenance using Git; direct audit
commands also work in minimal source exports without Git history.

## Limits and task provenance

This is finite invoice/boundary corroboration and verifier testing. It does not
re-prove the full E8 geometry, raw U/J/C interface or the chronological theorem;
the original pinned checker is run unchanged as an additional positive control.
The semantic bridge remains credited to PR1194/1782. Native C++/Boost,
physical hosting, all-size/compiler realization, precision/tape, recovery and
outer analytic transfer are unrun or inherited. No full selected cold replay,
Lean proof, independent human review or hosted-CI success is claimed.

Main base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; chooser nonce
`d3ae39b751060009ee5b1c99986efcb7`; priority revision3; original card
`bit-helper-contract`, scope key `bfb61f829a81535adeae`. Scope is explicitly
**changed** to an independent audit because PR1194/1311/1782 and PR1805 already
cover the original bridge and invoice questions. The bit side is nonbinding;
this contribution does not claim the original new-construction acceptance gate.
TASK.json and TASK-CARD.md preserve scope, overlap and the bounded stop rule.

## Open next questions

Will PR1805 adopt the repair and the two regression cases? It matters because
the present suite cannot detect this omitted check and conflates replay with
receipt creation. First apply the patch on the pinned PR head, add the two
mutation cases to that package's tests, and rerun its registered replay. The
blocker is contributor review and adoption; no new mathematical search is needed
for this finding. The structured question is in TASK.json. Broader matching,
physical admission and supplier work remain predecessor questions, not claims
of this audit.

## Credit and license

Prepared for **Ross Richardson** with substantial **OpenAI Codex assistance**
in implementation, analysis, checks and writing. One assisted author; no
subagents. New code and writing are Apache-2.0.

Credit **Wentao Li / VictorLiwentao, PR1805** for the priced construction;
**Aaron Wang / navinor, PR848 and PR1782** for the pair census, wrap and semantic
admission; **woklerx / PR1194** for the substitution contract; **Arham Tahir /
PR1311** for the related bridge application; **DreamingOfClouds / PR589**,
**eumemic / PR555**, **Zhihao Chen / PR425** and the retained checker/supplier
lineage. The unrelated PR1062 B/star replay was the catalogue's entry control,
credited to Sagar Thakrar and its original contributors. Frozen copied sources
retain their original notices and the repository's Apache-2.0 license.
