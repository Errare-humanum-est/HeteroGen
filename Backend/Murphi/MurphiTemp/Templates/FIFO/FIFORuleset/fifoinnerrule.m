# $0$ func_name
# $1$ arch_name
# $2$ fifobuffer
#
if $0$$1$(msg, dst) then
  PopQueue($2$, dst);
endif;