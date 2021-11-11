# $0$ cache_id
# $1$ cache block identifier
# $2$ cache block entry
# $3$ Machine var
#
/* Issue Cache request to update */
procedure access_$0$(var cpu: MACH_CPU);
var instr: INSTR;
begin
  instr := GetInstr(cpu);
  alias adr: instr.adr do
  alias $3$: cpu.cache do
  alias $2$: i_$0$[$3$].$1$[adr] do
  alias access: instr.access do
