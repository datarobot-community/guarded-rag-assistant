This directory contains an example of fully customizable RAG retrieval
logic. To use this directory with your deployed stack, ensure
you have set `rag_type` to `RAGType.DIY` in `/infra/settings_main.py` 
before running `pulumi up`. To also customize the document chunking, 
and vectorization, edit `notebooks/build_rag.ipynb` after updating the
aforementioned setting.