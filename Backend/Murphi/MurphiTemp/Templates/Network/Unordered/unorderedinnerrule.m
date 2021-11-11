# $0$ fsm prefix name
# $1$ arch_name
# $2$ network name
#
if $0$$1$(msg, dst) then
  MultiSetRemove(midx, mach);
endif;