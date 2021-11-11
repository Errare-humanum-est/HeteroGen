# $0$ fifosize
#
FIFO: record
  Queue: array[0..$0$] of Message;
  QueueInd: 0..$0$+1;
end;