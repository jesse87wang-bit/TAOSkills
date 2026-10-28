import json,sys
d=json.load(open('lines_chars.json')); C=d['chars']; T=d['times']
def kw(w, after=0):
    w=w.lower(); i=0
    while True:
        i=C.find(w,i)
        if i<0: return None
        if T[i]>=after: return (T[i], T[i+len(w)-1])
        i+=1
if __name__=='__main__':
    after=0
    for a in sys.argv[1:]:
        if a.startswith('@'): after=float(a[1:]); continue
        r=kw(a,after); print(f'{a:12s}', r)
        if r: after=r[0]
