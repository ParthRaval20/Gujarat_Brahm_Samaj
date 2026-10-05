"""
Gujarati Search & Phonetic Transliteration Utility.
Enables bidirectional, intelligent search across Gujarati and English texts,
numerals, surnames, cities, and names.
"""

from __future__ import annotations

import re

# ── Gujarati to ASCII Digits ─────────────────────────────────────────────────
GUJ_DIGITS = {
    '૦': '0', '૧': '1', '૨': '2', '૩': '3', '૪': '4',
    '૫': '5', '૬': '6', '૭': '7', '૮': '8', '૯': '9',
}
ENG_TO_GUJ_DIGITS = {v: k for k, v in GUJ_DIGITS.items()}


def normalize_digits_to_english(text: str) -> str:
    """Convert any Gujarati numerals (૦-૯) in string to English digits (0-9)."""
    return "".join(GUJ_DIGITS.get(ch, ch) for ch in text)


def normalize_digits_to_gujarati(text: str) -> str:
    """Convert English digits (0-9) to Gujarati numerals (૦-૯)."""
    return "".join(ENG_TO_GUJ_DIGITS.get(ch, ch) for ch in text)


# ── Curated Community & Geographical Dictionary ──────────────────────────────
# Bi-directional mappings for community surnames, prominent names, and Gujarat regions
COMMUNITY_DICT: dict[str, list[str]] = {
    # Surnames
    'રાવલ': ['raval', 'rawal'],
    'રાવળ': ['raval', 'rawal'],
    'જોષી': ['joshi', 'josi'],
    'જોશી': ['joshi', 'josi'],
    'વ્યાસ': ['vyas'],
    'ભટ્ટ': ['bhatt', 'bhat'],
    'શુક્લ': ['shukla', 'shukal'],
    'શુકલ': ['shukla', 'shukal'],
    'દવે': ['dave'],
    'ત્રિવેદી': ['trivedi'],
    'ત્રીવેદી': ['trivedi'],
    'જાની': ['jani'],
    'ઉપાધ્યાય': ['upadhyay'],
    'મેહતા': ['mehta'],
    'મહેતા': ['mehta'],
    'શાસ્ત્રી': ['shastri'],
    'પંડ્યા': ['pandya', 'pande'],
    'પંડ્યા': ['pandya', 'pande'],
    'પંડિત': ['pandit'],
    'દ્વિવેદી': ['dwivedi', 'divedi'],
    'દીવેદી': ['dwivedi', 'divedi'],
    'આચાર્ય': ['acharya'],
    'પુરોહિત': ['purohit'],
    'નાગર': ['nagar'],
    'ખેડાવળ': ['khedaval', 'khedawal'],
    'ખેડાવાળ': ['khedaval', 'khedawal'],
    'ઔદીચ્ય': ['audichya', 'audich'],
    'મોઢ': ['modh'],
    'સિદ્ધપુરા': ['siddhpura'],
    'સોમપુરા': ['sompura'],
    'બ્રહ્મભટ્ટ': ['brahmbhatt'],
    'બ્રહ્મ': ['brahm', 'brahma'],

    # Common First Names
    'પાર્થ': ['parth'],
    'મહેશ': ['mahesh'],
    'હર્ષદ': ['harshad'],
    'રમેશ': ['ramesh'],
    'સુરેશ': ['suresh'],
    'દિનેશ': ['dinesh'],
    'રાજેશ': ['rajesh'],
    'મુકેશ': ['mukesh'],
    'અશોક': ['ashok'],
    'સંજય': ['sanjay'],
    'વિપુલ': ['vipul'],
    'ભાવેશ': ['bhavesh'],
    'કમલેશ': ['kamlesh'],
    'પિયુષ': ['piyush'],
    'નિલેશ': ['nilesh'],
    'હિતેશ': ['hitesh'],
    'જીતેન્દ્ર': ['jitendra', 'jitu'],
    'દર્શન': ['darshan'],
    'ગીતા': ['gita', 'geeta'],
    'પૂજા': ['puja', 'pooja'],
    'વર્ષા': ['varsha'],
    'રેખા': ['rekha'],
    'સીતા': ['sita', 'seeta'],
    'પ્રિયા': ['priya'],
    'ભાઈ': ['bhai'],
    'બહેન': ['bahen', 'ben'],
    'બેન': ['ben', 'bahen'],

    # Cities & Districts
    'ઈડર': ['idar'],
    'હિંમતનગર': ['himatnagar', 'himmatnagar'],
    'હિમ્મતનગર': ['himatnagar', 'himmatnagar'],
    'અમદાવાદ': ['ahmedabad', 'amdavad'],
    'રાજકોટ': ['rajkot'],
    'વડોદરા': ['vadodara', 'baroda'],
    'સુરત': ['surat'],
    'ગાંધીનગર': ['gandhinagar'],
    'સાબરકાંઠા': ['sabarkantha'],
    'બનાસકાંઠા': ['banaskantha'],
    'મહેસાણા': ['mehsana'],
    'પાટણ': ['patan'],
    'પ્રાંતિજ': ['prantij'],
    'તલોદ': ['talod'],
    'મોડાસા': ['modasa'],
    'ખેડબ્રહ્મા': ['khedbrahma'],
    'વિજયનગર': ['vijaynagar'],
    'ભિલોડા': ['bhiloda'],
    'વડનગર': ['vadnagar'],
    'ભાવનગર': ['bhavnagar'],
    'જામનગર': ['jamnagar'],
    'જૂનાગઢ': ['junagadh'],
    'જુનાગઢ': ['junagadh'],
    'ભુજ': ['bhuj'],
    'કચ્છ': ['kutch', 'kachchh'],
    'નવસારી': ['navsari'],
    'વલસાડ': ['valsad'],
    'આણંદ': ['anand'],
    'નડિયાદ': ['nadiad'],
    'ભરૂચ': ['bharuch'],
    'ગુજરાત': ['gujarat'],

    # Occupations
    'નોકરી': ['job', 'service'],
    'વેપાર': ['business', 'trade'],
    'શિક્ષક': ['teacher'],
    'વકીલ': ['advocate', 'lawyer'],
    'ડોક્ટર': ['doctor'],
    'તબીબ': ['doctor'],
    'ઈજનેર': ['engineer'],
    'એન્જિનિયર': ['engineer'],
    'ગૃહિણી': ['housewife', 'homemaker'],
    'અભ્યાસ': ['student', 'study'],
    'વિદ્યાર્થી': ['student'],
    'પ્રોફેસર': ['professor'],
    'પ્રિન્સિપાલ': ['principal'],
    'મેનેજર': ['manager'],
    'કન્સલ્ટન્ટ': ['consultant'],
    'આર્કિટેક્ટ': ['architect'],
    'ફાર્માસિસ્ટ': ['pharmacist'],
    'ઓફિસર': ['officer'],
    'સર્જન': ['surgeon'],
    'ડિઝાઇનર': ['designer'],
    'એનાલિસ્ટ': ['analyst'],
    'ખેતી': ['farming', 'agriculture'],
    'નિવૃત્ત': ['retired'],
}

