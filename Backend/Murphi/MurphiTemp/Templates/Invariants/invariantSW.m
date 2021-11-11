# $0$ kaddress
# $1$ kmachine
# $2$ kaccess
invariant "exclusive $2$ check"
    forall a:$0$ do
        forall m1:$1$ do
        forall m2:$1$ do
        ( m1 != m2
          & MultiSetCount(i:g_perm[m1][a], g_perm[m1][a][i] = $2$) > 0)
        ->
          MultiSetCount(i:g_perm[m2][a], g_perm[m2][a][i] = $2$) = 0
        endforall
        endforall
    endforall;


