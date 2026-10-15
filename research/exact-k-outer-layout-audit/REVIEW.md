# Applicability review: exact-K outer layout and complete layer fields

**Result.** The positional layout in PR2298 section 3 meets the geometric
complete-field entrance of PR2287 section 1, conditional on the admitted
complete interchange and normalized-layer contracts. This is an independent
written applicability audit of an existing construction. It is not a new layout
theorem, a new finite census, or a verification of those callee contracts.

Reviewed pins:

- repository base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`;
- PR2298 `8507498d363735ced0b0a3f02d5ecf80ed3e3805`, section 3;
- PR2287 `8c60765b5dea9d862b3b190d55da102a576031bf`, section 1;
- PR2234 `d047ef86fbc5b1614d3d8e2b8d3441413beab73f`, complete ordinary
  interchange contract;
- `upstream/build/sections/06-transforms.tex`, blob
  `de073e9292d58573f7065a3cd4f214e0d05f3444`, especially
  `lem:synthetic-transform-cost` and its named-slot convention;
- `upstream/build/sections/02-streams.tex`, complete-stream semantics and
  `lem:elementary-streams`.

The source06 proof already gives the layout, its complete Cartesian field
decomposition, the descriptor bound and the cost. Philipp (@mightyOil)'s
[`synthetic-layout-independent`](../synthetic-layout-independent/README.md)
already independently checks these positional operations and their exact
transform semantics on a stated finite domain (merged PR879, head
`12012c9478d121d6d404a0d94e446016e3f51a2e`). Its published coverage includes
9,486 layouts, 93,868 Cartesian rounds and 200,434 complete addresses. Those
numbers describe its retained evidence; this review does not recreate that
census or enlarge its domain. PR2298 explicitly credits and imports its model.
PR2413's compact endpoint-exchange controls are additional predecessor evidence,
not an all-parameter proof of stream cost.

## 1. Precisely covered all-parameter domain

Let `d >= 2`, `D=d-1`, `ell >= 2`, and `1 <= K <= ell-1` be integers. For
`i=1,...,D`, let `delta_i` be either 0 or 1 and put

```
a_i = ell-1+delta_i,   t_i = 2^a_i,
m = sum_i delta_i,    N = sum_i a_i = D(ell-1)+m,
b = (ell-1) mod K,   q = floor((ell-1)/K),
z = m+Db,            N = z+DqK.
```

Thus `q>=1`. Name each original record-address bit `(i,h)`, where
`0<=h<a_i`, and initially order bits by increasing `i` and decreasing `h`.
Every assignment to these `N` bits occurs. Each address has the same contiguous
payload suffix, with arbitrary contents. For the polynomial application this
suffix is `r=2^ell` coefficients, each stored as two components of `w` bits.

The geometric assertion below has no hypothesis on payload values or
correlations. The separate arithmetic call requires the disk, p-grid, precision,
guard/restoration and dimension hypotheses of the layer. In particular, this
review assumes rather than proves PR2298's extension of PR2287 from
`d=floor(p^(997/1000))` to `d=floor(p^(1/40))`.

## 2. A direct coordinate proof of the positional permutation

The prefix has exactly these `z` slots, in this order:

1. `(i,ell-1)` for the long axes, in increasing `i`;
2. `(i,h)` for `h=b-1,...,0`, and within each `h` increasing `i`.

Remove those slots while preserving the relative order of every other slot.
Every axis then has exactly the common levels `ell-2,...,b`, partitioned into
`q` width-`K` chunks. Chunk `j`, numbered from high to low, contains

```
(i, ell-2-(j-1)K), ..., (i, ell-1-jK),    1 <= j <= q.
```

The remaining transpose puts these chunks in order `(j,i)`: all `D` axes in
chunk group 1, then all `D` in group 2, and so on. For a direct description
independent of the movement schedule, the zero-based physical index of a slot
after this permutation is:

```
h = ell-1:  #{k<i : delta_k=1};
h < b:     m + (b-1-h)D + (i-1);
b<=h<=ell-2:
  j = 1 + floor((ell-2-h)/K),  rho = (h-b) mod K,
  index(i,h) = z + (j-1)DK + (i-1)K + (K-1-rho).
