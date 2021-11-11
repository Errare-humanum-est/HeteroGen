# $0$ k_machines
# $1$ Execute body
#
procedure Serve_CPU(var cbe: ClValue; adr: Address; m: $0$);
begin
for i:OBJSET_CPU do
   if i_cpu[i].cache = m then
     alias cpu:i_cpu[i] do
     if TestPend(i_cpu[i]) then
$1$
     endif;
     endalias;
   endif;
endfor;
end;