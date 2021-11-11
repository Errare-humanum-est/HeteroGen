# $0$ state name
# $1$ access type name
# $2$ block variable name
# $3$ arch name
# $4$ access func prefix
# $5$ optional network ready check
#
  rule "$0$_$1$"
    $2$.State = $0$ & CheckRemoteEvent_$3$($3$_$1$, m, adr) $5$
  ==>
    $4$$0$_$1$(adr, m);
  endrule;