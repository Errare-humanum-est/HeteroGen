# $0$ objset prefix
# $1$ arch name
# $2$ cache block variable name
# $3$ k_instance
# $4$ cache block identifier ("cb")
# $5$ rule str
#
ruleset m:$0$$1$ do
ruleset adr:Address do
  alias $2$:$3$$1$[m].$4$[adr] do

$5$
  endalias;
endruleset;
endruleset;