import yaml
import datetime

import pandas as pd

CONTRACT_CODE2MONTH = {'F':1, 'G':2, 'H':3, 'J':4, 'K':5,  'M':6, 'N':7, 'Q':8, 'U':9, 'V':10, 'X':11, 'Z':12}

def int2dt(dt, format_='%Y%m%d'):
  return datetime.datetime.strptime(str(dt), format_)

def dt2int(dt, format_='%Y%m%d'):
  return int(datetime.datetime.strftime(dt, format=format_))

def read_yaml(path_):
  with open(path_, 'r') as file:
    co = yaml.safe_load(file)
  return co

def get_exps(conf_file, cals_, from_, to_):
  yaml_ = read_yaml(conf_file)
  cals = yaml_[cals_]                                                                                                              
  res = None
  
  for cal in cals:
    dts =  pd.DataFrame(pd.date_range(str(from_), str(to_), freq=cals[cal]['freq']), columns=['exp'])
    # NOTE: should not be necessary if freq was correct. Need to approx. sometime though.
    dts['contract_code'] = dts.exp.map(lambda x: list(CONTRACT_CODE2MONTH.keys())[x.month-1])
    if not cals[cal]['months'] is None:
      dts['check'] = dts.contract_code.map(lambda x: x in cals[cal]['months'])
      dts = dts[dts.check]                                                                                                                                       
    dts.exp = dts.exp.map(dt2int)
    dts['year'] = dts.exp // 10000 
    dts['cal'] = cal                                                                                                                                             
    if res is None:
      res = dts 
    else:    
      res = pd.concat([res, dts], axis=0)
  res = res.merge(get_cals(yaml_[f'{cals_}_fut']), left_on='cal', right_on='cal') 
  assert (res['check']==True).all() 
  del res['check']                                                                                                                                               
  return res  

def get_cals(conf):
  l  = [ (k,v.split(',')) for k,v in conf.items()]
  res = []   
  for i in l:
    for j in i[1]:
      res.append( (i[0],j) )
  return pd.DataFrame(data=res, columns=['cal','root_symbol'])

