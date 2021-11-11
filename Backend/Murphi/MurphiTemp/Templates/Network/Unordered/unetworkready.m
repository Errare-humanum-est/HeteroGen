# $0$ networkname
# $1$ bound
# $2$ reduction
#
function $0$_network_ready(): boolean;
begin
      for mach:Machines do
        alias mul_set:$0$[mach] do
          if MultisetCount(i:mul_set, isundefined(mul_set[i].mtype)) >= ($1$-$2$) then
            return false;
          endif;
        endalias;
      endfor;

      return true;
end;