# Reverse lookup dictionary: English word (lowercased) -> list of Gujarati words
REVERSE_COMMUNITY_DICT: dict[str, list[str]] = {}
for guj_word, eng_list in COMMUNITY_DICT.items():
    for eng_word in eng_list:
        eng_lower = eng_word.lower()
        if eng_lower not in REVERSE_COMMUNITY_DICT:
            REVERSE_COMMUNITY_DICT[eng_lower] = []
        if guj_word not in REVERSE_COMMUNITY_DICT[eng_lower]:
            REVERSE_COMMUNITY_DICT[eng_lower].append(guj_word)


# ── Rule-Based Phonetic Transliteration (Gujarati -> English) ────────────────
CONSONANTS = {
    'ક': 'k', 'ખ': 'kh', 'ગ': 'g', 'ઘ': 'gh', 'ઙ': 'ng',
    'ચ': 'ch', 'છ': 'chh', 'જ': 'j', 'ઝ': 'z', 'ઞ': 'ny',
    'ટ': 't', 'ઠ': 'th', 'ડ': 'd', 'ઢ': 'dh', 'ણ': 'n',
    'ત': 't', 'થ': 'th', 'દ': 'd', 'ધ': 'dh', 'ન': 'n',
    'પ': 'p', 'ફ': 'f', 'બ': 'b', 'ભ': 'bh', 'મ': 'm',
    'ય': 'y', 'ર': 'r', 'લ': 'l', 'ળ': 'l', 'વ': 'v',
    'શ': 'sh', 'ષ': 'sh', 'સ': 's', 'હ': 'h',
    'ક્ષ': 'ksh', 'જ્ઞ': 'gn',
}

VOWEL_SIGNS = {
    'ા': 'a', 'િ': 'i', 'ી': 'i', 'ુ': 'u', 'ૂ': 'u',
    'ૃ': 'ru', 'ૄ': 'ru', 'ે': 'e', 'ૈ': 'ai', 'ો': 'o', 'ૌ': 'au',
    'ં': 'n', 'ઁ': 'n', 'ઃ': 'h',
}

INDEPENDENT_VOWELS = {
    'અ': 'a', 'આ': 'a', 'ઇ': 'i', 'ઈ': 'i', 'ઉ': 'u', 'ઊ': 'u',
    'ઋ': 'ru', 'એ': 'e', 'ઐ': 'ai', 'ઓ': 'o', 'ઔ': 'au',
}

VIRAMA = '્'


def gujarati_to_phonetic_english(text: str) -> str:
    """Convert Gujarati word into an approximate phonetic English representation."""
    res: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        next_ch = text[i + 1] if i + 1 < n else ''

        if ch in INDEPENDENT_VOWELS:
            res.append(INDEPENDENT_VOWELS[ch])
            i += 1
        elif ch in CONSONANTS:
            cons = CONSONANTS[ch]
            res.append(cons)
            if next_ch == VIRAMA:
                # Suppress inherent vowel
                i += 2
            elif next_ch in VOWEL_SIGNS:
                res.append(VOWEL_SIGNS[next_ch])
                i += 2
            else:
                # Inherent vowel 'a' if not at the very end of word
                if i + 1 < n and (next_ch in CONSONANTS or next_ch in INDEPENDENT_VOWELS):
                    res.append('a')
                i += 1
        elif ch in VOWEL_SIGNS:
            res.append(VOWEL_SIGNS[ch])
            i += 1
        elif ch in GUJ_DIGITS:
            res.append(GUJ_DIGITS[ch])
            i += 1
        else:
            res.append(ch)
            i += 1

    return "".join(res).lower()


