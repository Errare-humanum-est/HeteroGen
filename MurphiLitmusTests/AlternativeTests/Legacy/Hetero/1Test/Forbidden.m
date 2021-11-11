# $0$   CPU0
# $1$   CPU_COUNT
#
procedure Forbidden();
var R0: ClValue;

var match_cnt: 0..$1$;

begin
  /* Forbidden outcome */
  R0 := 0;

  match_cnt := 0;

  /* Queue index position is important */
  if i_cpu[$0$].instrstr.Queue[2].cl = R0 then
    if i_cpu[$0$].instrstr.Queue[2].access != load then
        put i_cpu[$0$].instrstr.Queue[2];
        error "CPU access $0$ is not of type load";
    endif;
    match_cnt := match_cnt + 1;
  endif;

  if match_cnt = $1$ then
    error "Litmus Test Failed"
  endif;

end;