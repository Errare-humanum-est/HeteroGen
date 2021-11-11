# $0$ networkname
# $1$ cluster name
# $2$ condition
# $3$ machines key
#
procedure Broadcast_$0$_$1$(var msg: Message; src: $3$;);
begin
      for dst:Machines do
          if $2$ then
              msg.dst := dst;
              Send_$0$(msg, src);
          endif;
      endfor;
end;