# $0$ state name
# $1$ access type name
# $2$ block variable name
# $3$ access func prefix
# $4$ optional network ready check
# $5$ optional lock functions
#
  rule "$0$_$1$"
    $2$.State = $0$ $4$
  ==>
    $3$$0$_$1$(adr, m);
    $5$
  endrule;