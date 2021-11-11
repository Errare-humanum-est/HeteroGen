# $0$ k_objset
# $1$ cache_id
#
    if ismember(cpu.cache, $0$$1$) then
      access_$1$(cpu);
    endif;