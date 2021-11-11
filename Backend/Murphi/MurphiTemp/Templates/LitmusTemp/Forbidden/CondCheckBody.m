# $0$ CPU
# $1$ Instruction number
# $2$ Value
#
  if i_cpu[$0$].instrstr.Queue[$1$].cl = $2$ then
    match_cnt := match_cnt + 1;
  endif;