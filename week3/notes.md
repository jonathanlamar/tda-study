# Week 3: Basic Homotopy Theory

## Homotopies

A homotopy is a continuous deformation between two functions who share the same
source and target. However, we often talk of spaces as being
homotopy-equivalent. This is because the modding out of maps induces a quotient
of categories, which identifies morphisms by homotopy. This also identifies
spaces because isomorphism in the homotopy category is a weaker condition than
isomorphism in Top.

In the words of a former classmate of mine: This is a great definition if you
never want to do anything with it. So we have to do a bunch of difficult math
instead.

So how do we reason about homotopy-equivalent spaces? It's a hard problem, so
there is no general program. However, if your space is a CW-complex (which I am
not presently defining), then one possible way to proceed is as follows.

1. Get rid of any nullhomotopic bloat (mod out, retract, etc.). Sometimes expand
   points to add bloat where needed... It really depends on what you need to do.
2. Realize your space as homotopy-equivalent to some algebraic/categorical
   construction whose component pieces are simpler complexes.
3. Look up the homotopy groups of those spaces (usually cofinitely trivial).
4. Use gluing results like Siefert-Van Kampen to compute the homotopy groups of
   the larger space.
5. Since your space is a CW-complex, homotopy groups determine the space up to
   homotopy equivalence. (Whitehead, 1949).

### Products of paths respect homotopy classes

If $X$ is a space, a _path_ in $X$ is a map $f:I\to X$. There is a natural way
of concatenating paths. Turns out, this respects the homotopy classes of the
factors. I.e., if $f_1$ and $f_2$ are paths from $x_1$ to $x_2$, $g_1$ and $g_2$
are paths from $x_2$ to $x_3$, and $f_1\sim f_2$ and $g_1\sim g_2$, then

$$
[f_1\ast g_1] = [f_2\ast g_1] = [f_1\ast g_2] = [f_2\ast g_2]
\text{ "=" } [f_1]\ast[g_1],
$$

where $[f]$ denotes the homotopy class of the path $f$.

### Pointed spaces and homotopy of loops

Paths have a tendency to wander. By this, what I mean is that products of paths
is really a groupoid operation - every concatenation sends you to a new node in
the groupoid. But we want to do _group_ theory, which means we need to fix a
point and study _loops_, i.e., paths that start and end from this point.

This is where pointed spaces come in handy. A pointed space is simply a
topological space with a "distinguished point". Maps between pointed spaces $(X,
x)$ and $(Y, y)$ are simply continuous functions with the added condition that
base points are mapped to each other. If we study loops from the base point,
then this framework is helpful for talking about pre/post-composition with maps
between pointed spaces (which yields the morphism component of the homotopy
functor. For most of algebraic topology, we are actually implicitly working
with pointed spaces and pointed maps.

## Algebraic Constructions

### Quotient Topology

This requires a bit of a setup. Suppose we have a surjection $q:X\to Y$, where
$X$ is a topological space and $Y$ is any _set_. Note that even ignoring
continuity, the preimages of points of $Y$ form a partition of $X$. Let
$X^\ast$ be the set consisting of the parts of this partition, and let $p:X\to
X^\ast$ be the map that takes a point to its equivalence class. Let
$f:X^\ast\to Y$ be the function which takes an equivalence class $[x]$ to
$q(x)$. Then by definition of the partition forming $X^\ast$, $f$ is
well-defined. It is also a bijection, so as sets, we can generally identify the
image of any surjection with the set $X^\ast$ defined in this construction.
This is to say, that any surjection can be represented by some identification of
points under an equivalence relation.

There is a natural topology on $X^\ast$ which can be defined as the _finest_
topology that makes $p$ continuous. This is defined by allowing the open sets
to be any set whose pre-image under $p$ is open.

Similarly, we can define the analogous topology on $Y$. Both of these
topologies are referred to as _the quotient topology_. Note that the quotient
topology endows $p$ (also $q$) with the property of being an _open map_.

### Attaching Spaces

Let $X$ and $Y$ be (pointed) topological spaces, $A \subset X$ a closed subset
(containing the base point), and $f : A \to Y$ a continuous (pointed) map. The
_attaching space_ $Y \cup_f X$ is defined as the following quotient:

$$
Y \cup_f X = X \sqcup Y / \sim,
$$

where $\sim$ is the equivalence relation defined by identifying $a\in A$ with
$f(a)\in Y$.

This can also be defined categorically as the _fibered coproduct_ of $X$ and $Y$
over $A$, with the maps $f:A\to X$ and $i:A\hookrightarrow X$.

### Mapping Cylinders and Mapping Cones

Let $X$ and $Y$ be pointed topological spaces and let $f:X\to Y$. Include $X$
into $X\times I$ via the map $\iota:x\mapsto (x, 0)$. Then the _mapping
cylinder_ of $f$, denoted $M_f$, is the attaching space

$$
M_f = Y \cup_f (X\times I).
$$

#### Mapping Cones

If $X$ is any space, we can construct the _cone over $X$_ (not to be confused
with the cone over a diagram) as the quotient space

$$
CX = (X\times I) / \sim,
$$

where $\sim$ identifies all points of the form $(x, 1)$. Now suppose $f:X\to
Y$. Then we can define the _mapping cone_ (also called _homotopy cofiber_) of
$f$ as

$$
C_f = Y\cup_f CX.
$$

### An example of homotopy equivalent spaces: Deformation retractions

Intuitively speaking, spaces are homotopy equivalent if they can be squished
continuously to the same space in a hole-preserving way. This is more general
than homeomorphism, because it allows for taking quotients of contractibe spaces
(assuming our space is a CW-complex, which it will always be).

An example of a homotopy equivalence is a _deformation retraction_. Consider
the letters example from Chapter 0 of Hatcher. We identify the fat and skinny
versions of the letters as having the same shape. But how?

Let $X$ be a space and let $A$ be a subspace. A _deformation retraction_ of $X$
onto $A$ is a homotopy $H:X\times I\to X$ such that $H_0 = \text{id}_X$ and
$H_1\vert_A = \text{id}_A$.

From the letters example, you can see the deformation in action by realizing the
retraction of a fat letter (say "B") onto its skeleton as a mapping cylinder,
where $X$ is the outer boundary of the fat letter, $Y$ is the skeleton, and the
map $f:X\to Y$ defining $M_f$ is the map that projects a point on the outer
boundary perpendicularly to its image on the skeleton.

**Theorem:** Two spaces X and Y are homotopy equivalent if and only if there
exists a third space Z containing both X and Y as deformation retracts.

_Proof:_ For the less trivial implication one can in fact take $Z$ to be the
mapping cylinder of any homotopy equivalence between $X$ and $Y$ as above.

## CW Complexes

TODO
