# $0$   Cond Checks
# $1$   Check Count
#
procedure Forbidden();

var match_cnt: 0..$1$;

begin
  match_cnt := 0;

$0$

  if match_cnt = $1$ then
    error "Litmus Test Failed"
  endif;

end;