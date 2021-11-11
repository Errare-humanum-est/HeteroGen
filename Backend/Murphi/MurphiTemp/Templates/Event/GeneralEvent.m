# $0$ arch name
# $1$ k_event
# $2$ k_objset
# $3$ k_address
# $4$ k_instance
# $5$ atomic event lock reset
#
procedure NextEvent_$0$(m: $2$$0$);
begin
  alias evt_entry: $4$$0$[m].evt do
  alias evt_index: evt_entry.event_queue_index do
  alias pend_adr: evt_entry.pend_adr do

    if isundefined(evt_entry.event_queue[0].evt_type) then
        return;
    endif;

    if MultisetCount(a:pend_adr, true) > 0 then
      return;
    else
      if evt_entry.event_queue_index > 0 then
        for a: $3$ do
          if a != evt_entry.event_queue[0].evt_adr then
            MultisetAdd(a, pend_adr);
          endif;
        endfor;
      endif;
    endif;

  endalias;
  endalias;
  endalias;
end;

procedure PopEvent_$0$(m: $2$$0$);
begin
  alias evt_entry: $4$$0$[m].evt do
  alias evt_index: evt_entry.event_queue_index do

    for i := 0 to evt_index-1 do
      if i < evt_index-1 then
        evt_entry.event_queue[i] := evt_entry.event_queue[i+1];
      else
        undefine evt_entry.event_queue[i];
      endif;
    endfor;

    evt_index := evt_index - 1;

  endalias;
  endalias;
end;

procedure ResetEvent_$0$();
begin
  for m: $2$$0$ do
    alias evt_entry: $4$$0$[m].evt do
      undefine evt_entry.event_queue;
      evt_entry.event_queue_index := 0;
      undefine evt_entry.pend_adr;
      $5$
    endalias;
  endfor;
end;

procedure IssueEvent_$0$(evt_type: $1$$0$; m: $2$$0$; adr: $3$);
begin
  alias evt_entry: $4$$0$[m].evt do
  alias evt_index: evt_entry.event_queue_index do

    evt_entry.event_queue[evt_index].evt_type := evt_type;
    evt_entry.event_queue[evt_index].evt_adr := adr;
    evt_index := evt_index + 1;

    NextEvent_$0$(m);

  endalias;
  endalias;
end;

/* Event: Checks if the currently pending event has been served*/
function CheckRemoteEvent_$0$(cur_evt_type: $1$$0$; m: $2$$0$; adr: $3$): boolean;
begin
  alias evt_entry: $4$$0$[m].evt do
  alias pend_adr: $4$$0$[m].evt.pend_adr do

    if isundefined(evt_entry.event_queue[0].evt_type) then
        return false;
    endif;

    /* Check if the event type matches and the event still need to be served for this address */
    if evt_entry.event_queue[0].evt_type = cur_evt_type & MultisetCount(a: pend_adr, pend_adr[a] = adr) = 1 then
        return true;
    endif;

    return false;

  endalias;
  endalias;
end;

procedure ServeRemoteEvent_$0$(cur_evt_type: $1$$0$; m: $2$$0$; adr: $3$);
begin
  alias evt_entry: $4$$0$[m].evt do
  alias pend_adr: $4$$0$[m].evt.pend_adr do

    /* Check if the event type matches and the event still need to be served for this address */
    if evt_entry.event_queue[0].evt_type = cur_evt_type & MultisetCount(a: pend_adr, pend_adr[a] = adr) = 1 then
        MultisetRemovePred(a: pend_adr, pend_adr[a] = adr);
    endif;

  endalias;
  endalias;
end;

/* Event Ack: Checks if the currently pending event has been served by all addresses */
function CheckInitEvent_$0$(cur_evt_type: $1$$0$; m: $2$$0$; adr: $3$): boolean;
begin
  alias evt_entry: $4$$0$[m].evt do
  alias pend_adr: $4$$0$[m].evt.pend_adr do

    if isundefined(evt_entry.event_queue[0].evt_type) then
        return false;
    endif;

    if evt_entry.event_queue[0].evt_type = cur_evt_type & MultisetCount(a:pend_adr, true) = 0 then
        return true;
    endif;

    return false;

  endalias;
  endalias;
end;

procedure ServeInitEvent_$0$(cur_evt_type: $1$$0$; m: $2$$0$; adr: $3$);
begin
  alias evt_entry: $4$$0$[m].evt do
  alias pend_adr: $4$$0$[m].evt.pend_adr do

    if evt_entry.event_queue[0].evt_type = cur_evt_type & MultisetCount(a:pend_adr, true) = 0 then
        PopEvent_$0$(m);
        NextEvent_$0$(m);
    endif;

  endalias;
  endalias;
end;
