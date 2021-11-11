# $0$ CPU_ID

procedure CPU$0$_Instr(var f: OBJ_CPU);
/* Instructions */
var I0: INSTR;
var I1: INSTR;
begin
  alias cpu:f[$0$] do
    I0.access := store;
    I0.adr := 2;
    I0.cl := 1;
    AddInstr(cpu, I0);

    I1.access := load;
    I1.adr := 0;
    I1.cl := 0;
    AddInstr(cpu, I1);

  endalias;
end;