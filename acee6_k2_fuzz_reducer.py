from __future__ import annotations
from copy import deepcopy
from typing import Any, Callable

def _candidates(value: Any) -> list[Any]:
    out=[]
    if isinstance(value,dict):
        for key in sorted(value):
            trial=dict(value); trial.pop(key,None); out.append(trial)
        for key in sorted(value):
            for reduced in _candidates(value[key]):
                trial=dict(value); trial[key]=reduced; out.append(trial)
    elif isinstance(value,list):
        for index in range(len(value)):
            out.append(value[:index]+value[index+1:])
        if value: out.extend([[], value[:max(1,len(value)//2)]])
    elif isinstance(value,str):
        if value: out.extend(["", value[:1], value[:max(1,len(value)//2)], value.replace("..", "."), value.replace("\u200b","")])
    elif isinstance(value,(int,float)) and not isinstance(value,bool): out.extend([0,1,-1])
    return out

def minimize(value: Any, failing: Callable[[Any], bool], max_rounds: int=128) -> Any:
    current=deepcopy(value)
    rounds=0
    changed=True
    while changed and rounds < max_rounds:
        changed=False
        for candidate in _candidates(current):
            rounds += 1
            try: still=bool(failing(candidate))
            except Exception: still=True
            if still:
                current=candidate; changed=True; break
            if rounds >= max_rounds: break
    return current
