# Selected diagonal batches: source-bound corroboration of PR679

**Independent application of an existing obstruction; no new theorem or κ.** Sixteen independent
rank-one climbs are not one retained rank-sixteen child surrounded only by
invertible monomial adapters. The obstruction already occurs for two climbs:
their direct sum has two nonzeros per row, whereas the rank-two child has four.
Arbitrary permutations, nonzero diagonal factors, and independent dirty
spectators do not fix that mismatch.

**Prior result found during the final overlap review:** Greer Guthrie's
[PR679](https://github.com/CrocSwap/integer-mult-bounds/pull/679), head
`dce137e540acd2b689281afe222cd32c0ec1f1ae`, already proves this monomial-support
obstruction and prices the correct selector repair in
[selector-batching](../selector-batching/README.md). Its package replay passes
again on Python 3.12. This session supplies a separate check of its application
to the exact PR1094 batches now used in PR1779/PR1817. A finding on their live
handoff, with this reproducible fork artifact, is the contribution; no duplicate
theorem PR is requested. The local README search exposed this merged predecessor.

This audits the missing `RecipesExact` implication in the package from
[PR1779](https://github.com/CrocSwap/integer-mult-bounds/pull/1779), at
`1e3128bf642bbaf250b7d6b9639b2bb24b98ce5e`, and the explicit physical-contract
handoff in Josie Elliston's
[PR1817](https://github.com/CrocSwap/integer-mult-bounds/pull/1817), at
`ac3a759e874e8e526bc884fc2cb8eb114695b063`.
It leaves their chronological counts and hypothetical profile arithmetic intact.
It does **not** show that batching is impossible or that sixteen separate calls
are necessary. Nonmonomial gather/decode work, restricted encoded inputs, or a
different primitive are outside this theorem and need a new full cost model.

## The actual child and the missing implication

The retained local register is an arbitrary vector in `C^(2^9)`; a register
file is a direct product of such vector spaces. `Event.phys` applies a relabel
to one register. `RecipesExact` requires that relabel to equal `T_B T_A^-1`
on **every** vector. See the pinned
[Lemma G statement](../e8-lemma-g-lean/PROOF.md) §1 and H2, and
[formal definition](../e8-lemma-g-lean/LemmaG/Stream.lean).

The pinned compiler's `lower_child` represents a rank-r child as

`L (C_[r] tensor I) R`, where `C_[r] = C^tensor r`,

```text
C = 1/2 [[1+i, 1-i],
         [1-i, 1+i]].
```

`L` and `R` are serialized invertible monomials: coordinate permutations,
quadratic/linear phases, translations and a global phase. This is a fixed
linear operator. Its rank parameter counts coordinate axes in the Fourier
factor; it is neither its full matrix rank nor the number of independent
registers. The convention and lowering are pinned in
[clifford_exact.py](../complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py).

PR1779's `check_diagonal_identity` verifies the true matrix-multiplication
identity `diag(X_i) diag(Y_i) = diag(X_i Y_i)`. Its identity test never reads
`CLIFFORD-RECIPES.json`. That identity does not identify matrix multiplication
on diagonal blocks with the retained `C_[16]` operator. On independent
registers, executing all sixteen climbs is `diag(U_1,...,U_16)`, where each
`U_i` is a rank-one recipe; it is a **direct sum**, not `tensor_i U_i`.
Passing the unchanged local checker after merely reordering the original
climbs, as PR1817 does, verifies that reorder. It does not verify a replacement
child that the stream never executes.

## Existing support proof applied to this boundary

For a matrix A define `s_A(j)` to be the number of nonzero entries in row j.
Right multiplication by an invertible monomial permutes and rescales the
columns, so each row's support size is unchanged. Left multiplication permutes
and rescales rows, so the **multiset** of row support sizes is unchanged.
This holds for arbitrary nonzero complex scales and arbitrary permutations,
a larger class than the selected affine/quadratic adapters.

Every entry of C is nonzero. Consequently every row of `C_[r]` has exactly
`2^r` nonzeros; tensoring with any identity leaves that count unchanged.
Thus every row of a rank-one recipe has two nonzeros. Any nonempty direct sum
of these recipes has a required output row of support two, regardless of the
individual frames or the number of registers.

Now allow an arbitrary finite common coordinate space containing all payload
and independent dirty workspace. One rank-r child may act on any coordinate
block, with an identity on all other coordinates. Each row of that operation
has support either `2^r` or one. Surround it by arbitrary invertible monomial
maps of the **entire** space. Those are still its only possible row support
sizes. For `r>=2`, neither is two, so no required payload row can agree with the
direct-sum target. This also holds if workspace outputs may be arbitrary
garbage, or outputs are selected by coordinate: a required payload row still
cannot have support two. It does not allow free linear combinations when
decoding outputs or restrict inputs to a correlated subspace.

This proves the one-child obstruction. It does not price a general adapter
or exclude several children separated by mixing operations.

The smallest equal-dimension counterexample is exact. On `e_0`:

```text
(C direct-sum C)e_0 = ((1+i)/2, (1-i)/2, 0, 0)
(C tensor C)e_0     = (i/2,       1/2,     1/2, -i/2).
```

Both maps fix the all-ones vector: testing only that correlated input would
miss the error. Conversely, `C direct-sum C` **is** `C` on one coordinate with
an extra selector coordinate left idle. This is a positive algebraic control,
not a cost saving: combining physical families into a wider selector layout
does not preserve the old width, normalization, hosting and invoice by fiat.
The oracle also constructs the nonmonomial adapter
`(C direct-sum C) (C tensor C)^*`; multiplying it by `C tensor C` gives the
target exactly. This demonstrates why the monomial restriction is material.

## The known paid repair does not improve this cost model

PR679 supplies the exact repair. For sixteen rank-one lanes it is

`(C_[4]^-1 tensor I_2) C_[5] = I_16 tensor C_[1]`,

with the eight local spectator axes unchanged. Both engines separately check
all 1,024 entries of this 32-coordinate active core. This uses a rank-five
child and a rank-four inverse selector on the joined volume.

PR679's inherited per-call upper-bound model is `A V d^sigma`, with
`0 < sigma < 1`. Let each of the sixteen original lanes have volume V and
active rank f, where f is the uniform scale parameter. The joined array has
volume `16V`, and the complete budget is

```text
original = 16 A V f^sigma
joined   = 16 A V [(f+4)^sigma + 4^sigma] + E,  E >= 0.
ratio with E=0 = (1+4/f)^sigma + (4/f)^sigma > 1.
```

Even granting the inverse selector and every additional operation for free,
the joined-child term alone is larger. At f=1 the ratio is
`5^sigma + 4^sigma`; as f grows the complete ratio tends to one from above.
Thus the leading fixed-lane budget ties asymptotically, and does not improve.
This compares inherited available upper-bound expressions, not lower bounds
on optimal execution time. Merely implementing the known selector repair or
gathering the same lanes cannot improve those expressions. A reopening must
change the cost/encoding/interface hypothesis. Credit for the identity, volume
charge and all-size argument belongs to PR679.

## Source-bound finite evidence

[CERTIFICATE.json](CERTIFICATE.json) binds the original eight contiguous
batches per orientation to the archived selected PR1094 provider:

| Check | Coverage |
|---|---:|
| Selected rank-one climbs recounted | 2,412 per orientation |
| Original batches, forward plus backward | 16, with 256 event occurrences |
| Distinct child recipes used in those batches | 64 |
| Exact Gaussian-dyadic recipe columns | 32,768 |
| Independently checked reverse-incidence rows | 32,768 |
| Row/column permutation pairs of the 4-by-4 counterexample | 576 |
| Credited sixteen-lane selector repair, exact matrix entries | 1,024 |

Every decoded selected recipe has two nonzeros in each row **and** column.
For example, zero-based event 17006 relabels register 456 from frame 855 to
frame 1. Its input coordinate zero produces `(1-i)/2` at coordinate 1 and
`(-1-i)/2` at coordinate 504, with all other coordinates zero. The two engines
derive these coefficients separately from the serialized recipe.

At the finite 9-axis local-core level, sixteen arrays have 8,192 coordinates,
while `C_[16]` already needs 65,536. Padding the former with independent dirty
identity spectators gives 8,192 rows of support two and 57,344 of support one;
`C_[16]` has 65,536 rows of support 65,536. These dimensions are a local-core
diagnostic, **not** a bound on the global 73-axis family storage. Adding those
global spectator coordinates does not change the support proof.

The registered checks include the positive selector and true tensor identities,
the nonmonomial escape, the all-ones blind spot, full tensor support for
`r=1..6`, six on-disk certificate corruptions rejected by **both** engines,
wrong-rank/duplicate-register/singular-adapter semantic mutants, a real source
byte corruption, and optimized read-only replay after relocation without Git.

```sh
python3.12 -I -B scripts/research_package.py --package research/diagonal-child-contract-audit
```

Expected markers: `PASS_DIAGONAL_CHILD_CONTRACT_AUDIT`,
`PASS_INDEPENDENT_DIAGONAL_CONTRACT_ORACLE`, then four passing test groups.
`verify.py --write /absolute/output.json` explicitly regenerates a receipt;
ordinary replay writes nothing. Both implementations use the standard library
and exact arithmetic. They are code-separated implementations by the same
assisted author, not independent human review.

The source archive, selected record, compiler convention, and Lemma G sources
are pinned in [SOURCES.json](SOURCES.json). Exact predecessor text/blob pins and
overlap coverage are in [PREDECESSORS.json](PREDECESSORS.json). The assignment,
scope refinement and stopping rule are in [TASK.json](TASK.json).

**Not checked:** a changed physical batching implementation; nonmonomial
adapter cost; input encoding or reachable-subspace invariants; altered
coverage/width/W; all-size, hosting, precision/tape and analytic transfer;
global validity of PR1817's reorder; full selected cold replay; Lean proof or
human review. This checker decodes the pinned recipes and their support; it
does not re-prove every recipe equals `T_B T_A^-1` (the distinct PR1781 audit
addresses that). The selected certificate and all frozen sources are unchanged.

## Open next questions

1. **Can a changed interface or cost model improve the direct-sum budget?**
   Start with two explicit selected recipes on independent dirty arrays and
   list every gather, child, decode and restoration operation. Name the exact
   PR679 hypothesis that changes, then supply the new complete invoice and
   coverage law. The blocker is a costed replacement interface; the monomial
   and volume-weighted selector routes are already settled in scope.
2. **Can a reachable encoded subspace change that conclusion?** First exhibit
   and prove such a subspace at one actual caller cut, including arbitrary
   permitted initial helper values. Then charge its preparation, decoding and
   restoration and state a replacement for RecipesExact. No such invariant is
   established here; restricting test inputs does not prove it.

## Credit and scope of contribution

PR1779 supplied the diagonal proposal, original batch census and source pins.
Its package credits Jose Manuel (@jmbarrancoml); its GitHub submitter is Cinna
Davis (@1337isnot1337). Both attributions are retained. Josie Elliston (#1817) found 134 batches under register commutation
and explicitly requested the physical-contract audit. Arham Tahir (#1605)
supplied the integer price screen; Douglas Colkitt (#1240) the ceiling model;
Sagar Thakrar (#1012) the coverage identity. DreamingOfClouds supplied the
retained exact Clifford compiler and Lemma G semantics. The selected supplier
credits remain Rohan Arun (#1094), Jeremy Kothe's k8/T16 lineage, Hao Yan's
controller, icekylinx's gauge44 lineage, and their retained predecessors.
Sagar Thakrar (#1781) is credited for the distinct full exact-recipe audit.

Greer Guthrie (#679) has priority for this repository's support obstruction,
selector circuit, dirty-padding repair and volume-cost diagnosis. No novelty
is claimed for those results or their elementary linear algebra. The added
value is a separate source-bound check and explicit application to the two live
proposals, preserving a precise statement of what remains missing.
Prepared by Ross Richardson with substantial OpenAI Codex assistance in
analysis, proof, code, tests and writing. No subagents. Apache-2.0.
