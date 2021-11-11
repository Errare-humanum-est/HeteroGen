# $0$ networkname
# $1$ cnt_network

undefine $0$;
for dst:Machines do
    for src: Machines do
        $1$$0$[dst][src] := 0;
    endfor;
endfor;