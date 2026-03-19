# tools/calculator.py

def execute_code(code: str) -> dict:
    """
    Python kodu çalıştırarak matematiksel hesaplama yapar.
    Gerçek zamanlı çalışır, API gerekmez.
    """
    try:
        local_vars = {}
        exec(code, {"__builtins__": {"print": print, "range": range, "len": len,
                                      "sum": sum, "min": min, "max": max,
                                      "abs": abs, "round": round, "int": int,
                                      "float": float, "str": str, "list": list}}, local_vars)
        
        result = local_vars.get("result", "Kod çalıştı fakat 'result' değişkeni tanımlanmadı.")
        
        return {
            "success": True,
            "code": code,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "code": code,
            "error": str(e)
        }