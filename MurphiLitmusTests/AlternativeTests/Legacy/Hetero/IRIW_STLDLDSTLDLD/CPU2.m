# $0$ CPU_ID
#
procedure CPU$0$_Instr(var f: OBJ_CPU);
/* Instructions */
var I0: INSTR;
var I1: INSTR;
var I2: INSTR;
var I3: INSTR;
begin
  alias cpu:f[$0$] do
    I0.access := load;
    I0.adr := 0;
    I0.cl := undefined;
    AddInstr(cpu, I0);

    I1.access := load;
    I1.adr := 1;
    I1.cl := undefined;
    AddInstr(cpu, I1);

    I2.access := load;
    I2.adr := 1;
    I2.cl := undefined;
    AddInstr(cpu, I2);

    I3.access := store;
    I3.adr := 1;
    I3.cl := 1;
    AddInstr(cpu, I3);

  endalias;
end;