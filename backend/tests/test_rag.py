from app.services.rag import KnowledgeService

def test_chunking_overlap_and_empty():
    assert KnowledgeService.split("") == []
    chunks=KnowledgeService.split("a"*1500,size=700,overlap=100)
    assert len(chunks)==3
    assert len(chunks[0])==700
