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
    I0.adr := 1;            /* Dummy load y */
    I0.cl := undefined;
    AddInstr(cpu, I0);

    I1.access := store;
    I1.adr := 0;            /* x */
    I1.cl := 1;
    AddInstr(cpu, I1);

    I2.access := mfence;
    I2.adr := 0;            /* x */
    I2.cl := undefined;
    AddInstr(cpu, I2);

    I3.access := load;
    I3.adr := 1;            /* y */
    I3.cl := undefined;
    AddInstr(cpu, I3);

  endalias;
end;