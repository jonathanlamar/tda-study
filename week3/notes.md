# Week 3: Basic Homotopy Theory

## Algebraic Constructions

Probably some or all of this gets pushed to week 3, so I will be very brief.

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

### Homotopies and the Homotopy category

Homotopies are continuous deformations of maps, but we often talk of spaces as
being homotopy-equivalent. This is because the modding out of maps induces a
quotient of categories, which identifies morphisms by homotopy. This also
identifies spaces because isomorphism in the homotopy category is a weaker
condition then isomorphism in Top.

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
