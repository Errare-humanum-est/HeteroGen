# $0$ kaccesstype
# $1$ kaddress
# $2$ kmachines
#
procedure Clear_perm(adr: $1$; m: $2$);
begin
  alias l_perm_set:g_perm[m][adr] do
      undefine l_perm_set;
  endalias;
end;

procedure Set_perm(acc_type: $0$; adr: $1$; m: $2$);
begin
  alias l_perm_set:g_perm[m][adr] do
  if MultiSetCount(i:l_perm_set, l_perm_set[i] = acc_type) = 0 then
      MultisetAdd(acc_type, l_perm_set);
  endif;
  endalias;
end;

procedure Reset_perm();
begin
  for m:$2$ do
    for adr:$1$ do
      Clear_perm(adr, m);
    endfor;
  endfor;
end;

