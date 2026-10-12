from acee6_k2_fuzz_reducer import minimize
value={"target_path":"../../escape.py","noise":[1,2,3],"extra":"abc"}
reduced=minimize(value,lambda x:isinstance(x,dict) and "target_path" in x and ".." in str(x["target_path"]))
assert reduced=={"target_path":".."} or (set(reduced)=={"target_path"} and ".." in reduced["target_path"])
print("ACEE6_K2_REDUCER_OK")
