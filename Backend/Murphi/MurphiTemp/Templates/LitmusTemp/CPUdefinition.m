# $0$ NrCaches
# $1$ NrInstr (Litmust test dependent)
# $2$ Machinekey self.kmachines
# $3$ Permission type key
# $4$ k_address
# $5$ k_cl_value
#
/* The number of CPUS in the OBJSET must be equal to the number of L1 caches */
OBJSET_CPU: 0..$0$-1;

/* Instruction */
INSTR: record
  access: $3$;
  adr: $4$;
  cl: $5$;      /* Value store for read operation performed */
  pend: boolean;
end;

/* Instruction Queue */
FIFO_CPU: record
  Queue: array[0..$1$] of INSTR;
  QueueInd: 0..$1$+1;
  QueueCnt: 0..$1$+1;
end;

MACH_CPU: record
  cache: $2$;  /* Store associated cache ID*/
  active: boolean;
  pending: boolean;
  instrstr: FIFO_CPU;
end;

/* CPUs */
OBJ_CPU: array[OBJSET_CPU] of MACH_CPU;