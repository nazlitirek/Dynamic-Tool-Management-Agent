# main_agent.py
# Zero-knowledge başlayan, araçları dinamik olarak keşfeden ana ajan
import time
import os
import json
from typing import Any
from dotenv import load_dotenv
from groq import Groq
from groq.types.chat import ChatCompletionToolParam
from tool_manager import search_tools

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

SYSTEM_PROMPT = """Sen bir görev çözücü yapay zeka asistanısın.Her zaman türkçe yanıt ver.

ÖNEMLİ KURALLAR:
1. Başlangıçta hiçbir araca erişimin YOKTUR.
2. Bir görevi çözmek için önce tool_search fonksiyonunu çağırarak uygun araçları keşfet.
3. tool_search sana araçların şemalarını döndürecek, ondan sonra o araçları kullanabilirsin.
4. Sana şemada verilmeyen bir aracı ASLA icat etme veya kullanmaya çalışma.
5. Eğer görev için uygun araç bulunamazsa, verecek bir cevap bulamazsan bunu kullanıcıya dürüstçe söyle.
6. Araç sonuçlarını kullanıcıya anlamlı ve akıcı bir şekilde açıkla."""

TOOL_SEARCH_SCHEMA: ChatCompletionToolParam = {
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
            "required": ["query"],
            "additionalProperties": False
        }
    }
}


def format_tool_for_groq(tool: dict) -> Any:
    params = tool["parameters"].copy()
    params["additionalProperties"] = False
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": params
        }
    }


def execute_tool(tool_name: str, tool_input: dict) -> str:
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

    messages: list[Any] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    available_tools: list[Any] = [TOOL_SEARCH_SCHEMA]
    final_text = ""
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        response = None
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    tools=available_tools,
                    tool_choice="auto",
                    max_tokens=4096
                )
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  ⚠️ API hatası, tekrar deneniyor ({attempt + 1}/{max_retries})...")
                    time.sleep(2)
                else:
                    print(f"  ❌ API hatası: {e}")
                    return final_text

        if response is None:
            return final_text

        choice = response.choices[0]
        message = choice.message

        # Asistanın cevabını geçmişe ekle
        tool_calls_data = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            }
            for tc in (message.tool_calls or [])
        ]

        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": tool_calls_data if tool_calls_data else None
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

    print("\n✅ BAŞARILI SENARYOLAR")
    successful_scenarios = [
    "İstanbul'un hava durumu nasıl?",           # get_weather
    "Son depremleri listeler misin?",            # get_earthquakes
    "AAPL hisse senedi fiyatı nedir?",           # get_stock_price
    "Inception filmi hakkında bilgi ver",        # get_movie_info
    "8.8.8.8 IP adresi hangi ülkeye ait?",      # ip_lookup
    "Teknoloji haberleri neler?",                # get_news
    "Bana bir programcı şakası anlat",           # get_joke
    "Tokyo'da şu an saat kaç?",                  # get_world_time
    "Atatürk hakkında kısa bilgi ver",           # search_wikipedia
    "100 dolar kaç türk lirası eder?",           # currency_converter
    "Python'da 1'den 100'e kadar sayıların toplamını hesapla",  # execute_code
]

    for scenario in successful_scenarios:
        run_agent(scenario)
        print()

    print("\n❌ BAŞARISIZ SENARYOLAR (Sistemde Araç Yok)")
    failed_scenarios = [
        "Bana uçak bileti bul",
        "Pizza tarifi ver",
        "Otel rezervasyonu yap",
        "Spotify'da şarkı çal",
        "Instagram hesabımı aç",
    ]

    for scenario in failed_scenarios:
        run_agent(scenario)
        print()