from pydantic import BaseModel
from typing import Optional


# request validation
class ProcessRequest(BaseModel):
    # make file ID optional.
    file_id: str = None
    chunk_size: Optional[int] = 100
    chunk_overlap: Optional[int] = 20
    do_reset: Optional[int] = 0