```

These cases partition the original slot set. The first two biject onto the
prefix positions `0,...,z-1`; the last bijects onto `z,...,N-1`. Hence this is
a permutation of all `N` record-address coordinates. Extend it by the identity
on every suffix coordinate. For any full address `x` and payload coordinate
`u`, its boundary map is

```
(x,u) -> (Lx,u),       A_after(Lx,u) = A_before(x,u).
```

This proves preservation for arbitrary payloads, including independently dirty
or correlated values. No zero initialization, padding assumption, erasure of
input data, or unused input coordinate is involved. Reversing the complete
positional operations gives `L^-1` on this same domain. Work restoration and
head return are inherited requirements of each admitted complete operation;
the coordinate identity alone does not prove their physical implementation.

## 3. Complete fields and the exact logical-volume invoice

Fix a common named level `b<=h<=ell-2` and its `j,rho` above. Set

```
n_P = z + (j-1)DK,     n_S = (q-j)DK,
P = 2^n_P,            S = 2^n_S.
```

The `D` chunks in group `j` are consecutive. In each chunk its selected bit
is exactly bit `rho`, counted from the least significant end. The source's
`ell=6,K=2` illustration therefore selects offset 1 at `h=4`, despite that
slot being first when the chunk is written most significant bit first.

Because `L` is a permutation of the full binary address cube, not a projection
or a list of a subset of records, its full entrance address set is exactly

```
[P] x [2^K]^D x [S],
n_P+DK+n_S = N,       P S 2^(DK) = 2^N = M.
```

This includes every combination of the unselected bits within the selected
chunks and every preceding/following field. A zero-length prefix or suffix
means the singleton range `[1]`, not a missing or empty array. The entire
coefficient suffix is still contiguous, in its original order. All calls
operate on the complete stream. They cannot charge only the `D` selected bits
or one selected `2^D` fibre.

At actual component width `w`, every routing or layer call on this stream has

```
V(w) = 2 w r M = 2 w r P S 2^(DK) = 2 w T,   T=rM.
```

The same formula applies independently at each inverse call's actual width.
When an intermediate width is `w'`, its invoice is `V(w')`, even if its
coordinates coincide with the entrance coordinates. If `w,w'=Theta(p)` with
uniform fixed comparison constants, both are `Theta(Tp)`. Temporary copies
and scratch are charged in work; they are not silently added to this logical
volume or omitted from the callee's tariff.

The passed self-delimiting layer header is the existing source05 header

```
Gamma(p) Gamma(d) Gamma(r) Gamma(D) Gamma(P) Gamma(S)
Gamma(K) Gamma(rho+1) Gamma(w).
```

Here `Gamma(v)` has `2 floor(log2 v)+1` bits for `v>=1`. Under the source's
`d ell <= C_ell p`, `p+2<=w<=C_w p` and fixed parameter hypotheses, this is
`O(p)` uniformly in the mask and round, since
`ell+n_P+n_S<=d ell`. The separate table locating all named slots has
`O(N log(N+1))` bits and need not fit in the call header. Its polynomial
construction and traversal costs require the admitted long-record condition
`r=2^Theta(p/d)` and `d=Theta(p^epsilon)`, `epsilon<1`, for absorption. The
finite permutation argument alone supplies no such time bound.

## 4. Named levels, literal calls and costs

The common stage order is `h=ell-2,...,b`. It follows the optional top round
`h=ell-1` on the `m` long axes and precedes the bottom rounds
`h=b-1,...,0`. The opposite schedule reverses that order. At common level
`h`, every axis's recursive length is `2^(h+1)`. Its newly written branch bit
has frequency significance `a_i-1-h`, which may differ between long and short
axes without changing this shared pairing rule.

In particular, the original lower slots used for the twiddle are the named
slots `v<h`. Some now lie in the prefix, physically above the selected group.
Reading the low physical address bits would not implement the source's
`k_i=sum_(v<h) 2^v x_(i,v)`. The existing independent check already has an
explicit defect control for this error.

For a single traversal, a conservative complete-call invoice is:

