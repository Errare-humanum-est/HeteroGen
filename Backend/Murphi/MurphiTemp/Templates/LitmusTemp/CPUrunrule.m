# $0$ Reset function name
#
/* RUN CPU */
ruleset m:OBJSET_CPU do
  ruleset adr:Address do
      alias cpu: i_cpu[m] do

      rule "CPU_serve"
        cpu.active = true
      ==>
        Issue_CPU(i_cpu[m]);
      endrule;

      /* RULESET RESET CONDITION */
      rule "CPU_done"
        cpu.active = false
      ==>
        if Check_reset() then
          /* Evaluate invariants */
          Forbidden();
          /* Then perform reset */
          $0$();
        endif;
      endrule;

      endalias;
  endruleset;
endruleset;
