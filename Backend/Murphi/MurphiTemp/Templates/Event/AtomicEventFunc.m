# $0$   Test atomic func
# $1$   Lock atomic func
# $2$   Unlock atomic func
# $3$   arch name
# $4$   instance id
# $5$   objset id
# $6$   address id
# $7$   event lock var
#
function $0$$3$(m: $5$$3$): boolean;
begin
    if isundefined($4$$3$[m].evt.$7$) then
        return true;
    else
        return false;
    endif;
end;

procedure $1$$3$(m: $5$$3$; adr: $6$);
begin
  $4$$3$[m].evt.$7$ := adr;
end;

procedure $2$$3$(m: $5$$3$; adr: $6$);
begin
    if !isundefined($4$$3$[m].evt.$7$) then
        if $4$$3$[m].evt.$7$ = adr then
            undefine $4$$3$[m].evt.$7$;
        endif;
    endif;
end;
