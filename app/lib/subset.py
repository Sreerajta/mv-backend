#Temporary script for demo only ...
#Find the subsets(which we already have) needed to build a given set . NOTE : not the best solution , to be looked into later
def compare(a,b):
    if len(a)>len(b):
        return 1
    elif len(a)<len(b):
        return -1
    else:
        return 0


dictionary = {
    frozenset(["Action","Comedy"]): 3,
    frozenset(["Drama","Fantasy"]): 2,
    frozenset(["Drama"]): 1
}

def totree(d):
    tree = {}
    for key in d:
        t = tree
        for x in sorted(key):
            t = t.setdefault(x, {})
        t["value"] = d[key]
    return tree

tree = totree(dictionary)
print(tree)

def check_subsets(tree, key, prefix=[]):
    if "value" in tree:
        yield prefix, tree["value"]
    for i, x in enumerate(key):
        if x in tree:
            yield from check_subsets(tree[x], key[i+1:], prefix+[x])
 
biglist= ["Action", "Comedy","Drama"]
biglist = sorted(biglist)
print(biglist)
res = list(check_subsets(tree, sorted(biglist)))
res_set = []
for r in res:
    res_set.append(r[0])
res_set_sorted = sorted(res_set, key = len,reverse=True)

subsets_needed = []
temp = []
for r in res_set_sorted:    
        temp += r
        subsets_needed.append(r)       
        temp.sort()
        if temp == biglist:
            break
print(subsets_needed)   

