"""Частотний аналіз літер. Варіант 7. Python 3.10+."""

import unicodedata
import argparse
import contextlib
import io
from vendor.zanalyze_histogram import print_histogram
import sys
from pathlib import Path
from scaling import scale_bars

def count_letters(text):
    counts = {}
    for char in unicodedata.normalize("NFC", text).lower():
        if char.isalpha():
            counts[char] = counts.get(char, 0) + 1
    return dict(sorted(counts.items()))

def render_histogram(counts, min_count=1, chart_style="ascii"):
    """Відібрати частоти включно з порогом і масштабувати стовпчики до 50.

    counts зіставляє літери з додатними цілими частотами, як count_letters.
    Порожній counts дає лише повідомлення про відсутність літер. Для
    непорожнього counts початкові підсумки зберігаються навіть тоді, коли
    поріг приховує всі літери; тоді показано нуль різних літер.
    Вхідний словник не змінюється.
    """
    if type(min_count) is not int or min_count < 1:
        raise ValueError("Поріг частоти має бути цілим числом від 1.")
    if not counts:
        return "Літер не знайдено."
    visible = {letter: count for letter, count in counts.items() if count >= min_count}
    if not visible:
        return "\n".join([
            f"Літер із частотою не меншою за {min_count} не знайдено.",
            f"Усього літер: {sum(counts.values())}; різних: {len(counts)}",
            f"Показано різних літер: 0; поріг: {min_count}.",
        ])
    if chart_style == "blocks":
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            print_histogram("Частоти літер (zanalyze)", sorted(visible.items()),
                            sum(counts.values()), "Літера", width=50)
        result = output.getvalue().rstrip("\n")
        result += f"\nУсього літер: {sum(counts.values())}; різних: {len(counts)}"
        if len(visible) != len(counts):
            result += f"\nПоказано різних літер: {len(visible)}; поріг: {min_count}."
        return result
    if chart_style != "ascii":
        raise ValueError("Невідомий стиль діаграми.")
    widths = scale_bars(list(value for _, value in sorted(visible.items())))
    lines = [f"Літера | Діаграма (максимум 50 символів; поріг: {min_count}) | Кількість"]
    for (letter, count), width in zip(sorted(visible.items()), widths):
        lines.append(f"{letter} {'#' * width} {count}")
    lines.append(f"Усього літер: {sum(counts.values())}; різних: {len(counts)}")
    if len(visible) != len(counts):
        lines.append(f"Показано різних літер: {len(visible)}; поріг: {min_count}.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Підрахунок літер і символьна діаграма частот.")
    parser.add_argument("--file", type=Path, help="Шлях до текстового файлу UTF-8")
    parser.add_argument("--min-count", type=int, default=1, help="Мінімальна частота літери (ціле число від 1)")
    parser.add_argument("--chart-style", choices=["ascii", "blocks"], default="ascii",
                        help="Стиль діаграми: # або блоки zanalyze (zlib)")
    args = parser.parse_args(argv)
    if args.min_count < 1:
        parser.error("Поріг частоти має бути цілим числом від 1.")
    try:
        text = args.file.read_text(encoding="utf-8-sig") if args.file else input("Введіть текст: ")
    except UnicodeError:
        print("Помилка: файл має бути збережений у UTF-8.", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"Помилка читання файлу: {error.strerror or error}.", file=sys.stderr)
        return 2
    except (EOFError, KeyboardInterrupt):
        print("Помилка: ввід перервано або текст не надано.", file=sys.stderr)
        return 2
    if not text.strip():
        print("Помилка: введіть непорожній текст із літерами.", file=sys.stderr)
        return 2
    counts = count_letters(text)
    if not counts:
        print("Помилка: текст не містить літер; цифри й розділові знаки не враховуються.", file=sys.stderr)
        return 2
    print(render_histogram(counts, args.min_count, args.chart_style))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
