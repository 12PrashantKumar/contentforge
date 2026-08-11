from dataclasses import dataclass
from datetime import datetime

@dataclass
class Finding:
    title:str
    content : str
    source_url : str
    source_type: str
    fetched_at : datetime
    source_id :str = ''
