# Week 3: Basic Homotopy Theory

## Algebraic Constructions

## Quotient Topology

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

TODO: Left off here.

Similarly, we can define the _mapping cone_ (also called _homotopy cofiber_)

### An example of homotopy equivalent spaces: Deformation retractions

- Deformation retraction defined in terms of mapping cylinder
- A deformation retraction is a special case of a homotopy.

### Homotopies and the Homotopy category

Homotopies are continuous deformations of maps, but we often talk of spaces as
being homotopy-equivalent. This is because the modding out of maps induces a
quotient of categories, which identifies morphisms by homotopy. This also
identifies spaces because isomorphism in the homotopy category is a weaker
condition than isomorphism in Top.

#### Products of paths respect homotopy classes

There is a natural way of concatenating paths. Turns out, this respects the
homotopy classes of the factors. I.e., if $f_1$ and $f_2$ are paths from $x_1$
to $x_2$ and $g_1$ and $g_2$ are paths from $x_2$ to $x_3$. And moreover, if
$f_1\sim f_2$ and $g_1\sim g_2$, then

$$
[f_1\ast g_1] \sim [f_2\ast g_1] \ast [f_1\ast g_2] \ast [f_2\ast g_2]
\text{ "=" } [f_1]\ast[g_1]
$$

#### Pointed spaces and homotopy equivalence

Paths have a tendency to wander. By this, what I mean is that products of paths
is really a groupoid operation. But we want to do group theory, which means we
need to fix a point. This is where pointed spaces come in handy. A pointed
space is simply a topological space with a "distinguished point". Maps between
$(X, x)$ and $(Y, y)$ are simply continuous functions with the added condition
that base points are mapped to each other.

### Cell Complexes

## Homotopy Groups

From Munkres (beginning of chapter 9): Why study homotopy groups? Because it's
easy to prove that spaces are homeomorphic. But to show two spaces are _not_
homeomorphic (using only existence), you'd have to show that _no_ homeomorphism
exists. Much better to show that they have different invariants. Consider
proving that $\mathbb{R}^2$ and $\mathbb{R}^3$ are not homeomorphic. The
"basic" point-set properties that we know of are the same for each space
(connectedness, compactness, metrizability, separability, etc.). To Truly
differentiate between them as topological spaces, you'd need to discuss
dimension. But we're not allowed to do geometry in topology class, so we have
to beat around the bush and use notions like "simple connectedness". This is a
really deep concept that is often discussed in calculus 3 for some reason.
