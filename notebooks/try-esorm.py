# %%
from bgm_archive.es.subjects_index import SubjectsIndex
from bgm_archive.es.conn import get_async_client

si = SubjectsIndex(get_async_client(), 'subjects')
# %%
await si.recreate_index()


# %%
