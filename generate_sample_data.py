"""Generate deterministic synthetic UK ecommerce source data. No real customers."""
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
rng = np.random.default_rng(20260924)
regions = ['North', 'South', 'Midlands', 'Scotland', 'Wales']
products = [
    (1,'Laptop','Electronics',850,610),
    (2,'Monitor','Electronics',250,175),
    (3,'Tablet','Electronics',380,270),
    (4,'Headphones','Electronics',115,62),
    (5,'Desk','Home Office',280,175),
    (6,'Office Chair','Home Office',195,112),
    (7,'Desk Lamp','Home Office',55,26),
    (8,'Webcam','Accessories',70,33),
    (9,'Keyboard','Accessories',85,43),
    (10,'Mouse','Accessories',35,15),
    (11,'Laptop Stand','Accessories',48,22),
    (12,'Notebook Set','Stationery',18,7),
]
pd.DataFrame(products,columns=['product_id','product_name','category','list_price_gbp','unit_cost_gbp']).to_csv(BASE/'raw_products.csv',index=False)

# Signup dates are independent of the simulated purchasing patterns.
start = pd.Timestamp('2023-01-01')
end = pd.Timestamp('2026-07-31')
customers=[]
for i in range(1,261):
    signup = start+pd.Timedelta(days=int(rng.integers(0,(end-start).days+1)))
    region=str(rng.choice(regions,p=[.28,.32,.22,.1,.08]))
    customers.append((i,f'C{i:04}',region,signup.strftime('%Y-%m-%d')))
customers_df=pd.DataFrame(customers,columns=['customer_id','customer_code','region','signup_date'])
# Deliberate data-quality examples: blank and inconsistent regional labels.
missing_region_ids=rng.choice(customers_df.index,size=12,replace=False)
customers_df.loc[missing_region_ids,'region']=''
remaining=np.setdiff1d(customers_df.index,missing_region_ids)
for idx in rng.choice(remaining,size=14,replace=False):
    customers_df.loc[idx,'region']=f" {str(customers_df.loc[idx,'region']).lower()} "
customers_df.to_csv(BASE/'raw_customers.csv',index=False)

orders=[];items=[];order_id=10001;line_id=1
months=pd.date_range('2024-01-01','2026-08-01',freq='MS')
for first in months:
    if first.year==2024: count=54
    elif first.year==2025: count=72
    else: count=85
    last=first+pd.offsets.MonthEnd(0)
    for _ in range(count):
        order_date=first+pd.Timedelta(days=int(rng.integers(0,last.day)))
        elig=customers_df.index[pd.to_datetime(customers_df.signup_date)<=order_date]
        customer_idx=int(rng.choice(elig))
        customer=int(customers_df.iloc[customer_idx].customer_id)
        status=str(rng.choice(['Completed','Cancelled','Returned'],p=[.85,.1,.05]))
        orders.append((order_id,customer,order_date.strftime('%Y-%m-%d'),status))
        for pid in rng.choice(np.arange(1,13),size=int(rng.choice([1,2,3],p=[.55,.33,.12])),replace=False):
            _,_,_,price,cost=products[int(pid)-1]
            qty=int(rng.choice([1,2,3],p=[.7,.24,.06]))
            discount=float(rng.choice([0,.05,.10,.15,.20],p=[.42,.23,.2,.11,.04]))
            items.append((line_id,order_id,int(pid),qty,float(price),float(cost),discount))
            line_id+=1
        order_id+=1
orders_df=pd.DataFrame(orders,columns=['order_id','customer_id','order_date','status'])
items_df=pd.DataFrame(items,columns=['order_item_id','order_id','product_id','quantity','unit_price_gbp','unit_cost_gbp','discount_pct'])
# Add known, intentional defects so the cleaning stages are demonstrable.
orders_df.loc[0,'status']=' completed '
orders_df.loc[1,'status']='CANCELLED'
orders_df=pd.concat([orders_df,orders_df.iloc[[4]],pd.DataFrame([[99999,1,'not-a-date','Completed']],columns=orders_df.columns)],ignore_index=True)
items_df=pd.concat([items_df,items_df.iloc[[3,8,13]]],ignore_index=True)
items_df=pd.concat([items_df,pd.DataFrame([
    [90001,10001,1,0,850,610,0],
    [90002,10001,2,1,-90,60,0],
    [90003,10001,3,1,380,270,1.3],
    [90004,10001,999,1,100,40,0],
    [90005,99999,1,1,850,610,0],
],columns=items_df.columns)],ignore_index=True)
orders_df.to_csv(BASE/'raw_orders.csv',index=False)
items_df.to_csv(BASE/'raw_order_items.csv',index=False)
print(f'Generated {len(customers_df)} customers, {len(orders_df)} raw orders, {len(items_df)} raw order lines.')
print('Source files include intentional quality issues; see README and analysis.py.')
