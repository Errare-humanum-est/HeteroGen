# $0$ network name
# $1$ buffer suffix
#
for i:Machines do
    undefine $1$$0$[i].Queue;
    $1$$0$[i].QueueInd:=0;
endfor;