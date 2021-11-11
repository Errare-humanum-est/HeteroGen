# $0$ networkname
# $1$ cnt_network

undefine $0$;
for dst:Machines do
    $1$$0$[dst] := 0;
endfor;