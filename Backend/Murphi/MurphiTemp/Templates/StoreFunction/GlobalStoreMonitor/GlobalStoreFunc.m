# $0$ kaddress
# $1$ k_cl_value
# $2$ k_cl_value_bound
#
procedure Execute_store_monitor(cb: $1$; adr: $0$);
begin
  alias cbe: g_monitor_store[adr] do
    if cbe = cb then
      if cbe = $2$ then
        cbe := 0;
      else
        cbe := cbe + 1;
      endif;
    else
        error "Write linearization failed";
    endif;
  endalias;
end;

procedure Reset_global_monitor();
begin
  for adr:$0$ do
    g_monitor_store[adr] := 0;
  endfor;
end;