# $0$ k_objset
# $1$ cache_id
#
        if ismember(cpu.cache, $0$$1$) then
          if cpu_try_access_$1$(cbe, adr, cpu) then
            PopInstr(cpu);
            return;
          endif;
        endif;