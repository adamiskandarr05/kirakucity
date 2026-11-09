"""All generated quantities and all solution arithmetic use Fraction.

JSON stores rational values as strings, never binary floating point.
"""
from dataclasses import dataclass
from fractions import Fraction as F

TOPICS = {
    'ratio_percent': ('Nisbah dan peratus', 'Ratio & percentage'),
    'linear_equation': ('Persamaan linear', 'Linear equations'),
    'statistics': ('Statistik', 'Statistics'),
    'two_unknowns': ('Dua pembolehubah', 'Two unknowns'),
}


def rounded(value, places=2):
    value = F(value)
    factor = 10 ** places
    sign = -1 if value < 0 else 1
    value = abs(value) * factor
    whole = value.numerator // value.denominator
    if value - whole >= F(1, 2):
        whole += 1
    return F(sign * whole, factor)


def display(value, places=2):
    n = rounded(value, places) * 10 ** places
    n = int(n)
    sign = '-' if n < 0 else ''
    n = abs(n)
    return f'{sign}{n // (10 ** places)}.{n % (10 ** places):0{places}d}' if places else f'{sign}{n}'


def step(label, unit, value, trap, mistake, approach, method, worked):
    return dict(label=label, unit=unit, expected=str(F(value)), trap=str(F(trap)),
                mistake=mistake, solution=dict(approach=approach, method=method,
                worked=worked), places=2)


