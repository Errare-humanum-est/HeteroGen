    trace_index: 0..10;

    procedure trace_check();
    var found: boolean;
    begin
      found := false;

      for adr: Address do
      for c1:OBJSET_cacheL1C1 do
      for c2:OBJSET_cacheL1C1 do
      for dir:OBJSET_directoryL1C1 do

      if (trace_index = 0
        & c1 != c2
        & i_cacheL1C1[c1].cb[adr].State = cacheL1C1_O_store
        & i_cacheL1C1[c2].cb[adr].State = cacheL1C1_S_store
        & i_directoryL1C1[dir].cb[adr].State = directoryL1C1_M
        & i_directoryL1C1[dir].cb[adr].ownerL1C1 = c1
      )
      then
        found := true;
      endif;

      if (trace_index = 1
        & c1 != c2
        & i_cacheL1C1[c1].cb[adr].State = cacheL1C1_O_store
        & i_cacheL1C1[c2].cb[adr].State = cacheL1C1_S_store
        & i_directoryL1C1[dir].cb[adr].State = directoryL1C1_M
        & i_directoryL1C1[dir].cb[adr].ownerL1C1 = c2
      )
      then
        found := true;
        error "STOP";
      endif;

      endfor;
      endfor;
      endfor;
      endfor;

      if found then
        trace_index := trace_index + 1;
        put trace_index;
        error "STOP";
      else
        trace_index := 0;
      endif;
    end;


    ruleset adr:Address do
        rule "Trace Test"
          true
        ==>
          trace_check();
        endrule;
    endruleset;