| Operation | Count bound | Logical volume per call |
| --- | --- | --- |
| Prefix extraction, or its inverse | `z=m+Db <= DK` single-bit moves | actual `V(w)` |
| Width-K chunk transposition, or its inverse | `c<=Dq-1` completed exchanges | actual `V(w)` |
| Common normalized layer | exactly `qK` complete calls | actual `V(w)` |
| Elementary prefix-axis H0 factors | exactly `z` factors, each with its temporary move and inverse | actual intermediate `V(w')` |
| Combined monomial rounds | `qK+b+1_(m>0) <= ell` | actual `V(w')` |

An optional identity move or already-correct chunk position may be omitted;
the bounds do not require an unnecessary call. The opposite procedure pays
its full reversed layout. Two forward transforms and one opposite transform
in a convolution multiply these bounds by three; sharing the retained `L B`
frequency order does not remove the opposite's `L^-1` charge.

Assume the ordinary complete exchange costs `O(V K^tau)`, the complete
normalized layer costs `O(V d^lambdaPrime)`, and elementary moves/scans cost
`O(V)`, all including cleanup and head return. Since `DqK<=D ell=O(p)`,
one procedure then has the already published bound

```
O(Tp [dK + p K^(tau-1) + ell d^lambdaPrime]).
```

This audit verifies which calls and volumes that conditional expression
counts. It does not establish the sublinear exchange tariff or recursive
layer tariff from an indexed Python permutation.

For the changed dimension exponent, PR2298 gives
`epsilon=1/40`, `c=1/500`, and the compatibility gaps
`1-epsilon(1+c)=19499/20000`, `1-epsilon=39/40`,
`epsilon*c=1/20000`. Their role here is solely to state the admitted
dimension/long-record hypotheses. Proving the extension, numerical bounds,
fixed cutoffs, and complete callee construction remains separate work.

## 5. Nonadjacent endpoint exchanges

Let `P` and `S` be arbitrary complete preceding and following fields, `G` an
arbitrary complete intervening field, and `x,y` width-`E` bit fields. Let `e`
be one extra bit. On all assignments, with the entire payload suffix carried
unchanged, the two unequal-width cases are

```
P e x G y S -> P e y G x S -> P y G e x S,
P x G e y S -> P e x G y S -> P e y G x S.
```

The first line uses the equal-width `x,y` exchange then moves `e` rightward
across `y G`. The second moves `e` leftward across `x G` then uses the same
equal-width exchange. In each case the endpoint fields have been swapped,
`G` is again between them with its own order and values preserved, and `P,S`
and the payload retain their values. The intermediate callee always sees
complete fields; no value-dependent slice or sparse fibre is passed.

Thus each unequal endpoint exchange costs one completed width-`E`
interchange plus one elementary bit move on the full actual volume. Equal
widths use one interchange at that width. Empty `G` is a singleton range.
The source application has `E=ell-1>=1`; if one admits the explicit width-zero
identity contract, the formulas also cover `E=0` with only the bit move.

Consequently an axis reversal uses at most `floor(d/2)` endpoint exchanges;
exposing each noninnermost Gaussian axis and restoring it uses at most
`2(d-1)`. Under the stated callee tariffs, these have costs
`O(V d(1+ell^tau))`, with every inverse evaluated at its actual payload
width. The final coordinate identity is an all-parameter proof. Its physical
time and scratch conclusions are conditional on the complete elementary and
interchange contracts.

## 6. Conclusion and remaining obligations

No missing positional hypothesis or counterexample was found in this scope.
The complete synthetic layout needed by PR2298 is already proved in source06
and independently exercised by the retained package. The pending integration
gate is the validity and uniformity of the invoked callee and elementary
stream contracts, together with the separate dimension/precision conditions;
it is not a missing Cartesian decomposition of these round addresses.

This review does not certify numerical error propagation, prime-box or Gaussian
domain inequalities, the tensor common-label theorem, either full recursive
callee, fixed-tape transition tables, or the final multiplication theorem.
It is an all-parameter written argument about address permutations and a
conditional cost invoice, not a formal-kernel proof or independent human peer
review. Prepared by the recursive-interfaces specialist through OpenAI Codex;
the layout, transforms and prior finite verification retain their original
source and contributor attribution. New review prose is Apache-2.0.
