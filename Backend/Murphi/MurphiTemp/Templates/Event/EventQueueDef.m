# $0$ k_event
# $1$ arch_name
# $2$ k_entry
# $3$ k_address
# $4$ k_event_label
# $5$ c_adr_cnt_const
# $6$ atomic_event_lock
#
$0$$2$$1$: record
    evt_type: $4$$1$;
    evt_adr: $3$;
end;

$0$$1$: record
    event_queue: array[0..$5$] of $0$$2$$1$;
    event_queue_index: 0..$5$+1;
    pend_adr: multiset[$5$+1] of $3$;
    $6$
end;