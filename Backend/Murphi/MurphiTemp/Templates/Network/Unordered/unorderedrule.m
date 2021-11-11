# $0$ networkname
# $1$ cond_rule_str
#
ruleset dst:Machines do
    choose midx:$0$[dst] do
        alias mach:$0$[dst] do
        alias msg:mach[midx] do
          rule "Receive $0$"
            !isundefined(msg.mtype)
          ==>
$1$
          endrule;
        endalias;
        endalias;
    endchoose;
endruleset;