# PR2298 exact-K caller applicability audit

**Independent written review; no positional defect found.** PR2298 section3's
synthetic layout meets PR2287 section1's complete-field geometry under the
stated complete-operation contracts. [REVIEW.md](REVIEW.md) gives the direct
coordinate proof, complete logical volume, header size and paid operation
invoice for every integer d>=2, ell>=2, 1<=K<=ell-1 and long/short-axis mask.
Arithmetic and eventual-parameter admission remain separate hypotheses.

The original construction, all-parameter layout proof and operation bounds
already appear in OpenAI's frozen source06. Philipp (@mightyOil)'s merged
[PR879](https://github.com/CrocSwap/integer-mult-bounds/pull/879) already supplies
independent finite geometry and transform checks. PR2298 explicitly imports
that unchanged model. This note resolves the applicability part of the current
review request; it does not add another layout implementation or census.

For each common round, with the notation of the review,

```
n_P=z+(j-1)DK, n_S=(q-j)DK,
P S 2^(DK)=2^N=M, V(w)=2wrM=2wT.
```

Every unselected address combination occurs and the polynomial suffix stays
contiguous. Every inverse is charged at its actual payload width. Assuming the
complete exchange and layer tariffs, the inherited full bound is
`O(Tp[dK+p K^(tau-1)+ell d^lambdaPrime])`. This is a written permutation
argument and conditional invoice, not a formal-kernel proof or tape simulation.

## Reproduction and evidence

At the pinned main base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`:

```sh
python3.12 -I -O -B research/synthetic-layout-independent/verify.py
python3.12 -I -O -B research/synthetic-layout-independent/test_verify.py
python3 -B scripts/verify_selected_result.py
```

The retained replay passes: 9,486 layouts, 93,868 Cartesian round groups,
200,434 complete addresses, 4,340 ring columns, 1,244 additional scalar columns
and 11 negative controls. All six test groups pass, including source/receipt
corruption and isolated relocation. These are existing finite coverage counts,
freshly replayed; they are not new enumeration or an all-parameter proof.
[EVIDENCE.json](EVIDENCE.json) records commands and scope; [SOURCES.json](SOURCES.json)
pins the exact source text, predecessor checker and PR dependency heads.

## Open next questions

The useful next review is the invoked complete-operation chain: assess PR2234's
uniform ordinary-interchange cost and PR2287's extended layer implementation,
including work restoration, proper-width recursion and actual physical
adapters. Begin with one source-bound composed child endpoint and its full
work/volume invoice. Geometric Cartesian coverage is available already;
repeating the same finite layout census does not discharge those callee claims.
Dimension/precision, Gaussian/prime domains and numerical recovery remain
outside this note. No new kappa, selected-frontier change, full cold replay,
hosted CI, formal-kernel or independent human verification is claimed.

Credit OpenAI's frozen source; Philipp's PR879 finite audit; Jose Manuel
(@jmbarrancoml)'s PR2234/2287/2298 composition; PR2413's compact exchange and
format audit; and the source's Nussbaumer–Quandalle, Harvey–van der Hoeven and
Douglas Colkitt lineage. Ross prepared this review with substantial OpenAI
Codex assistance, including a separately delegated recursive-interface audit.
New prose is Apache-2.0; upstream and predecessor evidence remain unchanged.
