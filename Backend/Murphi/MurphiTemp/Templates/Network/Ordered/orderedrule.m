# $0$ networkname
# $1$ cnt_suffix_network
# $2$ cond_rule_str
#
ruleset dst:Machines do
    ruleset src: Machines do
        alias msg:$0$[dst][src][0] do
          rule "Receive $0$"
            $1$$0$[dst][src] > 0
          ==>
$2$
          endrule;
        endalias;
    endruleset;
endruleset;