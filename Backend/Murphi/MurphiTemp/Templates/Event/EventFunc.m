# $0$ arch name
# $1$ k_event
# $2$ k_objset
# $3$ k_address
# $4$ k_instance
#
/* Checks if the currently pending event has been served and if a new one has been issued*/
function TestEvent_$0$(cur_evt_type: $1$$0$; m: $2$$0$; adr: $3$): boolean;
begin
  alias evt_entry: $4$$0$[m].evt do
  alias pend_adr: $4$$0$[m].evt.pend_adr do

    if isundefined(evt_entry.event_queue[0].evt_type) then
        return false;
    endif;

    /* Check if the event type matches and the event still need to be served for this address */
    if evt_entry.event_queue[0].evt_type = cur_evt_type & MultisetCount(a: pend_adr, pend_adr[a] = adr) = 1 then
        MultisetRemovePred(a: pend_adr, pend_adr[a] = adr);
        return true;

    else
      /* If no more adresses are pending and the current event entry is not undefined pop the event queue */
      if MultisetCount(a:pend_adr, true) = 0 then
        if !isundefined(evt_entry.event_queue[0].evt_type) then
          FSM_Event_$0$(evt_entry.event_queue[0].evt_type, m, evt_entry.event_queue[0].evt_adr);
          PopEvent_$0$(m);
        endif;
      endif;
      return false;
    endif;

  endalias;
  endalias;
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