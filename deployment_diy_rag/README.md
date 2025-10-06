This directory contains an example of fully customizable RAG retrieval
logic. To use this directory with your deployed stack, ensure
you have set `rag_type` to `RAGType.DIY` in `/infra/settings_main.py` 
before running `pulumi up`. To also customize the document chunking, 
and vectorization, edit `notebooks/build_rag.ipynb` after updating the
aforementioned setting.

## Important Note

**Metadata Filtering:** The metadata filtering feature available in the Streamlit 
frontend (`frontend/app.py`) is currently only supported when using `RAGType.DR` 
(DataRobot's managed Vector Database). If you switch to `RAGType.DIY`, the metadata 
filters in the UI will not affect document retrieval unless you implement custom 
filtering logic in `custom.py` to handle the `metadata_filter` parameter from 
`extra_body` in the OpenAI-compatible API request.
