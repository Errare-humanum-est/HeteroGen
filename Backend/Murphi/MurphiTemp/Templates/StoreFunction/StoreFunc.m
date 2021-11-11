# $0$ v_cache
# $1$ k_cl_value
# $2$ v_address
# $3$ k_address
# $4$ k_cl_value_bound
# $5$ check_function (optional), the check must be performed before the store is executed
#
procedure Store(var $0$: $1$; $2$: $3$);
begin
  $5$
  if $0$ = $4$ then
    $0$:= 0;
  else
    $0$ := $0$ + 1;
  endif;
end;