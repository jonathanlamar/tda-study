object CategoryTheory {
  trait Functor[F[_]] {
    def fmap[A, B](f: A => B): F[A] => F[B]
  }

  object ListFunctor extends Functor[List] {
    def fmap[A, B](f: A => B): List[A] => List[B] = (v: List[A]) =>
      v match {
        case Nil          => Nil
        case head :: tail => f(head) :: fmap(f)(tail)
      }
  }

  // Just to define A
  type A = Int

  // Functions from A to B are covariant w.r.t. B
  type CovariantHom[+B] = A => B
  // Functions from B to A are contravariant w.r.t. B
  type ContravariantHom[-B] = B => A

  trait ContravariantFunctor[F[-_]] {
    def fmap[X, Y](f: X => Y): F[Y] => F[X]
  }

  object HomFunctor extends Functor[CovariantHom] {
    def fmap[X, Y](f: X => Y): CovariantHom[X] => CovariantHom[Y] =
      (g: A => X) => f.compose(g) // fg: A => Y
  }

  object ContravariantHomFunctor
      extends ContravariantFunctor[ContravariantHom] {
    def fmap[X, Y](f: X => Y): ContravariantHom[Y] => ContravariantHom[X] =
      (g: Y => A) => g.compose(f) // gf: X => A
  }

  trait NaturalTransformation[F[_], G[_]] {
    def etaMapObs[X]: F[X] => G[X]
  }

  object SafeHead extends NaturalTransformation[List, Option] {
    def etaMapObs[X]: List[X] => Option[X] = (l: List[X]) =>
      // Pattern matching is like switch-case, but has nice qualities.
      l match {
        case Nil       => None
        case head :: _ => Some(head) // Scala way of saying (head, anything)
      }
  }

  type Product[B] = (B, A)
  type Id[B] = B

  object ProdFunctor extends Functor[Product] {
    // Unfortunate failure in scala destructuring functionality.
    def fmap[X, Y](f: X => Y): Product[X] => Product[Y] = { case (x: X, a: A) =>
      (f(x), a)
    }
  }

  object IdFunctor extends Functor[Id] {
    def fmap[X, Y](f: X => Y): Id[X] => Id[Y] = f
  }

  type ProdHom[B] = Product[CovariantHom[B]]
  object ProdHomFunctor extends Functor[ProdHom] {
    def fmap[X, Y](
        f: X => Y
    ): Product[CovariantHom[X]] => Product[CovariantHom[Y]] =
      (ProdFunctor
        .fmap[CovariantHom[X], CovariantHom[Y]](_))
        .compose(HomFunctor.fmap[X, Y])(f)
  }

  type HomProd[B] = CovariantHom[Product[B]]
  object HomProdFunctor extends Functor[HomProd] {
    def fmap[X, Y](
        f: X => Y
    ): CovariantHom[Product[X]] => CovariantHom[Product[Y]] =
      (HomFunctor
        .fmap[Product[X], Product[Y]](_))
        .compose(ProdFunctor.fmap[X, Y])(f)
  }

  object CurryingCoUnit extends NaturalTransformation[Id, HomProd] {
    def etaMapObs[B]: Id[B] => CovariantHom[Product[B]] = (b: B) =>
      (a: A) => (b, a)
  }

  object CurryingUnit extends NaturalTransformation[ProdHom, Id] {
    def etaMapObs[B]: Product[CovariantHom[B]] => Id[B] = { case (f, a) =>
      f(a)
    }
  }
}
