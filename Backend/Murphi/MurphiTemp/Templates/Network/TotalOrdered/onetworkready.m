# $0$ networkname
# $1$ countsuf
# $2$ bound
# $3$ reduction
#
function $0$_network_ready(): boolean;
begin
      for dst:Machines do
        for src: Machines do
          if $1$$0$[dst] >= ($2$-$3$) then
            return false;
          endif;
        endfor;
      endfor;

      return true;
end;