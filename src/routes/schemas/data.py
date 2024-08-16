from pydantic import BaseModel
from typing import Optional


# request validation
class ProcessRequest(BaseModel):
    file_id: str
    # optional with default
    chunk_size: Optional[int] = 100
    chunk_overlap: Optional[int] = 20
    # perfix do for action behind property
    do_reset: Optional[int] = 0
