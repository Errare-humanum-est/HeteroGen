# $0$ cache_id
# $1$ cache block identifier
# $2$ additional load strings
# $3$ additional store strings
# $4$ no access operations
#
/* Tries to serve the access */
function cpu_try_access_$0$(var cbe: ClValue; adr: Address; var cpu: MACH_CPU): boolean;
var instr: INSTR;
begin
  instr := GetInstr(cpu);

  alias cpu_adr:instr.adr do
  alias cache: cpu.cache do

  if cpu_adr != adr then
    return false;
  endif;

  /* Load operation */
  if $2$isundefined(instr.cl) &
        (MultiSetCount(i:g_perm[cache][cpu_adr], g_perm[cache][cpu_adr][i] = load) = 1) then
    UpdateVal(cpu, cbe);
    return true;
  endif;

  /* Store operation */
  if $3$
        MultiSetCount(i:g_perm[cache][cpu_adr], g_perm[cache][cpu_adr][i] = store) = 1 then
    cbe := instr.cl;
    return true;
  endif;

  $4$

  return false;
  endalias;
  endalias;
end;
