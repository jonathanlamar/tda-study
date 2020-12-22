# Week 1: Basic Point-Set Topology

## Chapter 2

It took a really long time to settle on a definition of Topology, as well as a
definition for _a_ topology. To the first point, my grad Topology professor
said that Topology is best defined as _the intrinsic geometry of a space_. But
what is intrinsic, what is geometry, and what is a space?

I think intrinsic refers to the invariance of topology under distortions,
without which we would be doing analysis. Defining _space_ is also nontrivial,
which might explain why the axioms of a topology aren't the most intuitive.

Some guiding intuitions to keep in mind are:

1. Open sets encode the information of nearness and farness without a metric to
   measure distance, however open sets should always be thought of as analogues
   of open _intervals_ (discs, hyperspheres) in Euclidean space.
2. In particular, the interior of a set should be thought of in metric terms
   (even if the topology is not metrizable), i.e., that some "distance" around a
   given point is contained in the set.
3. Specifying a basis for a topology is the same thing for choosing what shape
   the neighborhoods of points will take. Therefore, it is easy to believe that
   two bases (sub-bases) generate the same topology if all elements of each
   contain elements of the other around any point.
4. Canonical topologies should always be thought of as universal constructions
   whenever possible (i.e., any good canonical topology should be able to be
   defined as either the finest or coarsest topology satisfying some
   relationship to other, related spaces).
5. Separability axioms specify how easy it is to distinguish points, which is
   related to nearness and farness, but encodes the _resolution_ of a topology
   in these terms. So a topology may contain many open sets (and therefore
   most points are "not close"), but there are counterexamples which fail even
   T1 separability and therefore are low resolution, at least around some
   points.

### Continuity

In calculus, we say a function is continuous if small wiggles in the domain
beget small wiggles in the range. What is closeness but open sets though? So we
can only measure small wiggles via open sets. However, we can't look at forward
images like we do in calculus, since constant functions map open sets to a
singleton (which is not generally open). Thus, we have to measure preimages of
open sets. In fact we define continuity using preimages of open sets for this
reason. Since in calculus all functions are locally invertible, this is fine.

High points:

1. Forward images of compact sets are compact.
2. Continuous functions commute with the closure operator.
3. For each $x\in X$ and each neighborhood $V$ of $f(x)$, there is a
   neighborhood $U$ of $x$ whose image is contained in $V$. This is most
   analogous to the analysis definition of continuity.

### Hausdorff spaces

Why is this important? Almost all "nice" topological spaces will be compactly
generated and Hausdorff.

Some features of Hausdorff spaces that do _not_ hold in general:

- Compact implies closed in a Hausdorff space.
- Continuous bijections are homeomorphisms (when restricted to compact subsets)
  in a Hausdorff space. This might be wrong..?
- Sequences converge to at most one limit.

## Chapter 3

### Connectedness

Mostly trivia. Pretty easy concept. Note the definition of path-connectedness.
This will be important in algebraic topology. Also the fact that there are
local versions of these definitions (locally connected, locally compact, etc.).
If not connected (path connected), can usually break up into disjoin union of
components that are.

### Compactness

Read the beginning paragraph for some history on the concept. The "official"
definition came later (after the "official" definition of a topological space).
But the concept was known by its nice properties.

Theorem: In a metrizable space, TFAE:

1. $X$ is compact
2. Every infinite subset of $X$ has a limit point in $X$.
3. Every sequence of points in $X$ has a convergent subsequence whose limit lies
   in $X$.

Theorem: A topological space $X$ is connected if and only if the functor
Hom($X$, $-$) preserves coproducts.

There are many reasons to prefer local properties. Here is one result along
those lines.

Theorem: In a locally path connected space, the path components and connected
components are the same.
