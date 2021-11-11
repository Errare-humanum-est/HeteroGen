# $0$ cbe identifier
# $1$ key State
# $2$ Cache state
# $3$ Access type
# $4$ Optional network ready check
# $5$ Machine var
# $6$ access func prefix
#
  if cpu.pending = false & $0$.$1$ = $2$ & access = $3$ $4$ then
    $6$$2$_$3$(adr, $5$);
  endif;