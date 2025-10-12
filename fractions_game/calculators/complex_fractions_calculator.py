import random
from fractions import Fraction

# ---------- вспомогательные ----------

def _comma(x: float, ndigits: int | None = None) -> str:
    """Число -> строка с запятой: 1.25 -> '1,25' (опционально округлить)"""
    if ndigits is not None:
        x = round(x, ndigits)
    s = f"{x}"
    return s.replace(".", ",")

def _mix(n: int, num: int, den: int) -> Fraction:
    """Смешанное число n num/den -> Fraction"""
    return Fraction(n) + Fraction(num, den)

def _to_float(fr: Fraction) -> float:
    return float(fr.numerator) / float(fr.denominator)

def _eval_safe(val) -> Fraction:
    """Любое число/Fraction -> Fraction"""
    if isinstance(val, Fraction):
        return val
    return Fraction(val).limit_denominator()

# ---------- генерация 5 типов ----------

def generate_complex_fractions():
    """
    Ровно 5 задач (в фиксированном порядке) по образцам:
      1) (a − 1/b) : 1/c + (11/16 + d) : 3
      2) a : (p/q) + (r/s) : 0,125 + 4 1/2 · 0,8
      3) (4 1/8 − 0,004 · 300) : 0,0015 + (4 1/5 − 3 1/2) : 10
      4) (3,625 + 0,25 + 2 3/4) : (28,75 + 92 1/4 − 15) : 0,0625
      5) ((1/2 + 0,4 + 0,375) · 2/5) / (75 · 2/5)
    """
    tasks = []

    # ---- Тип 1 ----  (2,314 − 1/4) : 1/50 + (11/16 + 0,7125) : 3
    a = round(random.uniform(1.200, 3.900), 3)     # как 2,314
    b = random.choice([3, 4, 5, 8])                # 1/4 и подобные
    c = random.choice([25, 50, 100])               # 1/50 как в примере
    d = random.choice([0.3125, 0.625, 0.7125, 0.9375])  # “шестнадцатные” доли
    expr_text_1 = f"({_comma(a,3)} − 1/{b}) : 1/{c} + (11/16 + {_comma(d,4)}) : 3"

    # вычисление
    val1 = (_eval_safe(a) - Fraction(1, b)) / Fraction(1, c) + (Fraction(11, 16) + _eval_safe(d)) / 3
    tasks.append({
        "task": expr_text_1 + "",
        "answer": round(_to_float(val1), 6),
        "type": "type1"
    })

    # ---- Тип 2 ----  1,456 : 7/25 + 5/16 : 0,125 + 4 1/2 · 0,8
    a2 = round(random.uniform(1.200, 1.800), 3)    # ~1,456
    p, q = random.choice([(7,25), (9,20), (11,40)])  # простые доли
    r, s = random.choice([(5,16), (3,20), (7,32)])
    const_0125 = 0.125
    mix = _mix(4, 1, 2)   # 4 1/2
    m08 = 0.8
    expr_text_2 = f"{_comma(a2,3)} : {p}/{q} + {r}/{s} : {_comma(const_0125,3)} + 4 1/2 · {_comma(m08,1)}"
    val2 = _eval_safe(a2) / Fraction(p, q) + Fraction(r, s) / _eval_safe(const_0125) + mix * _eval_safe(m08)
    tasks.append({
        "task": expr_text_2 + "",
        "answer": round(_to_float(val2), 6),
        "type": "type2"
    })

    # ---- Тип 3 ---- (4 1/8 − 0,004 · 300) : 0,0015 + (4 1/5 − 3 1/2) : 10
    mix41_8 = _mix(4,1,8)
    dec_0004 = 0.004
    mult_300 = random.choice([300, 250, 200])  # близкие масштабы
    dec_0015 = 0.0015
    mix41_5 = _mix(4,1,5)
    mix31_2 = _mix(3,1,2)
    expr_text_3 = f"(4 1/8 − {_comma(dec_0004,3)} · {mult_300}) : {_comma(dec_0015,4)} + (4 1/5 − 3 1/2) : 10"
    val3 = (mix41_8 - _eval_safe(dec_0004) * mult_300) / _eval_safe(dec_0015) + (mix41_5 - mix31_2) / 10
    tasks.append({
        "task": expr_text_3 + "",
        "answer": round(_to_float(val3), 6),
        "type": "type3"
    })

    # ---- Тип 4 ---- (3,625 + 0,25 + 2 3/4) : (28,75 + 92 1/4 − 15) : 0,0625
    a4 = random.choice([3.625, 2.875, 3.375])      # как 3,625
    b4 = 0.25
    mix2_3_4 = _mix(2,3,4)                          # 2 3/4
    left = _eval_safe(a4) + _eval_safe(b4) + mix2_3_4

    A = random.choice([28.75, 27.5, 29.0])          # как 28,75
    B = _mix(92,1,4)                                # 92 1/4
    C = 15
    right = (_eval_safe(A) + B - _eval_safe(C))
    den = _eval_safe(0.0625)                        # 1/16

    expr_text_4 = f"({_comma(a4,3)} + {_comma(b4,2)} + 2 3/4) : ({_comma(A,2)} + 92 1/4 − {C}) : {_comma(0.0625,4)}"
    val4 = left / right / den
    tasks.append({
        "task": expr_text_4 + "",
        "answer": round(_to_float(val4), 6),
        "type": "type4"
    })

    # ---- Тип 5 ---- ((1/2 + 0,4 + 0,375) · 2/5) / (75 · 2/5)
    part1 = Fraction(1,2) + _eval_safe(0.4) + _eval_safe(0.375)
    two_five = Fraction(2,5)
    num = part1 * two_five
    denom_left = 75 * two_five
    expr_text_5 = f"((1/2 + {_comma(0.4,1)} + {_comma(0.375,3)}) · 2/5) / (75 · 2/5)"
    val5 = num / denom_left
    tasks.append({
        "task": expr_text_5 + "",
        "answer": round(_to_float(val5), 6),
        "type": "type5"
    })

    return tasks


# ---------- проверка ----------

def _parse_user_number(s: str) -> float | None:
    """
    Принимает: '3,25', '3.25', '1/4', '2 3/5'
    Возвращает float или None.
    """
    try:
        s = s.strip().replace("−", "-")
        # смешанная дробь 'a b/c'
        if " " in s and "/" in s:
            whole, frac = s.split()
            num, den = frac.split("/")
            val = Fraction(int(whole), 1) + Fraction(int(num), int(den))
            return float(val)
        # простая дробь 'a/b'
        if "/" in s:
            num, den = s.split("/")
            return float(Fraction(int(num), int(den)))
        # десятичная с запятой/точкой
        s = s.replace(",", ".")
        return float(s)
    except Exception:
        return None

def check_complex_fraction(user_answer, correct_answer, task_type):
    """
    Сравнение с допуском. Разрешаем ввод десятичным числом,
    обычной или смешанной дробью.
    """
    val = _parse_user_number(user_answer)
    if val is None:
        return False
    return abs(val - float(correct_answer)) <= 1e-2  # ~0.01

def check_complex_fractions(tasks, user_answers):
    results = []
    for i, task in enumerate(tasks):
        if i < len(user_answers):
            results.append(check_complex_fraction(user_answers[i], task["answer"], task["type"]))
        else:
            results.append(False)
    return results