@dataclass(frozen=True)
class Template:
    id: str
    topic: str
    level: int
    title_ms: str
    title_en: str
    kind: str

    def generate(self, rng, default=False):
        if self.id == 'kedai_bunga_melur':
            p, q, x, c, target = (F(20), F(10), F(110), F(85), F(25)) if default else (
                F(rng.choice([10, 20, 25, 30])), F(rng.choice([5, 10, 15, 20])),
                F(rng.randrange(8, 21) * 10), F(rng.randrange(4, 8) * 10), F(rng.choice([15, 25, 40])))
            if (1+p/100)*(1-q/100)==1:
                q=F(10)
            final = x * (1 + p / 100) * (1 - q / 100)
            # Keep generated profit positive, with both viable and held outcomes.
            c = min(c, final - 10)
            givens = dict(P=str(p), Q=str(q), F=str(final), C=str(c), T=str(target))
        elif self.id == 'teksi_kiraku':
            a, r, d, further = (F(5), F('1.2'), F(10), F(15)) if default else (
                F(rng.choice([3, 5, 7])), F(rng.choice(['1.2', '1.5', '2'])),
                F(rng.randrange(6, 19)), F(rng.randrange(12, 26)))
            givens = dict(A=str(a), R=str(r), F=str(a + r * d), D=str(further))
        elif self.id == 'gerai_taman':
            mode = F(40 if default else rng.randrange(25, 65))
            b, c, x = mode + 7, mode + 13, mode + 21
            known = [mode, mode, b, c]
            if not default:
                rng.shuffle(known)
            givens = dict(known=[str(v) for v in known], M=str((sum(known) + x) / 5), T=str(mode - 5))
        else:
            w = F(20 if default else rng.randrange(10, 31))
            r = F(40 if default else rng.choice([20, 30, 40]))
            budget = F(900) if default else (w + 5) * r + F(rng.choice([-100, 0, 100]))
            givens = dict(P=str(4 * w + 10), B=str(budget), R=str(r), gap='5')
        case = dict(template_id=self.id, topic=self.topic, level=self.level,
                    title_ms=self.title_ms, title_en=self.title_en, kind=self.kind,
                    givens=givens, rounding='Bulatkan kepada 2 tempat perpuluhan (Round to 2 decimal places; half up).')
        case['steps'] = self.solve(case)
        case['brief'], case['given_rows'] = self.brief(case)
        return case

    def solve(self, case):
        g = {k: ([F(x) for x in v] if isinstance(v, list) else F(v)) for k, v in case['givens'].items()}
        if self.id == 'kedai_bunga_melur':
            x = g['F'] / ((1 + g['P'] / 100) * (1 - g['Q'] / 100))
            profit = g['F'] - g['C']
            return [step('Harga asal / Original price', 'RM', x, g['F'] / (1 + g['P']/100 - g['Q']/100),
                'Peratus berturutan / Adding successive percentages',
                'Undo the discount first, then undo the price increase.',
                'Divide the final price by the discount multiplier, then by the increase multiplier.',
                f"{display(g['F'])} ÷ (1 + {display(g['P'],0)}/100) ÷ (1 − {display(g['Q'],0)}/100) = RM {display(x)}"),
                step('Untung / Profit', 'RM', profit, x - g['C'], 'Harga asal digunakan / Used the original selling price',
                'Profit compares what the shop receives with what it paid.',
                'Subtract the cost from the final selling price.',
                f"{display(g['F'])} − {display(g['C'])} = RM {display(profit)}")]
        if self.id == 'teksi_kiraku':
            d = (g['F'] - g['A']) / g['R']; cost = g['A'] + g['R'] * g['D']
            return [step('Jarak perjalanan / Distance', 'km', d, g['F']/g['R'], 'Tambang mula tertinggal / Forgot the flag fee',
                'The trip total includes a fixed fee and a distance charge.',
                'Subtract the fixed fee before dividing by the rate per kilometre.',
                f"({display(g['F'])} − {display(g['A'])}) ÷ {display(g['R'])} = {display(d)} km"),
                step('Tambang baharu / New fare', 'RM', cost, g['R']*g['D'], 'Tambang mula tertinggal / Forgot the flag fee',
                'The new trip also starts with the fixed fee.', 'Multiply the new distance by the rate, then add the fixed fee.',
                f"{display(g['A'])} + {display(g['R'])} × {display(g['D'])} = RM {display(cost)}")]
        if self.id == 'gerai_taman':
            total = g['M'] * 5; missing = total - sum(g['known'])
            mode = max(set(g['known']), key=g['known'].count)
            return [step('Jumlah jualan / Total sales', 'RM', total, g['M'], 'Min bukan jumlah / Mean used as total',
                'The mean spreads the total evenly across the days.', 'Multiply the mean by the number of days.',
                f"{display(g['M'])} × 5 = RM {display(total)}"),
                step('Jualan yang hilang / Missing sales', 'RM', missing, g['M'], 'Min bukan nilai hilang / Mean used as missing value',
                'Compare the full total with the known sales.', 'Subtract the sum of the known sales from the total.',
                f"{display(total)} − {display(sum(g['known']))} = RM {display(missing)}"),
                step('Mod / Mode', 'RM', mode, missing, 'Nilai hilang bukan mod / Missing value used as mode',
                'The mode is the value that occurs most often.', 'Count each value across all the daily sales and choose the most frequent.',
                f"RM {display(mode)} occurs twice; every other value occurs once.")]
        w = (g['P'] / 2 - g['gap']) / 2; length = w + g['gap']; cost = length*g['R']; shortfall = max(F(0), cost-g['B'])
        return [step('Lebar taman / Width', 'm', w, g['P']/4, 'Taman bukan segi empat sama / Treated the park as a square',
                'A rectangle has a pair of long sides and a pair of short sides.', 'Halve the perimeter, subtract the length difference, then halve again.',
                f"({display(g['P'])} ÷ 2 − 5) ÷ 2 = {display(w)} m"),
            step('Panjang taman / Length', 'm', length, w, 'Perbezaan tertinggal / Forgot the length difference',
                'The length is greater than the width.', 'Add the stated difference to the width.',
                f"{display(w)} + 5 = {display(length)} m"),
            step('Kos pagar / Fence cost', 'RM', cost, g['P']*g['R'], 'Seluruh perimeter / Fenced the whole perimeter',
                'The budget covers a fence on one long side only.', 'Multiply the length by the cost per metre.',
                f"{display(length)} × {display(g['R'])} = RM {display(cost)}"),
            step('Kekurangan bajet / Shortfall', 'RM', shortfall, cost, 'Bajet tidak ditolak / Budget not subtracted',
                'A shortfall is the amount still needed after using the budget.', 'Subtract the budget from the fence cost; use zero if the budget is sufficient.',
                f"max(0, {display(cost)} − {display(g['B'])}) = RM {display(shortfall)}")]

    def trap(self, case):
        return [F(s['trap']) for s in self.solve(case)]

    def outcome(self, final_values, case=None):
        values = [F(x) for x in final_values]
        if self.kind == 'shops':
            return values[-1] >= F(case['givens']['T'])
        if self.kind == 'stalls':
            return values[-1] >= F(case['givens']['T'])
        if self.kind == 'parks':
            return values[-1] == 0
        return True

    def brief(self, case):
        g = case['givens']; money = lambda k: display(g[k])
        if self.kind == 'shops':
            return (f"Kedai bunga menaikkan harga pasu sebanyak {money('P')}%, kemudian memberi diskaun {money('Q')}%. Harga akhir ialah RM {money('F')}. Cari harga asal dan untung. / A flower shop raises its vase price, then discounts it. Find the original price and profit. A profit of at least RM {money('T')} will reopen the shop.",
                [('Kenaikan / Increase', money('P'), '%'), ('Diskaun / Discount', money('Q'), '%'), ('Harga akhir / Final price', money('F'), 'RM'), ('Kos / Cost', money('C'), 'RM'), ('Sasaran untung / Profit target', money('T'), 'RM')])
        if self.kind == 'stands':
            return (f"Teksi mengenakan tambang mula dan kadar setiap kilometer. Perjalanan pertama berharga RM {money('F')}. / Find the first trip distance, then the fare for a {money('D')} km journey to open the taxi stand.",
                [('Tambang mula / Flag fee', money('A'), 'RM'), ('Kadar / Rate', money('R'), 'RM/km'), ('Jumlah / Trip cost', money('F'), 'RM'), ('Jarak baharu / New distance', money('D'), 'km')])
        if self.kind == 'stalls':
            known = ', '.join(display(x) for x in g['known'])
            return (f"Jualan lima hari mempunyai min RM {money('M')}. Empat nilai diketahui: {known}. / Find the total, missing daily sales and mode. A mode of at least RM {money('T')} opens the stall.",
                [('Jualan diketahui / Known sales', known, 'RM'), ('Min / Mean', money('M'), 'RM'), ('Bilangan hari / Days', '5', 'days'), ('Sasaran mod / Mode target', money('T'), 'RM')])
        return (f"Panjang taman ialah 5 m lebih daripada lebar. / The park is 5 m longer than it is wide. Find both dimensions, the fence cost for one long side, and the budget shortfall. Zero shortfall funds the park.",
            [('Perimeter', money('P'), 'm'), ('Perbezaan / Difference', '5.00', 'm'), ('Bajet / Budget', money('B'), 'RM'), ('Kadar pagar / Fence rate', money('R'), 'RM/m')])


TEMPLATES = {t.id: t for t in [
    Template('kedai_bunga_melur', 'ratio_percent', 3, 'Kedai Bunga Melur', 'The flower shop', 'shops'),
    Template('teksi_kiraku', 'linear_equation', 2, 'Teksi Kiraku', 'The taxi stand', 'stands'),
    Template('gerai_taman', 'statistics', 4, 'Gerai Taman', 'The garden stall', 'stalls'),
    Template('taman_kiraku', 'two_unknowns', 5, 'Taman Kiraku', 'The neighbourhood park', 'parks'),
]}
