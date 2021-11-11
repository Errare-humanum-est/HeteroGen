procedure AddInstr(var f: MACH_CPU; var instr:INSTR);
begin
  alias p:f.instrstr do
  alias q: p.Queue do
  alias qcnt: p.QueueCnt do

  instr.pend := false;
  q[qcnt]:=instr;
  qcnt:=qcnt+1;


  endalias;
  endalias;
  endalias;
end;


function GetInstr(var f: MACH_CPU): INSTR;
var
  instr: INSTR;
begin
  alias p:f.instrstr do
  alias q: p.Queue do
  alias qind: p.QueueInd do
  alias qcnt: p.QueueCnt do
  undefine instr;

  if qind = qcnt then
    return instr;
  endif;

  if !isundefined(q[qind].access) then
    q[qind].pend := true;   /* Set instruction as active */
    return q[qind];
  endif;

  return instr;

  endalias;
  endalias;
  endalias;
  endalias;
end;

procedure PopInstr(var f: MACH_CPU);
begin
  alias p:f.instrstr do
  alias q: p.Queue do
  alias qind: p.QueueInd do
  alias qcnt: p.QueueCnt do

   qind := qind + 1;

   if qind = qcnt then
      f.active := false;  /* Set flag CPU done*/
   else
      if isundefined(q[qind].access) then
         f.active := false;
      endif;
   endif;

  endalias;
  endalias;
  endalias;
  endalias;
end;

procedure UpdateVal(var f: MACH_CPU; var val: ClValue);
begin
  alias p:f.instrstr do
  alias q: p.Queue do
  alias qind: p.QueueInd do
  alias qcnt: p.QueueCnt do

  if qind < qcnt & !isundefined(q[qind].access) then
    q[qind].cl := val;
  endif;

  endalias;
  endalias;
  endalias;
  endalias;
end;

function TestPend(var f: MACH_CPU): boolean;
var
  instr: INSTR;
begin
  alias p:f.instrstr do
  alias q: p.Queue do
  alias qind: p.QueueInd do
  alias qcnt: p.QueueCnt do
  undefine instr;

  if qind = qcnt then
    return false;
  endif;

  if !isundefined(q[qind].access) then
    return q[qind].pend;    /* return if instruction is pending */
  endif;

  return false;

  endalias;
  endalias;
  endalias;
  endalias;
end;