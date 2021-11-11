# $0$   CPU0
# $1$   CPU1
# $2$   CPU_COUNT
#
procedure Forbidden();
var R0: ClValue;
var R1: ClValue;

var match_cnt: 0..$2$;

begin
  /* Forbidden outcome */
  R0 := 1;
  R1 := 0;

  match_cnt := 0;

  /* Queue index position is important */
  if i_cpu[$1$].instrstr.Queue[1].cl = R0 then

    if i_cpu[$1$].instrstr.Queue[1].access != load then
        put i_cpu[$1$].instrstr.Queue[1];
        error "CPU access $1$ is not of type load";
    endif;
    match_cnt := match_cnt + 1;
  endif;

  if i_cpu[$1$].instrstr.Queue[2].cl = R1 then
    if i_cpu[$1$].instrstr.Queue[2].access != load then
        put i_cpu[$1$].instrstr.Queue[2];
        error "CPU access $1$ is not of type load";
    endif;
    match_cnt := match_cnt + 1;
  endif;

  if match_cnt = $2$ then
    error "Litmus Test Failed"
  endif;

end;