# $0$ networkname
# $1$ networkmax
# $2$ machines key
#
procedure Send_$0$(msg:Message; src: $2$;);
  Assert (MultiSetCount(i:$0$[msg.dst], true) < $1$) "Too many messages";
  MultiSetAdd(msg, $0$[msg.dst]);
end;