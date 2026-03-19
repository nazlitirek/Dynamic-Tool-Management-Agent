# tool_manager.py
import os
from urllib import response
from dotenv import load_dotenv
import json
import chromadb
from sentence_transformers import SentenceTransformer
from tool_registry import get_all_tools, get_tool_by_name
from groq import Groq

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# Modelleri başlat
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.Client()

# ChromaDB koleksiyonu oluştur
collection = chroma_client.get_or_create_collection(name="tools")

def build_index():
    """
    Tool Registry'deki tüm araçları embedding'e çevirip
    ChromaDB'ye kaydeder. Sistem başlarken bir kez çalışır.
    """
    tools = get_all_tools()
    
    # Koleksiyonu temizle (yeniden build için)
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])
    
    documents = []
    metadatas = []
    ids = []
    
    for tool in tools:
        # Embedding için zengin metin oluştur
        doc_text = f"{tool['name']} {tool['description']} {' '.join(tool['tags'])}"
        documents.append(doc_text)
        metadatas.append({
            "name": tool["name"],
            "categories": ",".join(tool["category"]),
            "tags": ",".join(tool["tags"])
        })
        ids.append(tool["name"])
    
    # Embedding'leri hesapla ve kaydet
    embeddings = embedding_model.encode(documents).tolist()
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print(f"✓ {len(tools)} araç index'e eklendi.")


def keyword_filter(query: str) -> list:
    """
    Katman 1: Keyword ve kategori bazlı hızlı eleme.
    Query'deki kelimeleri araçların tag ve kategorileriyle karşılaştırır.
    100 araçtan ilgili ~10'u seçer.
    """
    tools = get_all_tools()
    query_words = set(query.lower().split())
    
    scored_tools = []
    for tool in tools:
        score = 0
        tool_keywords = set(tool["tags"] + tool["category"])
        
        for word in query_words:
            for keyword in tool_keywords:
                if word in keyword or keyword in word:
                    score += 1
        
        if score > 0:
            scored_tools.append((tool["name"], score))
    
    # Skora göre sırala, en yüksek önce
    scored_tools.sort(key=lambda x: x[1], reverse=True)
    
    # Eşleşen araç isimlerini döndür (max 8)
    filtered_names = [name for name, _ in scored_tools[:8]]
    
    print(f"  [Katman 1] '{query}' → {len(filtered_names)} araç kaldı: {filtered_names}")
    return filtered_names


def semantic_search(query: str, candidate_names: list, top_k: int = 5) -> list:
    """
    Katman 2: Semantic search.
    Sadece Katman 1'den gelen adaylar arasında embedding benzerliği yapar.
    """
    if not candidate_names:
        # Katman 1 hiçbir şey bulamadıysa tüm koleksiyonda ara
        candidate_names = [t["name"] for t in get_all_tools()]
    
    query_embedding = embedding_model.encode([query]).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, len(candidate_names)),
        where={"name": {"$in": candidate_names}}
    )
    
    found_names = results["ids"][0] if results["ids"] else []
    print(f"  [Katman 2] Semantic search → {found_names}")
    return found_names

def llm_reranker(query: str, candidate_names: list) -> list:
    """
    Katman 3: LLM Reranker.
    Groqa sorar: bu görev için hangi araçlar gerçekten gerekli?
    False positive'leri eler, halüsinasyonu önler.
    """
    if not candidate_names:
        return []
    
    candidates_info = []
    for name in candidate_names:
        tool = get_tool_by_name(name)
        if tool:
            candidates_info.append({
                "name": tool["name"],
                "description": tool["description"]
            })
    
    prompt = f"""Kullanıcının görevi: "{query}"

Aşağıdaki araç adayları var:
{json.dumps(candidates_info, ensure_ascii=False, indent=2)}

Bir tool seçerken, sadece gerçekten görevi çözmek için gerekli olanları seç. Gereksiz araçları dahil etme.
Eğer hiçbir araç bu görevi çözemiyorsa boş liste döndür: []
Gereksiz araçları dahil etme.
Sadece JSON array döndür, başka hiçbir şey yazma.

Örnek: ["get_weather", "translator"]"""
    response = groq_client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=200
)
    raw = (response.choices[0].message.content or "").strip()

    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        selected = json.loads(raw)
        print(f"  [Katman 3] LLM Reranker → {selected}")
        return selected
    except json.JSONDecodeError:
        print(f"  [Katman 3] Parse hatası, Katman 2 sonuçları kullanılıyor.")
        return candidate_names
def search_tools(query: str) -> list:
    """
    Ana arama fonksiyonu.
    3 katmanı sırayla çalıştırır ve sonuçta
    görev için uygun araçların tam şemalarını döndürür.
    """
    print(f"\n🔍 Araç aranıyor: '{query}'")
    
    # Katman 1: Keyword filter
    candidates = keyword_filter(query)
    
    # Katman 2: Semantic search
    candidates = semantic_search(query, candidates)
    
    # Katman 3: LLM reranker
    final_names = llm_reranker(query, candidates)
    
    # Seçilen araçların tam şemalarını getir
    final_tools = []
    for name in final_names:
        tool = get_tool_by_name(name)
        if tool:
            final_tools.append(tool)
    
    print(f"  ✓ Sonuç: {[t['name'] for t in final_tools]}\n")
    return final_tools