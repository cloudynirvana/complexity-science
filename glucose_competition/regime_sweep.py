"""Regime sweep: random dimensionless parameters -> counts of long-run behaviours (exploratory)."""
import numpy as np, collections
from glucose_competition.model import *
rng=np.random.default_rng(1)
cnt=collections.Counter(); ex={}
for i in range(400):
    p=Params(u=10**rng.uniform(-1,1.3),v=10**rng.uniform(-1.5,0.5),d=rng.uniform(0.05,0.45),
             k=10**rng.uniform(-0.5,1.2),h=10**rng.uniform(-1.3,0.3),s=10**rng.uniform(-3,-0.7),
             b=10**rng.uniform(-0.5,1),m=10**rng.uniform(-1.3,0))
    ss=steady_states(p,n_starts=40,seed=i)
    stable=[y for y,st,_ in ss if st]
    # long-run behaviour from tumour-bearing start
    sol=simulate(p,[0.8,0.5,0.1],900); tail=sol.y[:,sol.t>600]
    osc=(tail[1].max()-tail[1].min())>0.05*max(tail[1].max(),1e-9) and tail[1].max()>1e-3
    kind=("osc" if osc else "")+f"|stable={len(stable)}|tumourfree_stable={any(y[1]<1e-6 for y in stable)}|tumour_stable={any(y[1]>1e-3 for y in stable)}"
    cnt[kind]+=1; ex.setdefault(kind,p)
for k,v in cnt.most_common(): print(v,k)
import json; json.dump({k:vars(p) for k,p in ex.items()},open('glucose_competition/regime_examples.json','w'),indent=1)
