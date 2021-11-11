# $0$ networkname
# $1$ cnt
# $2$ networkmax
# $3$ machines key
#
procedure Send_$0$(msg:Message; src: $3$;);
  Assert($1$$0$[msg.dst][src] < $2$) "Too many messages";
  $0$[msg.dst][src][$1$$0$[msg.dst][src]] := msg;
  $1$$0$[msg.dst][src] := $1$$0$[msg.dst][src] + 1;
end;

procedure Pop_$0$(dst:$3$; src: $3$;);
begin
  Assert ($1$$0$[dst][src] > 0) "Trying to advance empty Q";
  for i := 0 to $1$$0$[dst][src]-1 do
    if i < $1$$0$[dst][src]-1 then
      $0$[dst][src][i] := $0$[dst][src][i+1];
    else
      undefine $0$[dst][src][i];
    endif;
  endfor;
  $1$$0$[dst][src] := $1$$0$[dst][src] - 1;
end;