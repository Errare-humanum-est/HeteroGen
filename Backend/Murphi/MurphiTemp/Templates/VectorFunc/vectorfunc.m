# $0$ vectorname
# $1$ vectortype
# $2$ machineset
# $3$ vectortyperange
#
-- .add()
procedure AddElement_$0$(var sv:$1$; n:$2$);
begin
    if MultiSetCount(i:sv, sv[i] = n) = 0 then
      MultiSetAdd(n, sv);
    endif;
end;

-- .del()
procedure RemoveElement_$0$(var sv:$1$; n:$2$);
begin
    if MultiSetCount(i:sv, sv[i] = n) = 1 then
      MultiSetRemovePred(i:sv, sv[i] = n);
    endif;
end;

-- .clear()
procedure ClearVector_$0$(var sv:$1$;);
begin
    MultiSetRemovePred(i:sv, true);
end;

-- .contains()
function IsElement_$0$(var sv:$1$; n:$2$) : boolean;
begin
    if MultiSetCount(i:sv, sv[i] = n) = 1 then
      return true;
    elsif MultiSetCount(i:sv, sv[i] = n) = 0 then
      return false;
    else
      Error "Multiple Entries of Sharer in SV multiset";
    endif;
  return false;
end;

-- .empty()
function HasElement_$0$(var sv:$1$; n:$2$) : boolean;
begin
    if MultiSetCount(i:sv, true) = 0 then
      return false;
    endif;

    return true;
end;

-- .count()
function VectorCount_$0$(var sv:$1$) : $3$$1$;
begin
    return MultiSetCount(i:sv, true);
end;