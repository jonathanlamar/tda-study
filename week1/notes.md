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

In calculus, we say continuous if small wiggles in the domain beget small
wiggles in the range. What is closeness but open sets though? So we can only
measure small wiggles via open sets. However, we can't look at forward images
like we do in calculus, since constant functions map open sets to a singleton
(which is not generally open). Thus, we have to measure preimages of open sets.
In fact we define continuity using preimages of open sets for this reason.
Since in calculus all functions are locally invertible, this is fine.

### Compactness

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

### Some Topologies as Universal Constructions

Absolute bare minimum category theory needed for this to make sense: A _cone_
over a diagram is an object that maps to every object in the diagram, in a way
such that all "triangles" commute. Keeping in mind that evrything in category
theory is a category, there is a category of cones over a diagram. Likewise,
there is a category of co-cones under a diagram (arrows generally move down and
to the right0. An object is _initial_ in a category if it has a unique map to
every other object. Likewise an object is _terminal_ if it accepts a unique map
from every other object.

The _limit_ of a diagram is the terminal co-cone (if it exists) over the
diagram, and the _colimit_ of the diagram is the initial co-cone onder the
diagram. The product is the limit over the factors, and the quotient is the
colimit of a surjection.

In the category of topological spaces, the limits of diagrams are always endowed
with the finest possible topology that allows the cone maps, and colimits are
always endowed with the coarsest possible maps that allow the co-cone maps to
exist. For a relatively straightforward illustration, note that all maps from
the discrete topology are continuous and all maps to the indiscrete topology are
continuous.

More generally, another explanation for why you should think of fine topologies
as "sitting to the left of" coarse topologies is that if a set $X$ is endowed
with two topologies $\mathcal{T}_1$ and $\mathcal{T}_2$, forming distinct
_topological spaces_ $X_1$ and $X_2$, then the identity map $X_1 \to X_2$ is
continuous if and only if $\mathcal{T}_1$ is finer than $\mathcal{T}_2$.

#### Product Topology

Ok, with that in mind, we can now see why the product topology is not the box
topology. By definition, the product topology is generated by the sub-basis
given by preimages of open sets under the projection maps, and this gives the
coarsest possible topology with these sets open (i.e., with the projection maps
continuous... Refer to the previous paragraph...).

However, the basis generated by this sub-basis is _not_ the set of all boxes.
Due to the finite intersection property of producing a basis from a sub-basis,
it is as originally defined.

Another remark is that it isn't trivial to a category theorist that the
underlying set should evn by the cartesian product. But the continuity of the
forgetful functor from Top to Set implies it.

Nice properties of product spaces:

1. Products of Hausdorff spaces are Housdorff.
2. Taking the product of the closures of subsets in the factors is equivalent to
   taking the closure of the product of those subsets.

#### Quotient Topology

This requires a bit of a setup. Suppose we have a surjection $q:X\to Y$, where
$X$ is a topological space and $Y$ is any _set_. Note that even ignoring
continuity, the preimages of points of $Y$ form a partition of $X$. Let
$X^\ast$ be the set consisting of the parts of this partition, and let $p:X\to
X^\ast$ be the map that takes a point to its equivalence class. Let
$f:X^\ast\to Y$ be the function which takes an equivalence class $[x]$ to
$q(x)$. Then by definition of the partition forming $X^\ast$, $f$ is
well-defined. It is also a bijection, so as sets, we can generally identify the
image of anyh bijection with the set $X^\ast$ defined in this construction.
This is to say, that any surjection can be represented by some identification of
points under an equivalence relation.

There is a natural topology on $X^\ast$ which can be defined as the _finest_
topology that makes $p$ continuous. This is defined by allowing the open sets
to be any set whose pre-image under $p$ is open.

Similarly, we can define the analogous topology on $Y$. Both of these
topologies are referred to as _the quotient topology_. Note that the quotient
topology endows $p$ (also $q$) with the property of being an _open map_.

## Chapter 3