def is_gujarati_text(text: str) -> bool:
    """Return True if text contains any Gujarati Unicode characters (U+0A80 to U+0AFF)."""
    return any('\u0A80' <= ch <= '\u0AFF' for ch in text)


def expand_search_terms(query: str) -> list[str]:
    """
    Given a search string (which could be in Gujarati, English, or digits),
    return a comprehensive list of search term variants to match across
    both Gujarati and English database columns.
    """
    raw = query.strip()
    if not raw:
        return []

    terms: set[str] = set()
    terms.add(raw)

    # 1. Dot & punctuation variations (e.g., M.B.B.S. -> MBBS, B.Com. -> BCom)
    no_dots = raw.replace('.', '').strip()
    if no_dots and no_dots != raw and len(no_dots) >= 2:
        terms.add(no_dots)

    # 2. Digit normalization
    norm_eng_digits = normalize_digits_to_english(raw)
    norm_guj_digits = normalize_digits_to_gujarati(raw)
    if norm_eng_digits != raw:
        terms.add(norm_eng_digits)
    if norm_guj_digits != raw:
        terms.add(norm_guj_digits)

    # If numeric digits exist, expand code formats (e.g. 42 -> GBS-000042)
    digits = "".join(ch for ch in norm_eng_digits if ch.isdigit())
    if digits and len(digits) <= 6:
        try:
            num = int(digits)
            terms.add(f"GBS-{num:06d}")
            terms.add(f"{num:06d}")
        except ValueError:
            pass

    # 3. Tokenized word expansion
    words = re.split(r'[\s,._-]+', raw)
    for word in words:
        w = word.strip()
        if not w:
            continue
        # Avoid treating 'GBS' as a standalone match term when part of a specific code
        if w.upper() == 'GBS' and len(raw) > 3:
            continue
        # Avoid 1-character token matches when user query is multi-character
        if len(w) < 2 and len(raw) >= 2:
            continue
        terms.add(w)

        # Check known dictionary directly
        if w in COMMUNITY_DICT:
            for eng in COMMUNITY_DICT[w]:
                terms.add(eng)
                # also test v/w variation
                if 'v' in eng:
                    terms.add(eng.replace('v', 'w'))
                if 'w' in eng:
                    terms.add(eng.replace('w', 'v'))

        w_lower = w.lower()
        if w_lower in REVERSE_COMMUNITY_DICT:
            for guj in REVERSE_COMMUNITY_DICT[w_lower]:
                terms.add(guj)

        # Gujarati spelling variants (શ <-> ષ, ળ <-> લ, ી <-> િ, ૂ <-> ુ)
        if is_gujarati_text(w):
            var_terms = [w]
            if 'શ' in w:
                var_terms.append(w.replace('શ', 'ષ'))
            if 'ષ' in w:
                var_terms.append(w.replace('ષ', 'શ'))
            if 'ળ' in w:
                var_terms.append(w.replace('ળ', 'લ'))
            if 'લ' in w:
                var_terms.append(w.replace('લ', 'ળ'))
            if 'ી' in w:
                var_terms.append(w.replace('ી', 'િ'))
            if 'િ' in w:
                var_terms.append(w.replace('િ', 'ી'))
            for vt in var_terms:
                terms.add(vt)
                if vt in COMMUNITY_DICT:
                    for eng in COMMUNITY_DICT[vt]:
                        terms.add(eng)

        # If it's Gujarati, compute rule-based phonetic English
        if is_gujarati_text(w):
            phonetic_eng = gujarati_to_phonetic_english(w)
            if phonetic_eng and len(phonetic_eng) >= 2:
                terms.add(phonetic_eng)
                if 'v' in phonetic_eng:
                    terms.add(phonetic_eng.replace('v', 'w'))
                if 'w' in phonetic_eng:
                    terms.add(phonetic_eng.replace('w', 'v'))
                if 'sh' in phonetic_eng:
                    terms.add(phonetic_eng.replace('sh', 's'))
                if 's' in phonetic_eng and 'sh' not in phonetic_eng:
                    terms.add(phonetic_eng.replace('s', 'sh'))

    # Also handle whole query phonetic
    if is_gujarati_text(raw):
        full_phonetic = gujarati_to_phonetic_english(raw)
        if full_phonetic:
            terms.add(full_phonetic)
            if 'v' in full_phonetic:
                terms.add(full_phonetic.replace('v', 'w'))
            if 'w' in full_phonetic:
                terms.add(full_phonetic.replace('w', 'v'))

    # Clean up empty or single-character noise
    clean_terms = [t for t in terms if t and len(t.strip()) > 0]
    return clean_terms
