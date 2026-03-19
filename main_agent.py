# main_agent.py
# Zero-knowledge başlayan, araçları dinamik olarak keşfeden ana ajan

import os
import json
from dotenv import load_dotenv
from groq import Groq
from tool_manager import search_tools
from typing import Any

from groq.types.chat import ChatCompletionToolParam
from tools.weather import get_weather
from tools.earthquake import get_earthquakes
from tools.stock import get_stock_price
from tools.movie import get_movie_info
from tools.ip_lookup import ip_lookup
from tools.news import get_news
from tools.joke import get_joke
from tools.world_clock import get_world_time
from tools.wikipedia import search_wikipedia
from tools.currency import currency_converter
from tools.calculator import execute_code

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY ortam değişkeni ayarlanmadı.")

client = Groq(api_key=api_key)

TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "get_earthquakes": get_earthquakes,
    "get_stock_price": get_stock_price,
    "get_movie_info": get_movie_info,
    "ip_lookup": ip_lookup,
    "get_news": get_news,
    "get_joke": get_joke,
    "get_world_time": get_world_time,
    "search_wikipedia": search_wikipedia,
    "currency_converter": currency_converter,
    "execute_code": execute_code,
}

SYSTEM_PROMPT = """Sen bir görev çözücü yapay zeka asistanısın.

ÖNEMLİ KURALLAR:
1. Başlangıçta hiçbir araca erişimin YOKTUR.
2. Sadece gerçek bir görev veya bilgi talebi varsa tool_search çağır.
3. Selamlama, sohbet veya kişisel sorular için KESİNLİKLE tool_search ÇAĞIRMA, direkt yanıt ver.
4. Bir görevi çözmek için önce tool_search fonksiyonunu çağırarak uygun araçları keşfet.
5. tool_search sana araçların şemalarını döndürecek, sadece ondan sonra o araçları kullanabilirsin.
6. Sana şemada verilmeyen bir aracı ASLA icat etme veya kullanmaya çalışma.
7. Eğer görev için uygun araç bulunamazsa kullanıcıya dürüstçe söyle.
8. Araç sonuçlarını kullanıcıya anlamlı ve akıcı bir şekilde açıkla."""

# tool_search şeması — Groq formatında
TOOL_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "tool_search",
        "description": "Görevi çözmek için gereken araçları arar ve şemalarını döndürür. Herhangi bir araç kullanmadan önce bunu çağırmalısın.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Hangi yeteneğe ihtiyacın olduğunu anlatan sorgu, örnek: 'hava durumu öğren'"
                }
            },
            "required": ["query"]
        }
    }
}


def format_tool_for_groq(tool: dict) -> Any:
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"]
        }
    }


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Araç adına göre ilgili fonksiyonu çağırır."""
    if tool_name not in TOOL_FUNCTIONS:
        return json.dumps({
            "success": False,
            "error": f"'{tool_name}' adlı araç bulunamadı."
        }, ensure_ascii=False)

    try:
        func = TOOL_FUNCTIONS[tool_name]
        result = func(**tool_input)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)


def run_agent(user_message: str) -> str:
    print(f"\n{'='*60}")
    print(f"👤 Kullanıcı: {user_message}")
    print(f"{'='*60}")

    # Mesaj geçmişi
    messages: list[Any] = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_message}
    ]

    # Başlangıçta sadece tool_search mevcut
    available_tools: list[Any] = [TOOL_SEARCH_SCHEMA]
    final_text = ""
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=available_tools,
            tool_choice="auto",
            max_tokens=4096
        )

        message = response.choices[0].message

        # Asistanın cevabını geçmişe ekle
        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            }
            for tc in (message.tool_calls or [])
        ] or None
        })

        # Araç çağrısı yoksa bitir
        if not message.tool_calls:
            final_text = message.content or ""
            print(f"\n🤖 Agent: {final_text}")
            break

        # Araç çağrılarını işle
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)

            print(f"\n🔧 Araç çağrısı: {tool_name}({tool_input})")

            if tool_name == "tool_search":
                query = str(tool_input.get("query", "")).strip()

                if not query:
                    result_text = json.dumps({
                        "found": False,
                        "tools": [],
                        "message": "Boş araç arama sorgusu."
                    }, ensure_ascii=False)
                else:
                    found_tools = search_tools(query)

                    if found_tools:
                        for t in found_tools:
                            formatted = format_tool_for_groq(t)
                            if formatted["function"]["name"] not in [
                                x["function"]["name"] for x in available_tools
                            ]:
                                available_tools.append(formatted)

                        result_text = json.dumps({
                            "found": True,
                            "tools": [{"name": t["name"], "description": t["description"]} for t in found_tools],
                            "message": f"{len(found_tools)} araç bulundu ve kullanıma hazır."
                        }, ensure_ascii=False, indent=2)

                        print(f"  ✓ tool_search sonucu: {[t['name'] for t in found_tools]}")
                    else:
                        result_text = json.dumps({
                            "found": False,
                            "tools": [],
                            "message": "Bu görev için uygun araç bulunamadı."
                        }, ensure_ascii=False)
            else:
                result_text = execute_tool(tool_name, tool_input)
                print(f"  ✓ {tool_name} sonucu alındı")

            # Araç sonucunu geçmişe ekle
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result_text
            })

    if iteration >= max_iterations:
        print(f"\n⚠️ Maksimum iterasyona ulaşıldı.")

    return final_text


if __name__ == "__main__":
    from tool_manager import build_index
    build_index()

    test_queries = [
        "İstanbul'un hava durumu nasıl?",
        "100 dolar kaç türk lirası eder?",
        "Son depremleri listeler misin?",
        
            
    ]

    for query in test_queries:
        result = run_agent(query)
        print(f"\n{'='*60}\n")