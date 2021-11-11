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
    I0.adr := 0;            /* Dummy load x */
    I0.cl := undefined;
    AddInstr(cpu, I0);

    I1.access := load;
    I1.adr := 1;            /* Dummy load x */
    I1.cl := undefined;
    AddInstr(cpu, I1);

    I2.access := acquire;
    I2.adr := 1;            /* y */
    I2.cl := undefined;
    AddInstr(cpu, I2);

    I3.access := load;
    I3.adr := 0;            /* x */
    I3.cl := undefined;
    AddInstr(cpu, I3);

  endalias;
end;