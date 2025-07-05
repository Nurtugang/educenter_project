import random
import re

def format_equation(equation):
	# Шаг 1: Убираем множитель 1 перед переменными
	equation = re.sub(r'(\b1) \* ([a-zA-Z])', r'\2', equation)
	
	# Шаг 2: Убираем знак умножения между числами и переменными или скобками
	equation = re.sub(r'(\d) \* \(', r'\1(', equation)  # Число перед скобкой
	equation = re.sub(r'(\d) \* ([a-zA-Z])', r'\1\2', equation)  # Число перед переменной
	
	# Убираем лишние пробелы вокруг скобок
	equation = re.sub(r'\s*\(\s*', '(', equation)
	equation = re.sub(r'\s*\)\s*', ')', equation)
	
	return equation

def find_single_letter_in_equation(equation):
	# Поиск первой буквы в уравнении
	match = re.search(r'[a-zA-Z]', equation)
	return match.group(0) if match else None


def generate_equations():
	equations = []
	# 1. ax + b = c
	var1 = 'a'
	while 1:
		a, b, c = random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)
		sign1 = random.choice(('+', '-'))
		eq1 = f'{a} * {var1} {sign1} {b} = {c}'
		solution = float(solve(eq1))
		if solution is not None and solution.is_integer():
			break 

	# 2. a(bx + c) + d = e(fx + g) + h
	var2 = 'b'
	while 1:
		sign1, sign2, sign3, sign4 = random.choice(('+', '-')), random.choice(('+', '-')), random.choice(('+', '-')), random.choice(('+', '-'))
		a, b, c, d, e, f, g, h = random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 20), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 20)
		eq2 = f'{a} * ({b} * {var2} {sign1} {c}) {sign2} {d} = ({e} * ({f} * {var2} {sign3} {g}) {sign4} {h})'
		solution = solve(eq2)
		if solution is not None and solution.is_integer():
			break 
	# 3. ax + b(cx - d) = e(f - gx) + hx + i
	var3 = 'c'
	while 1:
		sign1, sign2, sign3, sign4 = random.choice(('+', '-')), random.choice(('+', '-')), random.choice(('+', '-')), random.choice(('+', '-'))
		a, b, c, d, e, f, g, h, i = random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)
		eq3 = f'{a} * {var3} {sign1} {b} * ({c} * {var3} {sign2} {d}) = ({e} * ({f} - {g} * {var3}) {sign3} {h} * {var3} {sign4} {i})'
		solution = solve(eq3)
		if solution is not None and solution.is_integer():
			break 

	# 4. ax + b(cx - d) = -e(fx + g) - h
	var4 = 'd'
	while 1:
		sign1, sign2, sign3 = random.choice(('+', '-')), random.choice(('+', '-')), random.choice(('+', '-'))
		a, b, c, d, e, f, g, h = random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 20)
		eq4 = f'{a} * {var4} + {b} * ({c} * {var4} {sign1} {d}) = ({-1*e} * ({f} * {var4} {sign2} {g}) {sign3} {h})'
		solution = solve(eq4)
		if solution is not None and solution.is_integer():
			break 

	# 5. a(bx - c(dx + e)) = f - g(h + ix) - j
	var5 = 'x'
	while 1:
		sign1, sign2, sign3 = random.choice(('+', '-')), random.choice(('+', '-')), random.choice(('+', '-'))
		a, b, c, d, e, f, g, h, i, j = random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 10), random.randint(1, 20), random.randint(1, 10), random.randint(1, 20), random.randint(1, 10), random.randint(1, 10)
		eq5 = f'{a} * ({b} * {var5} - {c} * ({d} * {var5} {sign1} {e})) = ({f} - {g} * ({h} {sign2} {i} * {var5}) {sign3} {j})'
		solution = solve(eq5)
		if solution is not None and solution.is_integer():
			break 

	# 6. ax + b = cx + d
	var6 = 'y'
	while 1:
		sign1, sign2 = random.choice(('+', '-')), random.choice(('+', '-'))
		a, b, c, d = random.randint(1, 10), random.randint(1, 20), random.randint(1, 10), random.randint(1, 20)
		eq6 = f'{a} * {var6} {sign1} {b} = ({c} * {var6} {sign2} {d})'
		solution = solve(eq6)
		if solution is not None and solution.is_integer():
			break 

	equations.append(eq1)
	equations.append(eq2)
	equations.append(eq3)
	equations.append(eq4)
	equations.append(eq5)
	equations.append(eq6)
	
	return equations

def solve(equation): 
	letters_found = find_single_letter_in_equation(equation)
	s1 = equation.replace(letters_found, 'j') 
	s2 = s1.replace('=', '-(') 
	s = s2+')'
	z = eval(s, {'j': 1j}) 
	real, imag = z.real, -z.imag 
	if imag: 
		return real/imag 
	else: 
		if real: 
			return None
		else: 
			return None



