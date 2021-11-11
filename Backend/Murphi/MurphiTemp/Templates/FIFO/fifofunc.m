# $0$ fifosize
# $1$ net suffix
# $2$ machine key
# $3$ message key
#
function PushQueue(var f: $1$FIFO; n:$2$; msg:$3$): boolean;
begin
  alias p:f[n] do
  alias q: p.Queue do
  alias qind: p.QueueInd do

    if (qind<=$0$) then
      q[qind]:=msg;
      qind:=qind+1;
      return true;
    endif;

    return false;

  endalias;
  endalias;
  endalias;
end;

function GetQueue(var f: $1$FIFO; n:$2$): $3$;
var
  msg: $3$;
begin
  alias p:f[n] do
  alias q: p.Queue do
  undefine msg;

  if !isundefined(q[0].mtype) then
    return q[0];
  endif;

  return msg;
  endalias;
  endalias;
end;

procedure PopQueue(var f: $1$FIFO; n:$2$);
begin
  alias p:f[n] do
  alias q: p.Queue do
  alias qind: p.QueueInd do


  for i := 0 to qind-1 do
      if i < qind-1 then
        q[i] := q[i+1];
      else
        undefine q[i];
      endif;
    endfor;
    qind := qind - 1;

  endalias;
  endalias;
  endalias;
end;
