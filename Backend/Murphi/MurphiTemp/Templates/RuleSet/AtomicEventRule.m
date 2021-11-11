# $0$   arch name
# $1$   state name
# $2$   function name
# $3$   block variable name
#
rule "$0$_$1$_$2$"
  $3$.State = $0$_$1$
==>
  $2$$0$(m, adr);
endrule;