# $0$ fifobuffer
# $1$ cond_rule_str

ruleset dst:Machines do
  alias p:$0$[dst] do

      rule "$0$"
        (p.QueueInd>0)
      ==>
        alias msg:p.Queue[0] do
$1$
          else error "unknown machine";
          endif;
        endalias;
      endrule;

  endalias;
endruleset;