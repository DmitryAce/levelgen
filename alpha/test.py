import sys
import subprocess


def get_stdin():
    return '\n'.join(line for line in sys.stdin)


def run(data, path='program.py', timeout=5):
    try:
        p = subprocess.run(
            ['python', path],
            input=repr(data),
            capture_output=True,
            encoding='utf8',
            timeout=timeout
        )
        return p.stdout, p.stderr
    except:
        return '', 'Превышено время ожидания результата'


def format_result(task, x):
    if 0 <= task <= 4:
        return '%.2e' % x
    return repr(x)


def check_func(task, tests, code):
    if task == 12:
        res, err = run((task, tests, code), path='check_solution.py', timeout=60)
        try:
            out = eval(res)
            if type(out) is not bool:
                return False, ('', err or 'Неверный формат вывода', [])
        except Exception:
            return False, ('', err or 'Неверный формат вывода', [])

        if not out:
            return False, ('', err or 'Ошибка разбора решения', [])
    if task == 10:
        cov, err = run((task, None, code), path='check_coverage.py')
        try:
            c = round(float(cov), 4)
        except ValueError:
            return False, ('', err or 'Ошибка разбора результата (print в коде?)', [])
        if c < 100:
            return False, ('', f'Недостаточное тестовое покрытие ветвей ({c}%)', [])
    for test in tests:
        args, y = test
        out, err = run((task, args, code))
        if out != format_result(task, y):
            return False, (out, err, args)
    return True, None


if __name__ == '__main__':
    task, tests, code = eval(get_stdin())
    if 0 <= task <= 12:
        state = check_func(task, tests, code)
    else:
        state = False, ('', 'Неизвестная задача', None)
    print(state, end='')
