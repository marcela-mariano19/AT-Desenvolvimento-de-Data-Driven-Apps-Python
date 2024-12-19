import json
import pandas as pd
import numpy as np
from copy import copy

from orjson import dumps as to_json
from statsbombpy import sb
from typing import List



#Usado como base o código que o professor passou em aula
def get_events(match_id: int) -> str:
    events = sb.events(match_id=match_id, split=True, flatten_attrs=False)
    full_events = pd.concat([v for _, v in events.items()])
    return to_json([
        {k: v for k, v in event.items() if v is not np.nan} 
        for event in full_events.sort_values(by="minute").to_dict(orient='records')
    ])


def get_lineups(match_id: int) -> str:
    data = sb.lineups(match_id=match_id)
    data_final = copy(data)
    list_fields = ['cards', 'positions']
    for field in list_fields:
        for key, df in data.items():
            df[field] = df[field].apply(lambda v: {field: v})
            data_final[key] = df.to_dict(orient='records')
    return to_json(data_final)