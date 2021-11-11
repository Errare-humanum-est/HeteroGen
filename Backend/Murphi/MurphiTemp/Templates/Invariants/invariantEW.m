# $0$ kaddress
# $1$ kmachine
# $2$ allowed kaccess
# $3$ forbidden kaccess
invariant "$2$ excludes $3$ check"
    forall a:$0$ do
        forall m1:$1$ do
        forall m2:$1$ do
        ( m1 != m2
          & MultiSetCount(i:g_perm[m1][a], g_perm[m1][a][i] = $2$) > 0)
        ->
          MultiSetCount(i:g_perm[m2][a], g_perm[m2][a][i] = $3$) = 0
        endforall
        endforall
    endforall;
