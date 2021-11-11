# $0$ reset func name
# $1$ arch name
# $1$ objset key
# $2$ address key
# $3$ init functions
#
procedure $0$$1$();
begin
  for i:$2$$1$ do
    for a:$3$ do
$4$
    endfor;
  endfor;
end;