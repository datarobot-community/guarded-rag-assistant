This directory contains an example of fully customizable RAG chunking
and vector db building logic. To use this directory with your deployed 
stack, ensure you have set `rag_type` to `RAGType.DIY` in 
`/infra/settings_main.py` before running `pulumi up`. To also customize
the retrieval logic, edit `deployment_diy_rag/custom.py` after updating the
aforementioned setting.