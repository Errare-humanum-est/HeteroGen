# $0$ networkname
# $1$ buf_prefix
#
if PushQueue($1$$0$, dst, msg) then
  Pop_$0$(dst, src);
endif;