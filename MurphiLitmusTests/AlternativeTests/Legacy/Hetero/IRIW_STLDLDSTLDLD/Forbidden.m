# $0$   CPU0
# $1$   CPU1
# $2$   CPU2
# $3$   CPU2
# $4$   CPU_COUNT
#
procedure Forbidden();
var R0: ClValue;
var R1: ClValue;
var R2: ClValue;
var R3: ClValue;

var match_cnt: 0..$4$;

begin
  /* Forbidden outcome */
  R0 := 1;
  R1 := 0;
  R2 := 1;
  R3 := 0;

  match_cnt := 0;

  /* Queue index position is important */
  if i_cpu[$1$].instrstr.Queue[2].cl = R0 then
    if i_cpu[$1$].instrstr.Queue[2].access != load then
        put i_cpu[$1$].instrstr.Queue[2];
        error "CPU access $1$ is not of type load";
    endif;
    match_cnt := match_cnt + 1;
  endif;

  if i_cpu[$1$].instrstr.Queue[3].cl = R1 then
    if i_cpu[$1$].instrstr.Queue[3].access != load then
        put i_cpu[$1$].instrstr.Queue[3];
        error "CPU access $1$ is not of type load";
    endif;
    match_cnt := match_cnt + 1;
  endif;

  if i_cpu[$3$].instrstr.Queue[2].cl = R2 then
    if i_cpu[$3$].instrstr.Queue[2].access != load then
        put i_cpu[$3$].instrstr.Queue[2];
        error "CPU access $3$ is not of type load";
    endif;
    match_cnt := match_cnt + 1;
  endif;

  if i_cpu[$3$].instrstr.Queue[3].cl = R3 then
    if i_cpu[$3$].instrstr.Queue[3].access != load then
        put i_cpu[$3$].instrstr.Queue[3];
        error "CPU access $3$ is not of type load";
    endif;
    match_cnt := match_cnt + 1;
  endif;

  if match_cnt = 4 then
    error "Litmus Test Failed"
  endif;

end;