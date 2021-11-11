# $0$ CPU_ID
# $1$ Variables
# $2$ Instructions
#
procedure CPU$0$_Instr(var f: OBJ_CPU);
/* Instructions */
$1$
begin
  alias cpu:f[$0$] do
$2$
  endalias;
end;