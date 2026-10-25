# -*- coding: utf-8 -*-
"""
Проверка публичных текстов сайта Fatumon на стоп-слова.

Запуск (из C:\\claude\\token):
    python -I site/tools/check_texts.py            # все i18n/*.json и *.html
    python -I site/tools/check_texts.py --strict   # то же, но и слова «под вопросом»

Проходит i18n/ru.json, i18n/en.json (значения), README.md (без ссылок и тегов)
и все HTML сайта (текст и атрибуты content / alt / title / aria-label / placeholder). Без учёта регистра,
кроме отдельно помеченных правил. Выводит таблицу «файл · ключ/строка · найдено»
и итог; код выхода 1, если что-то найдено.

Список STOP_WORDS — константа ниже: (метка, регулярка, флаги). Источник —
базовый список координатора + итоговый раздел «Стоп-слова» из
docs/ПРАВИЛА_юридические_v1.md (43 строки).
"""
import re
import sys
import json
from html.parser import HTMLParser
from pathlib import Path

I = re.IGNORECASE

# ---------------------------------------------------------------------------
# СТОП-СЛОВА: (метка группы, регулярное выражение, флаги)
# ---------------------------------------------------------------------------
STOP_WORDS = [
    # --- 1–2. Цена ---
    ("цена",            r"\bцен[аыеу]\b|\bцены\b|\bцено[йю]\b", I),
    ("price",           r"\bprices?\b|price\s+(prediction|target)", I),
    ("прогноз цены",    r"прогноз\w*\s+цен\w*|целев\w*\s+цен\w*|цен\w*\s+(вырастет|поднимется)", I),
    ("to the moon",     r"\bmoon\b|to the moon|\bgems?\b", I),
    ("иксы x10",        r"\b[xх]\s?(?!402\b)\d{1,3}\b|\b\d{1,3}\s?[xх]\b|\bиксы?\b|\bиксов\b", I),
    # --- 3–7. Доход ---
    ("APY/APR",         r"\bAPY\b|\bAPR\b|\byield\b|\bгодовых\b|%\s*per\s*year|процент\w*\s+на\s+вклад", I),
    ("доходность",      r"доходност\w*|\breturns\b|\bROI\b|окупит\w*|\bmake\s+money\b|\bприбыл\w*|\bprofits?\b", I),
    ("пассивный доход", r"пассивн\w*\s+доход\w*|passive\s+income", I),
    ("дивиденды",       r"дивиденд\w*|дол[яи]\s+прибыли|выплат\w*\s+держател\w*|revenue\s+share|profit\s+share|dividends?|holder\s+rewards?", I),
    ("стейкинг",        r"стейкинг\w*|застейка\w*|фарминг\w*|\bstaking\b|stake\s+and\s+earn|yield\s+farming", I),
    # --- 8–10. Инвестиции ---
    ("инвестиции",      r"инвестиру\w*|инвестици\w*|инвестор\w*|\binvest\w*", I),
    ("деньги покупателей", r"деньг\w*\s+покупател\w*|средств\w*\s+покупател\w*|proceeds\s+are\s+invested|funds\s+from\s+buyers", I),
    ("токен и выручка", r"токен\w*\s+(связан\w*\s+с\s+)?выручк\w*|выручк\w*\s+(идёт|идет)\s+держател\w*|tied\s+to\s+revenue|revenue\s+backs", I),
    # --- 11–12. Токеномика ---
    ("дефляция",        r"дефляци\w*|сжигани\w*\s+подним\w*|\bdeflation\w*|burn\s*=\s*price", I),
    ("buyback",         r"\bbuybacks?\b|казн\w*\s+выкуп\w*|выкуп\w*\s+с\s+прибыл\w*|treasury\s+buys\s+back", I),
    # --- 13–16. Листинг, партнёры ---
    ("будет на Binance", r"(буд[еу][тм]|появи[мт]ся)\s+на\s+(binance|bybit|okx|coinbase|kraken|mexc|gate|bitget|kucoin|htx)\b|will\s+be\s+(listed\s+)?on\s+\w+|listing\s+on\s+\w+\s+soon", I),
    ("гарантированный листинг", r"гарантированн\w*\s+листинг\w*|листинг\w*\s+подтвержд\w*|guaranteed\s+listing|listing\s+confirmed", I),
    ("партнёр/при поддержке", r"\bпартн[её]р\w*|при\s+поддержке|partnered\s+with|\bpartners?\b|backed\s+by", I),
    ("инвестиция фонда", r"фонд\w*\s+(купил|инвестировал|вложил)\w*|foundation\s+invested", I),
    # --- 17–23. Airdrop, игра, рефералы ---
    ("airdrop",         r"airdrop\w*|аирдроп\w*|эйрдроп\w*|раздач\w*\s+токен\w*|free\s+tokens?|play\s+for\s+airdrop", I),
    ("заработай",       r"зарабат\w*|заработ\w*|\bearn\b|\bearning\w*|earn\s+(money|crypto)", I),
    ("play-to-earn",    r"play[\s-]*to[\s-]*earn|\bP2E\b|играй\s+и\s+получай\s+токен\w*|play\s+and\s+get\s+tokens?", I),
    ("ставки/азарт",    r"\bставк\w*|\bвыигрыш\w*|джекпот\w*|лотере\w*|розыгрыш\w*|\bbets?\b|\bwagers?\b|\bgambl\w*|\bjackpots?\b|\blotter(y|ies)\b|\braffles?\b|win\s+tokens?", I),
    ("купи шанс",       r"куп\w*\s+шанс\w*|покупк\w*\s+повыша\w*\s+шанс\w*|buy\s+to\s+win|pay\s+to\s+boost|stars\s*=\s*tokens?", I),
    ("квест: купи",     r"квест\w*[:\s]+куп\w*|quest[:\s]+buy|swap\s+to\s+qualify", I),
    ("рефералы MLM",    r"многоуровнев\w*|пирамид\w*|\bMLM\b|multi-?level|%\s+(с|от)\s+покупок|of\s+your\s+friend'?s\s+purchases", I),
    # --- 24–25. Сигналы, рекомендации ---
    ("точность N%",     r"точност\w*\s*\d+\s*%|\d+\s*%\s*accuracy|гарантированн\w*\s+сигнал\w*|guaranteed\s+signals?|безошибочн\w*|never\s+loses", I),
    ("купи/продай сейчас", r"\b(купи|продай|покупай|продавай)\b|мы\s+рекоменду\w*|\bbuy\s+now\b|\bsell\s+now\b|we\s+recommend", I),
    # --- 26. Даты ---
    ("дата (год)",      r"\b(19|20)\d{2}\b", 0),
    ("дата (дд.мм.гг)", r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b", 0),
    ("месяц RU",        r"\b(январ|феврал|апрел|июн|июл|август|сентябр|октябр|ноябр|декабр)\w*|\bмарт[аеу]?\b|\bма[йя]\b", I),
    ("месяц EN",        r"\b(january|february|march|april|june|july|august|september|october|november|december)\b|\b(jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\b\.?", I),
    ("месяц EN (May)",  r"\bMay\b", 0),   # с учётом регистра: глагол may — не месяц
    ("квартал Q1–Q4",   r"\bQ[1-4]\b|квартал\w*", I),
    ("TGE/листинг с датой", r"\bTGE\b", I),
    # --- 27. Команда ---
    ("имя человека",    r"\bИван\w*|\bIvan\b|\bВан[яе]\b", I),
    # --- 28–30. Токен как деньги, ценная бумага, риск ---
    ("монета/валюта",   r"\bмонет\w*|\bвалют\w*|цифров\w*\s+деньг\w*|\bcoins?\b|\bcurrenc(y|ies)\b|digital\s+money", I),
    ("ценная бумага",   r"ценн\w*\s+бумаг\w*|\bакци[яий]\b|дол[яи]\s+в\s+проекте|\bsecurit(y|ies)\b|\bshares?\b|\bequity\b", I),
    ("без риска",       r"без\s+риска|безопасн\w*\s+инвестиц\w*|не\s+упад[её]т|risk-?free|safe\s+investment|can'?t\s+go\s+down", I),
    # --- 31. Реклама, давление ---
    ("FOMO",            r"\bуспей\w*|последн\w*\s+шанс\w*|только\s+сегодня|\bhurry\b|last\s+chance|\bFOMO\b", I),
    # --- 33–35. Контракт, регионы, юрлицо ---
    ("навсегда",        r"\bнавсегда\b|\bforever\b", I),
    ("доступно всем",   r"доступн\w*\s+(всем|везде)|без\s+KYC|available\s+worldwide|no\s+KYC", I),
    ("лицензировано",   r"лицензирован\w*|регулиру\w*|\blicensed\b|\bregulated\b", I),
    # ======= дополнения из итогового списка (ПРАВИЛА_юридические_v1.md, раздел «Стоп-слова») =======
    # 1–2. Цена
    ("ATH/капитализация/pump", r"\bATH\b|капитализаци\w*|market\s+cap|\bpumps?\b|\bpumping\b|памп\w*", I),
    ("гемы/gems",       r"\bгем(ы|ов|а|ами|ах)?\b", I),
    # 7–8. Доход
    ("hold-to-earn/фарм", r"hold[\s-]*to[\s-]*earn|холд\w*|\bfarm\w*|\bфарм\w*", I),
    ("ранние инвесторы/presale", r"early\s+investors?|\bpre-?sales?\b|пресейл\w*|предпродаж\w*|со\s+скидкой", I),
    # 11–13. Токеномика
    ("deflationary/scarcity", r"\bdeflationary\b|\bscarcity\b|\bscarce\b|дефицит\w*|редкост\w*", I),
    ("repurchase",      r"\brepurchas\w*|buyback\s*&\s*burn", I),
    ("повысим ценность", r"повыс\w*\s+ценност\w*|работа\w*\s+на\s+цену|заинтересован\w*\s+в\s+росте|drive\s+value|aligned\s+on\s+price", I),
    # 14–17. Листинг (до white paper — молчание)
    ("листинг через MVB", r"\bMVB\b|alpha\s+гарантирован\w*|листинг\w*\s+через", I),
    ("листинг/пул/LP-лок", r"\bлистинг\w*|\blistings?\b|\blisted\b|\bпул\w*\b|\bpools?\b|LP[\s-]*(lock|лок)\w*|заявк\w*\s+подан\w*", I),
    # 19–26. Игра, рефералы
    ("win/prize/odds/casino", r"\bwins?\b|\bwinning\b|\bprizes?\b|\bodds\b|\bcasino\b|\bbookmakers?\b|\btotali[sz]ator\b|\bstakes?\b|\bприз(ы|а|у|ом|е|ов|ам|ами|ах)?\b|коэффициент\w*|казино|букмекер\w*|тотализатор\w*", I),
    ("угадай/guess",    r"угада\w*|\bguess\w*", I),
    ("cash out points", r"cash\s+out\s+points?|exchange\s+points?|sell\s+points?|вывести\s+очки|обменять\s+очки|продать\s+очки", I),
    ("приведи друга",   r"приведи\s+друга|refer-?a-?friend|referral\s+bonus", I),
    ("boost your chance", r"boost\s+your\s+chance|повысь\s+шанс\w*", I),
    # 27–28. Сигналы, советы
    ("инсайд/insider",  r"инсайд\w*|\binsider\w*", I),
    ("advisor/консультация", r"\badvisors?\b|\badvisory\b|investment\s+advice|(buy|sell)\s+signals?|советник\w*|консультаци\w*|входи\s+сейчас|сигнал\s+купить", I),
    # 30. Команда
    ("страна проживания", r"таиланд\w*|\bthailand\b|живу\s+в\b|работаю\s+из\b|working\s+from|team\s+size|команд\w*\s+из\s+\d+", I),
    # 31–32. Токен как деньги, ценная бумага
    ("платёжное средство", r"плат[её]жн\w*\s+средств\w*|means\s+of\s+payment", I),
    ("prospectus",      r"\bprospectus\b|\bпроспект\w*|эмисси\w*\s+ценн\w*|securities\s+offering", I),
    ("is not a security", r"is\s+not\s+a\s+security|не\s+являет\w*\s+ценн\w*\s+бумаг\w*", I),
    # 33. Надёжность
    ("stable/safe/unruggable", r"\bstable\b|\bsafe\b|\bsafely\b|rug-?proof|unruggable|стабильн\w*|над[её]жн\w*|невозможно\s+украсть", I),
    # 34. MiCA
    ("MiCA/approved",   r"\bMiCA\b|approved\s+by|одобрен\w*\s+регулятор\w*|вне\s+ЕС|not\s+subject\s+to|no\s+liability|без\s+ответственност\w*", I),
    # 35. Контракт
    ("anti-dump/blacklist", r"anti-?dump|анти-?дамп\w*|price\s+protection|защит\w*\s+цен\w*|blacklist\w*|ч[её]рн\w*\s+список|audited\s*=\s*secure|аудит\s+гарантиру\w*|adjust\s+anytime|в\s+любой\s+момент", I),
    # 36–38. Реклама
    ("limited time",    r"limited\s+time|ограниченн\w*\s+врем\w*|\btoday\s+only\b", I),
    ("#sp/#collab",     r"#sp\b|#collab\b|thanks\s+to", I),
    ("крипта и инфляция", r"инфляци\w*|\binflation\b|rent\s+is\s+too\s+high|дорог\w*\s+аренд\w*", I),
    # 39. Регионы
    ("anywhere/worldwide", r"\banywhere\b|\bworldwide\b|\bбат(ы|ов|ах)\b|тайск\w*|\bthai\b|UK\s+promo", I),
    # 40. Юрлицо
    ("мы — компания/регистрация", r"мы\s*[—-]\s*компани\w*|we\s+are\s+company|registered\s+with|зарегистрирован\w*\s+(в|у)\b|RAK\s+DAO|wyoming|паспорт\w*|passport", I),
    # 41. Данные
    ("персональные данные/анонимно", r"не\s+собираем|do\s+not\s+collect|\banonymous\w*|анонимн\w*|100\s*%\s*(safe|безопасн\w*)|GDPR-?\s*(certified|сертифицирован\w*)|age\s+verification|проверк\w*\s+возраст\w*|data\s+sale|продаж\w*\s+данных|for\s+AI\s+training|для\s+обучения\s+ИИ", I),
    # 42. ИС / бренды
    ("товарный знак/®", r"registered\s+trademark|зарегистрированн\w*\s+товарн\w*|®|official\s+partner|официальн\w*\s+партн[её]р\w*|Claude\s+Code|expert\s+answer|human\s+answer|ответ\s+(эксперта|человека)", I),
    # 43. Telegram-мини-апп (на сайте допустимо, но помечаем для ручной проверки)
    ("PancakeSwap",     r"pancakeswap", I),
]

# Слова «под вопросом» (проверяются только с --strict)
QUESTIONABLE = [
    ("игра (заголовок?)", r"\bигр[аыеу]\b", I),
    ("snapshot",          r"\bснимок\b|\bsnapshot\b", I),
    ("эмиссия",           r"эмисси\w*", I),
]

TEXT_ATTRS = {"content", "alt", "title", "aria-label", "placeholder"}

# Белый список: исключения, согласованные координатором. Каждое выводится в отчёте
# отдельной строкой «исключение: …», чтобы его нельзя было пропустить.
WHITELIST = {
    # ключ i18n или точный текст : пояснение для отчёта
    "home.stats.coins.label": "надпись на экранчике «COINS» (торговые пары бирж, не наш токен) — по ТЗ Ивана, требует подтверждения",
    "COINS": "надпись на экранчике «COINS» (торговые пары бирж, не наш токен) — по ТЗ Ивана, требует подтверждения",
    # Фаза 3 дорожной карты — по указанию Ивана, юрист: MiCA 4(4) (стоп-правила 14 и 17 итогового списка)
    "roadmap.p3.4": "фаза 3: биржи по порядку (MEXC → Gate → Bitget → BNB Chain) — по указанию Ивана, юрист: MiCA 4(4)",
    "roadmap.p3.5": "фаза 3: «каждая заявка на листинг закрывается постом» — по указанию Ивана, юрист: MiCA 4(4)",
    "Биржи, по порядку: MEXC → Gate → Bitget → программы BNB Chain": "фаза 3: биржи по порядку — по указанию Ивана, юрист: MiCA 4(4)",
    "Каждая заявка на листинг закрывается постом": "фаза 3: «каждая заявка на листинг закрывается постом» — по указанию Ивана, юрист: MiCA 4(4)",
}


class TextExtractor(HTMLParser):
    """Собирает текстовые узлы и значения текстовых атрибутов с номерами строк."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = []  # (line, text)
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        line = self.getpos()[0]
        for name, val in attrs:
            if name in TEXT_ATTRS and val:
                self.items.append((line, val))

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip:
            return
        s = " ".join(data.split())
        if s:
            self.items.append((self.getpos()[0], s))


def compiled(rules):
    return [(label, re.compile(rx, flags)) for label, rx, flags in rules]


def scan_text(text, rules):
    hits = []
    for label, rx in rules:
        for m in rx.finditer(text):
            hits.append((label, m.group(0)))
    return hits


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    strict = "--strict" in argv
    site = Path(__file__).resolve().parent.parent
    rules = compiled(STOP_WORDS + (QUESTIONABLE if strict else []))
    rows = []  # (file, where, found)
    exceptions = []  # (file, where, пояснение)

    for jf in sorted((site / "i18n").glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        for key, val in data.items():
            if not isinstance(val, str):
                continue
            hits = scan_text(val, rules)
            if hits and (key in WHITELIST or val in WHITELIST):
                exceptions.append((jf.relative_to(site).as_posix(), key, WHITELIST.get(key) or WHITELIST.get(val)))
                continue
            for label, found in hits:
                rows.append((jf.relative_to(site).as_posix(), key, f"{found}  [{label}]"))

    readme = site / "README.md"
    if readme.exists():
        in_code = False
        for n, line in enumerate(readme.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip().startswith("```"):                  # код-блоки — не публичный текст
                in_code = not in_code
                continue
            if in_code:
                continue
            text = re.sub(r"`[^`]*`", " ", line)                # inline code (имена ключей, команды)
            text = re.sub(r"<[^>]+>", " ", text)                # html-теги (бейджи, логотип)
            text = re.sub(r"https?://\S+", " ", text)          # ссылки
            hits = scan_text(text, rules)
            if hits and text.strip() in WHITELIST:
                exceptions.append(("README.md", f"строка {n}", WHITELIST[text.strip()]))
                continue
            for label, found in hits:
                rows.append(("README.md", f"строка {n}", f"{found}  [{label}]"))

    for hf in sorted(site.rglob("*.html")):
        if any(part in ("node_modules", ".git") for part in hf.parts):
            continue
        p = TextExtractor()
        p.feed(hf.read_text(encoding="utf-8"))
        for line, text in p.items:
            hits = scan_text(text, rules)
            if hits and text in WHITELIST:
                exceptions.append((hf.relative_to(site).as_posix(), f"строка {line}", WHITELIST[text]))
                continue
            for label, found in hits:
                rows.append((hf.relative_to(site).as_posix(), f"строка {line}", f"{found}  [{label}]"))

    for f, where, why in exceptions:
        print(f"исключение: {f} · {where} · {why}")
    if exceptions:
        print()

    if rows:
        w1 = max(len(r[0]) for r in rows)
        w2 = max(len(r[1]) for r in rows)
        print(f"{'файл'.ljust(w1)} · {'ключ/строка'.ljust(w2)} · найдено")
        print("-" * (w1 + w2 + 20))
        for f, where, found in rows:
            print(f"{f.ljust(w1)} · {where.ljust(w2)} · {found}")
        print(f"\nИтог: найдено {len(rows)} совпадений в {len({r[0] for r in rows})} файлах"
              + (" (режим --strict)" if strict else ""))
        return 1

    print(f"Итог: стоп-слов не найдено. Правил: {len(rules)}" + (" (режим --strict)" if strict else "")
          + f". Проверено: {len(list((site / 'i18n').glob('*.json')))} JSON, README.md, {len(list(site.rglob('*.html')))} HTML.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
