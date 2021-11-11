# $0$ network name
# $1$ cluster name
# $2$ Vector for multicast
# $3$ machines key
#
procedure Multicast_$0$_$1$(var msg: Message; dst_vect: $2$; src: $3$;);
begin
      for n:Machines do
          if n!=msg.src then
            if MultiSetCount(i:dst_vect, dst_vect[i] = n) = 1 then
              msg.dst := n;
              Send_$0$(msg, src);
            endif;
          endif;
      endfor;
end;