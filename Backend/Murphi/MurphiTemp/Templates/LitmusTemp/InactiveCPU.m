# $0$ CPU_ID
#
procedure CPU$0$_Instr(var f: OBJ_CPU);
begin
  alias cpu:f[$0$] do
    cpu.active := false;
  endalias;
end;