"""
╔══════════════════════════════════════════════════════════════╗
║           GRAND CASINO ROYALE — ROULETTE SIMULATOR           ║
║   Outcome Tracker · Pattern Detection · Est. 1875 · Monaco   ║
╚══════════════════════════════════════════════════════════════╝
"""

import random, time, sys, os, re, csv, json, math
from collections import Counter, defaultdict
from datetime import datetime


# ─── ANSI Palette ─────────────────────────────────────────────────────────────
RESET   = "\033[0m";  BOLD  = "\033[1m";  DIM   = "\033[2m";  ITALIC = "\033[3m"
GOLD    = "\033[38;2;212;175;55m";  AMBER  = "\033[38;2;255;191;0m"
CREAM   = "\033[38;2;255;245;200m"; DKGREEN= "\033[38;2;0;80;40m"
LTGREEN = "\033[38;2;50;200;100m";  RED    = "\033[38;2;200;30;30m"
CRIMSON = "\033[38;2;220;20;40m";   SILVER = "\033[38;2;180;180;180m"
GREY    = "\033[38;2;110;110;110m"; CYAN   = "\033[38;2;80;200;220m"
PURPLE  = "\033[38;2;180;100;220m"; ORANGE = "\033[38;2;255;140;0m"
TEAL    = "\033[38;2;0;200;180m";   ROSE   = "\033[38;2;255;100;130m"

# ─── Number Classification ────────────────────────────────────────────────────
RED_NUMBERS   = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
BLACK_NUMBERS = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

def num_color(n):
    if n == 0:            return LTGREEN + BOLD
    if n in RED_NUMBERS:  return CRIMSON + BOLD
    return SILVER + BOLD

def colour_of(n):
    if n == 0:            return "zero"
    if n in RED_NUMBERS:  return "red"
    return "black"

def parity_of(n):
    if n == 0: return "zero"
    return "even" if n % 2 == 0 else "odd"

def dozen_of(n):
    if n == 0:   return "zero"
    if n <= 12:  return "1st dozen"
    if n <= 24:  return "2nd dozen"
    return "3rd dozen"

def half_of(n):
    if n == 0:  return "zero"
    return "low (1-18)" if n <= 18 else "high (19-36)"


# ─── Visual Helpers ───────────────────────────────────────────────────────────
def clear():  os.system('cls' if os.name == 'nt' else 'clear')

def hr(char="=", width=72, color=GOLD):
    print(f"{color}{char * width}{RESET}")

def center(text, width=72):
    plain = re.sub(r'\033\[[0-9;]*m', '', text)
    pad   = max(0, (width - len(plain)) // 2)
    return " " * pad + text

def print_header():
    hr("=")
    print(center(f"{GOLD}{BOLD}+  GRAND CASINO ROYALE  +{RESET}"))
    print(center(f"{CREAM}{ITALIC}Established 1875  .  Monte Carlo, Monaco{RESET}"))
    hr("-", color=AMBER)
    print(center(f"{AMBER}- La Roulette Europeenne  .  Pattern Detection Suite -{RESET}"))
    hr("=")
    print()

def spinning_animation(result):
    frames = [
        "  0   3   6   9  12  15  18  21  24  27  30  33  36",
        " 36   2   5   8  11  14  17  20  23  26  29  32  35",
        " 35   1   4   7  10  13  16  19  22  25  28  31  34",
        " 34   0   3   6   9  12  15  18  21  24  27  30  33",
        " 33  36   2   5   8  11  14  17  20  23  26  29  32",
    ]
    W = 54
    print(f"\n{GOLD}  +{'--'*W//2}+{RESET}")
    print(f"{GOLD}  |{RESET}{AMBER}{'  LA BILLE TOURNE ...':^{W}}{RESET}{GOLD}|{RESET}")
    for i in range(22):
        sys.stdout.write(f"\r{GOLD}  |{RESET}{CREAM}{frames[i%len(frames)]:<{W}}{RESET}{GOLD}|{RESET}")
        sys.stdout.flush()
        time.sleep(0.06 + i * 0.003)
    col = num_color(result)
    if   result == 0:               label,bg = f"  ZERO ({result})  ","  \033[48;2;0;90;40m"
    elif result in RED_NUMBERS:     label,bg = f"  ROUGE ({result})  ","\033[48;2;120;0;10m"
    else:                           label,bg = f"  NOIR ({result})  ", "\033[48;2;20;20;20m"
    sys.stdout.write(f"\r{GOLD}  |{RESET}{bg}{col}{BOLD}{label:^{W}}{RESET}{GOLD}|{RESET}\n")
    print(f"{GOLD}  +{'--'*W//2}+{RESET}\n")
    sys.stdout.flush()

def _bar(v, mx, w=20, fill="*", empty="."):
    b = int((v/mx)*w) if mx else 0
    return fill*b + empty*(w-b)

def _pct_bar(pct, w=20):
    b = int(pct/100*w)
    return "*"*b + "."*(w-b)

def pause():
    hr("-", color=SILVER)
    input(f"\n  {AMBER}Press ENTER to continue ...{RESET}  ")


# =============================================================================
#  OUTCOME TRACKER
# =============================================================================

class OutcomeTracker:
    def __init__(self):
        self.spins      = []
        self.timestamps = []
        self._cur_colour     = None; self._cur_colour_len  = 0
        self._cur_parity     = None; self._cur_parity_len  = 0
        self.streaks         = defaultdict(list)
        self.max_streak      = {}

    def record(self, n):
        self.spins.append(n); self.timestamps.append(time.time())
        self._update_streaks(n)

    def record_batch(self, nums):
        t0 = time.time()
        for i,n in enumerate(nums):
            self.spins.append(n); self.timestamps.append(t0 + i*0.001)
            self._update_streaks(n)

    def _update_streaks(self, n):
        col = colour_of(n); par = parity_of(n)
        if col == self._cur_colour:   self._cur_colour_len += 1
        else:
            if self._cur_colour: self._finish_streak("colour", self._cur_colour, self._cur_colour_len)
            self._cur_colour = col; self._cur_colour_len = 1
        if par == self._cur_parity:   self._cur_parity_len += 1
        else:
            if self._cur_parity: self._finish_streak("parity", self._cur_parity, self._cur_parity_len)
            self._cur_parity = par; self._cur_parity_len = 1

    def _finish_streak(self, kind, val, length):
        self.streaks[kind].append((val, length))
        if length > self.max_streak.get(kind, (None,0))[1]:
            self.max_streak[kind] = (val, length)

    def flush_streaks(self):
        if self._cur_colour:
            self._finish_streak("colour", self._cur_colour, self._cur_colour_len)
            self._cur_colour = None; self._cur_colour_len = 0
        if self._cur_parity:
            self._finish_streak("parity", self._cur_parity, self._cur_parity_len)
            self._cur_parity = None; self._cur_parity_len = 0

    def frequency(self):    return Counter(self.spins)
    def colour_frequency(self): return dict(Counter(colour_of(n) for n in self.spins))
    def parity_frequency(self): return dict(Counter(parity_of(n) for n in self.spins))
    def dozen_frequency(self):  return dict(Counter(dozen_of(n)  for n in self.spins))
    def half_frequency(self):   return dict(Counter(half_of(n)   for n in self.spins))

    def distribution_over_time(self, segments=10):
        n   = len(self.spins); bsz = max(1, n//segments); out = []
        for s in range(segments):
            sl = self.spins[s*bsz:(s+1)*bsz]
            if not sl: continue
            cnt = Counter(sl); tot = len(sl)
            out.append({
                "segment":   s+1, "spins": tot,
                "red_pct":   sum(cnt[x] for x in RED_NUMBERS)/tot*100,
                "black_pct": sum(cnt[x] for x in BLACK_NUMBERS)/tot*100,
                "zero_pct":  cnt.get(0,0)/tot*100,
                "odd_pct":   sum(v for k,v in cnt.items() if k!=0 and k%2==1)/tot*100,
                "even_pct":  sum(v for k,v in cnt.items() if k!=0 and k%2==0)/tot*100,
                "top5":      cnt.most_common(5),
            })
        return out

    def streak_summary(self):
        out = {}
        for kind in ("colour","parity"):
            s = self.streaks[kind]
            if not s: continue
            lengths = [l for _,l in s]; by_val = defaultdict(list)
            for val,l in s: by_val[val].append(l)
            out[kind] = {
                "total_streaks": len(s),
                "avg_length":    sum(lengths)/len(lengths),
                "max":           self.max_streak.get(kind,(None,0)),
                "by_value":      {v:{"count":len(ls),"avg":sum(ls)/len(ls),"max":max(ls)}
                                   for v,ls in by_val.items()},
            }
        return out

    def export_csv(self, path):
        with open(path,"w",newline="") as f:
            w = csv.writer(f)
            w.writerow(["spin_index","number","colour","parity","dozen","half","timestamp"])
            for i,(n,ts) in enumerate(zip(self.spins,self.timestamps),1):
                w.writerow([i,n,colour_of(n),parity_of(n),dozen_of(n),half_of(n),
                            datetime.fromtimestamp(ts).isoformat()])

    def export_json(self, path):
        data = {
            "meta":      {"total_spins":len(self.spins),"generated":datetime.now().isoformat()},
            "spins":     [{"index":i,"number":n,"colour":colour_of(n),
                           "parity":parity_of(n),"dozen":dozen_of(n),
                           "timestamp":datetime.fromtimestamp(ts).isoformat()}
                          for i,(n,ts) in enumerate(zip(self.spins,self.timestamps),1)],
            "frequency": dict(self.frequency()),
            "streaks":   self.streak_summary(),
        }
        with open(path,"w") as f: json.dump(data,f,indent=2)


# =============================================================================
#  PATTERN DETECTION ENGINE
# =============================================================================

class PatternDetector:
    """
    Three independent detection modules:
      1. Streak Irregularity Analysis  – tests observed streak distribution
         against geometric-series expectation using a KS-like stat.
      2. Outcome Clustering            – sliding-window scan for local
         concentration of specific outcomes (colour/number/dozen).
      3. Deviation from Expected       – per-number and per-category
         z-scores + chi-square with anomaly flagging.
    """

    # ── Expected probabilities ────────────────────────────────────────────────
    P_RED   = 18/37;  P_BLACK = 18/37;  P_ZERO  = 1/37
    P_ODD   = 18/37;  P_EVEN  = 18/37
    P_NUM   = 1/37

    def __init__(self, tracker: OutcomeTracker):
        self.t   = tracker
        self.n   = len(tracker.spins)
        self.exp = self.n / 37          # expected hits per number

    # =========================================================================
    # 1. STREAK IRREGULARITY
    # =========================================================================

    def streak_irregularity(self) -> dict:
        """
        For colour streaks, compare observed length-frequency distribution
        against geometric expectation: P(streak=k) = p*(1-p)^(k-1)
        where p = P(colour change) ≈ 1 - P_RED (for red streaks, etc.)

        Returns per-value analysis + an overall irregularity score [0-100].
        """
        results = {}
        ss = self.t.streak_summary()
        if "colour" not in ss:
            return {}

        for val, p_cont in [("red", P_CONT := 18/37),
                             ("black", 18/37),
                             ("zero", 1/37)]:
            lengths = [l for v,l in self.t.streaks["colour"] if v == val]
            if len(lengths) < 5:
                continue
            p_cont   = {"red":18/37,"black":18/37,"zero":1/37}[val]
            p_break  = 1 - p_cont
            total    = len(lengths)
            max_len  = max(lengths)
            lc       = Counter(lengths)

            # Expected count for each streak length k under geometric model
            geo_expected = {}
            for k in range(1, max_len+1):
                geo_expected[k] = total * p_break * (p_cont ** (k-1))

            # KS-style max deviation + weighted score
            cum_obs  = 0.0; cum_exp = 0.0; ks_stat = 0.0
            anomaly_lengths = []
            for k in range(1, max_len+1):
                obs  = lc.get(k, 0)
                exp  = geo_expected.get(k, 0.001)
                cum_obs += obs / total
                cum_exp += exp / total if total else 0
                dev      = abs(cum_obs - cum_exp)
                if dev > ks_stat: ks_stat = dev
                if exp > 0.5 and abs(obs - exp) / exp > 0.5:
                    anomaly_lengths.append((k, obs, exp, (obs-exp)/exp*100))

            # Irregularity score: KS scaled to 0-100
            # KS crit val at 5% for large n ≈ 1.36/sqrt(n)
            n_s   = total
            crit  = 1.36 / math.sqrt(n_s) if n_s > 0 else 1
            score = min(100, ks_stat / crit * 50)

            # Probability of longest observed streak under null (geometric tail)
            p_longest = p_cont ** (max_len - 1) * p_break
            p_longest_at_least = p_cont ** (max_len - 1)   # P(L >= max_len) in one trial
            # Over n trials, expected count
            exp_max_count = self.n * p_longest_at_least

            results[val] = {
                "total_streaks":    total,
                "avg_len":          sum(lengths)/len(lengths),
                "max_len":          max_len,
                "ks_statistic":     ks_stat,
                "ks_critical":      crit,
                "irregularity_score": score,
                "flag":             ks_stat > crit,
                "anomaly_lengths":  anomaly_lengths[:5],
                "longest_expected_count": exp_max_count,
                "geo_expected":     geo_expected,
                "observed_counts":  dict(lc),
            }

        return results

    # =========================================================================
    # 2. CLUSTERING DETECTION
    # =========================================================================

    def clustering_analysis(self, window: int = None) -> dict:
        """
        Sliding-window scan. For each window of W spins, count occurrences
        of each colour/number/dozen.  Flag windows where observed count
        exceeds the 99.9th percentile of the binomial(W, p) distribution.
        Uses normal approximation: flag if Z > 3.09 (p<0.001).
        """
        n = self.n
        if n < 50: return {}
        if window is None:
            window = max(20, n // 50)    # adaptive: ~2% of session

        spins = self.t.spins
        results = {}

        # ── Colour clustering ─────────────────────────────────────────────────
        for col, p_col in [("red", 18/37), ("black", 18/37), ("zero", 1/37)]:
            mu    = window * p_col
            sigma = math.sqrt(window * p_col * (1 - p_col))
            if sigma == 0: continue

            hot_windows  = []   # (start, count, z)
            cold_windows = []

            for i in range(n - window + 1):
                sl  = spins[i:i+window]
                cnt = sum(1 for x in sl if colour_of(x) == col)
                z   = (cnt - mu) / sigma
                if z > 3.09:
                    hot_windows.append((i+1, cnt, z))
                elif z < -3.09:
                    cold_windows.append((i+1, cnt, z))

            # Merge overlapping hot windows into clusters
            def merge_windows(wins, w):
                if not wins: return []
                wins = sorted(wins)
                clusters = []; cur = list(wins[0])
                for wx in wins[1:]:
                    if wx[0] - cur[0] < w:
                        if wx[2] > cur[2]: cur = list(wx)
                    else:
                        clusters.append(tuple(cur)); cur = list(wx)
                clusters.append(tuple(cur))
                return clusters

            results[f"colour_{col}"] = {
                "window":        window,
                "expected_mu":   mu,
                "expected_sigma":sigma,
                "hot_clusters":  merge_windows(hot_windows, window),
                "cold_clusters": merge_windows(cold_windows, window),
                "total_hot":     len(hot_windows),
                "total_cold":    len(cold_windows),
            }

        # ── Number-level hotspot scan ──────────────────────────────────────────
        p_num = 1/37; mu_n = window*p_num
        sigma_n = math.sqrt(window*p_num*(1-p_num))
        num_hotspots = {}
        for num in range(37):
            max_z = -999; best_start = 0; best_cnt = 0
            for i in range(n - window + 1):
                cnt = spins[i:i+window].count(num)
                z   = (cnt - mu_n) / sigma_n if sigma_n else 0
                if z > max_z: max_z = z; best_start = i+1; best_cnt = cnt
            if max_z > 3.09:
                num_hotspots[num] = {"peak_start": best_start,
                                     "peak_count": best_cnt,
                                     "peak_z":     max_z}

        results["number_hotspots"] = num_hotspots

        # ── Dozen clustering ──────────────────────────────────────────────────
        for doz, p_doz in [("1st dozen",12/37),("2nd dozen",12/37),("3rd dozen",12/37)]:
            mu_d = window*p_doz; sig_d = math.sqrt(window*p_doz*(1-p_doz))
            hot = []; cold = []
            for i in range(n-window+1):
                sl  = spins[i:i+window]
                cnt = sum(1 for x in sl if dozen_of(x) == doz)
                z   = (cnt - mu_d) / sig_d if sig_d else 0
                if z >  3.09: hot.append((i+1, cnt, z))
                if z < -3.09: cold.append((i+1, cnt, z))
            results[f"dozen_{doz}"] = {
                "hot_count": len(hot), "cold_count": len(cold),
                "peak_hot":  max(hot,  key=lambda x:x[2])  if hot  else None,
                "peak_cold": min(cold, key=lambda x:x[2])  if cold else None,
            }

        return results

    # =========================================================================
    # 3. DEVIATION FROM EXPECTED
    # =========================================================================

    def deviation_analysis(self) -> dict:
        """
        Per-number z-scores (normal approx to binomial).
        Category chi-square tests (colour 2-way, parity 2-way, dozens 3-way).
        Returns anomaly lists + overall assessment.
        """
        counts  = self.t.frequency()
        n       = self.n
        p       = 1/37
        mu      = n * p
        sigma   = math.sqrt(n * p * (1-p))

        # ── Per-number z-scores ───────────────────────────────────────────────
        num_stats = {}
        for num in range(37):
            obs = counts.get(num, 0)
            z   = (obs - mu) / sigma if sigma else 0
            num_stats[num] = {
                "observed": obs,
                "expected": mu,
                "z_score":  z,
                "p_approx": _two_tail_p(z),
                "flag":     abs(z) > 2.576,   # 99% threshold
                "severe":   abs(z) > 3.291,   # 99.9% threshold
            }

        # ── Chi-square tests ──────────────────────────────────────────────────
        # Colour: red=18/37, black=18/37, zero=1/37
        cf = self.t.colour_frequency()
        chi_colour, df_colour = _chi_sq_test(
            [cf.get("red",0), cf.get("black",0), cf.get("zero",0)],
            [18/37, 18/37, 1/37], n)

        # Parity (excluding zero)
        n_nz   = n - counts.get(0, 0)
        pf     = self.t.parity_frequency()
        chi_parity, df_parity = _chi_sq_test(
            [pf.get("odd",0), pf.get("even",0)],
            [0.5, 0.5], n_nz) if n_nz > 0 else (0, 1)

        # Dozens
        df2 = self.t.dozen_frequency()
        chi_dozens, df_dozens = _chi_sq_test(
            [df2.get("1st dozen",0), df2.get("2nd dozen",0), df2.get("3rd dozen",0)],
            [12/36, 12/36, 12/36], n - counts.get(0,0)) if n > 0 else (0,2)

        # Full 37-pocket chi-square
        chi_full = sum((counts.get(i,0) - mu)**2 / mu for i in range(37))
        df_full  = 36

        # ── Anomaly flags ─────────────────────────────────────────────────────
        flagged   = [(num, d) for num,d in num_stats.items() if d["flag"]]
        severe    = [(num, d) for num,d in num_stats.items() if d["severe"]]
        overdue   = sorted([(num,d) for num,d in num_stats.items()
                             if d["z_score"] < -1.5],
                            key=lambda x: x[1]["z_score"])
        hot_nums  = sorted([(num,d) for num,d in num_stats.items()
                             if d["z_score"] > 1.5],
                            key=lambda x: -x[1]["z_score"])

        return {
            "num_stats":    num_stats,
            "chi_full":     chi_full,   "df_full":    df_full,
            "chi_colour":   chi_colour, "df_colour":  df_colour,
            "chi_parity":   chi_parity, "df_parity":  df_parity,
            "chi_dozens":   chi_dozens, "df_dozens":  df_dozens,
            "flagged":      flagged,
            "severe":       severe,
            "overdue":      overdue[:5],
            "hot_numbers":  hot_nums[:5],
            "overall_uniform": chi_full < df_full * 1.5,
        }


# ── Stat helpers ──────────────────────────────────────────────────────────────

def _chi_sq_test(observed, proportions, n_total):
    """Return (chi_sq, df)."""
    if n_total <= 0: return 0, len(observed)-1
    chi = sum((o - n_total*p)**2 / (n_total*p)
               for o,p in zip(observed,proportions) if n_total*p > 0)
    return chi, len(observed)-1

def _two_tail_p(z):
    """Rough two-tailed p approximation via error function."""
    az = abs(z)
    p_one = 0.5 * math.erfc(az / math.sqrt(2))
    p = 2 * p_one
    if   p > 0.05:  return ">0.05 (not sig.)"
    elif p > 0.01:  return "0.01-0.05  *"
    elif p > 0.001: return "0.001-0.01 **"
    else:           return "<0.001     ***"

def _chi_pvalue_label(chi, df):
    """Very rough label using Wilson-Hilferty normal approximation."""
    if df <= 0: return "n/a"
    k = df
    z = ((chi/k)**(1/3) - (1 - 2/(9*k))) / math.sqrt(2/(9*k))
    p_approx = 0.5 * math.erfc(z / math.sqrt(2))
    if   p_approx > 0.05:  return f"p>{0.05}  (uniform)"
    elif p_approx > 0.01:  return f"p~0.01-0.05  *"
    elif p_approx > 0.001: return f"p~0.001-0.01 **"
    else:                  return f"p<0.001  *** ALERT"


# =============================================================================
#  PATTERN DETECTION DISPLAY
# =============================================================================

def print_pattern_detection(tracker: OutcomeTracker):
    pd = PatternDetector(tracker)
    n  = tracker.n if hasattr(tracker,"n") else len(tracker.spins)

    ALERT_COLOR = ROSE
    OK_COLOR    = LTGREEN

    # =========================================================================
    # HEADER
    # =========================================================================
    hr("=", color=ORANGE)
    print(center(f"{ORANGE}{BOLD}+  PATTERN DETECTION ENGINE  +{RESET}"))
    print(center(f"{DIM}{n:,} spins analysed{RESET}"))
    hr("=", color=ORANGE)
    print()

    if n < 100:
        print(f"  {AMBER}  Minimum 100 spins required for pattern analysis.{RESET}\n")
        return

    # =========================================================================
    # MODULE 1 — STREAK IRREGULARITY
    # =========================================================================
    hr("-", color=PURPLE)
    print(f"  {PURPLE}{BOLD}MODULE 1  |  STREAK IRREGULARITY ANALYSIS{RESET}")
    print(f"  {DIM}Tests whether streak length distribution follows geometric expectation{RESET}")
    hr("-", color=PURPLE)
    print()

    si = pd.streak_irregularity()
    if not si:
        print(f"  {GREY}Insufficient streak data.{RESET}\n")
    else:
        for val, d in si.items():
            vc = CRIMSON if val=="red" else LTGREEN if val=="zero" else SILVER
            flag_sym = f"{ALERT_COLOR}{BOLD} !!! IRREGULAR !!!{RESET}" if d["flag"] else f"{OK_COLOR} within normal range{RESET}"
            print(f"  {vc}{BOLD}{val.upper()}{RESET} streaks   {flag_sym}")
            print(f"  {SILVER}{'─'*66}{RESET}")

            score = d["irregularity_score"]
            score_col = ALERT_COLOR if score > 60 else (AMBER if score > 30 else OK_COLOR)
            score_bar_len = int(score/100*30)
            score_bar = f"{score_col}{'|'*score_bar_len}{GREY}{'.'*(30-score_bar_len)}{RESET}"

            print(f"    {CREAM}Irregularity Score : {score_col}{BOLD}{score:5.1f}/100{RESET}  [{score_bar}]")
            print(f"    {CREAM}KS Statistic       : {AMBER}{d['ks_statistic']:.4f}{RESET}  "
                  f"(critical = {AMBER}{d['ks_critical']:.4f}{RESET})")
            print(f"    {CREAM}Total Streaks      : {AMBER}{d['total_streaks']:,}{RESET}  "
                  f"avg length = {AMBER}{d['avg_len']:.2f}{RESET}  "
                  f"max = {AMBER}{d['max_len']}{RESET}")

            exp_mx = d["longest_expected_count"]
            exp_col = AMBER if exp_mx >= 0.5 else ALERT_COLOR
            print(f"    {CREAM}Longest run ({d['max_len']:>2}x) expected count in session: "
                  f"{exp_col}{exp_mx:.2f}{RESET}")

            # Show obs vs expected for first 10 lengths
            print()
            print(f"    {SILVER}{'Len':>4}  {'Observed':>9}  {'Expected':>9}  {'Ratio':>8}  Comparison{RESET}")
            print(f"    {GREY}{'─'*56}{RESET}")
            geo   = d["geo_expected"]
            obs_c = d["observed_counts"]
            max_len_show = min(max(obs_c.keys()), 15)
            for k in range(1, max_len_show+1):
                o  = obs_c.get(k, 0)
                e  = geo.get(k, 0.001)
                ratio = o/e if e > 0 else 0
                ratio_col = (ALERT_COLOR if ratio>2 or ratio<0.3 else
                             AMBER       if ratio>1.5 or ratio<0.5 else OK_COLOR)
                o_bar = "|"*min(o,20); e_bar = "."*min(int(e),20)
                print(f"    {CREAM}{k:>4}  {o:>9,}  {e:>9.1f}  "
                      f"{ratio_col}{ratio:>7.2f}x{RESET}  "
                      f"{CRIMSON}{o_bar}{RESET}{GREY}{e_bar}{RESET}")
            if max(obs_c.keys(), default=0) > 15:
                print(f"    {DIM}     ... longer streaks exist (shown up to 15){RESET}")
            print()

            if d["anomaly_lengths"]:
                print(f"    {ALERT_COLOR}{BOLD}Anomalous lengths:{RESET}")
                for k,o,e,pct in d["anomaly_lengths"]:
                    direction = "EXCESS" if o > e else "DEFICIT"
                    print(f"      {ALERT_COLOR}Length {k:>2}: observed {o:,}  expected {e:.1f}  "
                          f"({pct:+.0f}%)  [{direction}]{RESET}")
            print()

    # =========================================================================
    # MODULE 2 — CLUSTERING
    # =========================================================================
    hr("-", color=CYAN)
    print(f"  {CYAN}{BOLD}MODULE 2  |  OUTCOME CLUSTERING DETECTION{RESET}")
    print(f"  {DIM}Sliding-window Z-test: flags local concentrations (|Z|>3.09, p<0.001){RESET}")
    hr("-", color=CYAN)
    print()

    window = max(20, n//50)
    ca     = pd.clustering_analysis(window=window)
    if not ca:
        print(f"  {GREY}Insufficient data for clustering analysis.{RESET}\n")
    else:
        print(f"  {SILVER}Window size: {AMBER}{window}{RESET} spins  "
              f"(~{window/n*100:.1f}% of session)\n")

        # Colour clusters
        print(f"  {AMBER}{BOLD}-- Colour Clusters{RESET}")
        print(f"  {SILVER}{'Colour':<10}{'Hot Windows':>12}{'Cold Windows':>14}  Assessment{RESET}")
        print(f"  {GREY}{'─'*58}{RESET}")
        for col, cc in [("red",CRIMSON),("black",SILVER),("zero",LTGREEN)]:
            key = f"colour_{col}"
            if key not in ca: continue
            d   = ca[key]
            hot = d["total_hot"]; cold = d["total_cold"]
            flag = hot > 0 or cold > 0
            fc   = ALERT_COLOR if flag else OK_COLOR
            asmt = f"{ALERT_COLOR}CLUSTERS DETECTED{RESET}" if flag else f"{OK_COLOR}Uniform{RESET}"
            print(f"  {cc}{col:<10}{RESET}  {CRIMSON}{hot:>10}{RESET}  {CYAN}{cold:>12}{RESET}  {asmt}")
            if d["hot_clusters"]:
                for start, cnt, z in d["hot_clusters"][:3]:
                    print(f"    {ALERT_COLOR}HOT  at spin {start:>6}: "
                          f"count={cnt} in {window} spins  Z={z:+.2f}{RESET}")
            if d["cold_clusters"]:
                for start, cnt, z in d["cold_clusters"][:3]:
                    print(f"    {CYAN}COLD at spin {start:>6}: "
                          f"count={cnt} in {window} spins  Z={z:+.2f}{RESET}")
        print()

        # Number hotspots
        hs = ca.get("number_hotspots", {})
        print(f"  {AMBER}{BOLD}-- Number Hotspots  (peak Z > 3.09 in any {window}-spin window){RESET}")
        if not hs:
            print(f"  {OK_COLOR}  No individual number hotspots detected.{RESET}")
        else:
            print(f"  {SILVER}  {'Num':<5}{'Peak Start':>12}{'Count':>8}{'Z-score':>10}  Colour{RESET}")
            print(f"  {GREY}  {'─'*50}{RESET}")
            for num, d in sorted(hs.items(), key=lambda x: -x[1]["peak_z"]):
                nc = num_color(num)
                cl = colour_of(num)
                cc = CRIMSON if cl=="red" else LTGREEN if cl=="zero" else SILVER
                print(f"  {ALERT_COLOR}  {nc}{num:<5}{RESET}"
                      f"{CREAM}{d['peak_start']:>12}{RESET}"
                      f"{AMBER}{d['peak_count']:>8}{RESET}"
                      f"{ALERT_COLOR}{d['peak_z']:>10.2f}{RESET}  "
                      f"{cc}{cl}{RESET}")
        print()

        # Dozen clusters
        print(f"  {AMBER}{BOLD}-- Dozen Clusters{RESET}")
        print(f"  {SILVER}{'Dozen':<14}{'Hot':>6}{'Cold':>6}  Peak Z{RESET}")
        print(f"  {GREY}{'─'*40}{RESET}")
        for doz in ["1st dozen","2nd dozen","3rd dozen"]:
            key = f"dozen_{doz}"
            if key not in ca: continue
            d   = ca[key]
            ph  = d["peak_hot"];  pc = d["peak_cold"]
            hot_str  = (f"  {ALERT_COLOR}HOT  spin {ph[0]}  Z={ph[2]:+.2f}{RESET}" if ph else "")
            cold_str = (f"  {CYAN}COLD spin {pc[0]}  Z={pc[2]:+.2f}{RESET}" if pc else "")
            flag = d["hot_count"]>0 or d["cold_count"]>0
            fc   = ALERT_COLOR if flag else OK_COLOR
            print(f"  {fc}{doz:<14}{RESET}"
                  f"{CRIMSON}{d['hot_count']:>6}{RESET}"
                  f"{CYAN}{d['cold_count']:>6}{RESET}"
                  f"{hot_str}{cold_str}")
        print()

    # =========================================================================
    # MODULE 3 — DEVIATION FROM EXPECTED
    # =========================================================================
    hr("-", color=TEAL)
    print(f"  {TEAL}{BOLD}MODULE 3  |  DEVIATION FROM EXPECTED PROBABILITY{RESET}")
    print(f"  {DIM}Z-scores + chi-square tests against true roulette probabilities{RESET}")
    hr("-", color=TEAL)
    print()

    da = pd.deviation_analysis()

    # ── Chi-square battery ────────────────────────────────────────────────────
    print(f"  {AMBER}{BOLD}-- Chi-Square Test Battery{RESET}")
    print(f"  {SILVER}{'Test':<22}{'chi-sq':>9}{'df':>5}  p-value / verdict{RESET}")
    print(f"  {GREY}{'─'*66}{RESET}")

    for label, chi, df in [
        ("All 37 numbers",     da["chi_full"],   da["df_full"]),
        ("Colour split",       da["chi_colour"], da["df_colour"]),
        ("Odd / Even",         da["chi_parity"], da["df_parity"]),
        ("Dozens (1-2-3)",     da["chi_dozens"], da["df_dozens"]),
    ]:
        verdict = _chi_pvalue_label(chi, df)
        flag    = "***" in verdict or "**" in verdict
        vc      = ALERT_COLOR if "***" in verdict else (AMBER if "**" in verdict or "*" in verdict else OK_COLOR)
        alert   = f"  {ALERT_COLOR}{BOLD}<-- ANOMALY{RESET}" if flag else ""
        print(f"  {CREAM}{label:<22}{RESET}  {AMBER}{chi:>7.2f}{RESET}"
              f"  {GREY}{df:>3}{RESET}  {vc}{verdict}{RESET}{alert}")
    print()

    # ── Z-score league table ──────────────────────────────────────────────────
    print(f"  {AMBER}{BOLD}-- Number Deviation Z-Score Table{RESET}")
    print(f"  {DIM}  |Z|>2.58 = 99% flag (**)  |Z|>3.29 = 99.9% flag (***){RESET}")
    print()
    print(f"  {SILVER}{'No':>3}  {'Col':<6}  {'Obs':>6}  {'Exp':>6}  "
          f"{'Z':>7}  {'p-value':>16}  Flag{RESET}")
    print(f"  {GREY}{'─'*68}{RESET}")

    ns = da["num_stats"]
    for num in range(37):
        d   = ns[num]
        z   = d["z_score"]
        nc  = num_color(num)
        if num == 0:   cl = f"{LTGREEN}Zero  {RESET}"
        elif num in RED_NUMBERS: cl = f"{CRIMSON}Rouge {RESET}"
        else:          cl = f"{SILVER}Noir  {RESET}"

        zc  = (ALERT_COLOR if d["severe"] else
               ORANGE      if d["flag"]   else
               OK_COLOR    if abs(z)<0.5  else AMBER)
        sym = f"{ALERT_COLOR}***{RESET}" if d["severe"] else (f"{ORANGE}** {RESET}" if d["flag"] else "   ")
        print(f"  {nc}{num:>3}{RESET}  {cl}  "
              f"{CREAM}{d['observed']:>6,}{RESET}  "
              f"{GREY}{d['expected']:>6.1f}{RESET}  "
              f"{zc}{z:>+7.2f}{RESET}  "
              f"{DIM}{d['p_approx']:>16}{RESET}  {sym}")
    print()

    # ── Summary anomaly panel ─────────────────────────────────────────────────
    print(f"  {AMBER}{BOLD}-- Anomaly Summary{RESET}")
    print(f"  {SILVER}{'─'*66}{RESET}")

    def anomaly_row(title, items, direction):
        if not items:
            print(f"  {OK_COLOR}{title:<28} None detected{RESET}")
            return
        nums_str = "  ".join(
            f"{num_color(num)}{num}{RESET}(Z={d['z_score']:+.1f})" for num,d in items
        )
        print(f"  {ALERT_COLOR}{title:<28}{RESET}  {nums_str}")

    anomaly_row("Hot numbers (Z>+1.5):",   da["hot_numbers"],  "+")
    anomaly_row("Overdue numbers (Z<-1.5):",da["overdue"],     "-")
    print()

    severe = da["severe"]
    if severe:
        print(f"  {ALERT_COLOR}{BOLD}  *** SEVERE DEVIATIONS (99.9% confidence) ***{RESET}")
        for num, d in severe:
            direction = "OVER" if d["z_score"] > 0 else "UNDER"
            print(f"    {ALERT_COLOR}Number {num_color(num)}{num}{RESET}{ALERT_COLOR}: "
                  f"{direction}-represented  "
                  f"obs={d['observed']}  exp={d['expected']:.1f}  "
                  f"Z={d['z_score']:+.2f}{RESET}")
    else:
        print(f"  {OK_COLOR}  No severe deviations detected at 99.9% confidence.{RESET}")
    print()

    # ── Overall verdict ───────────────────────────────────────────────────────
    hr("-", color=ORANGE)
    n_flags    = len(da["flagged"])
    n_severe   = len(da["severe"])
    has_cluster= any(
        (ca.get(f"colour_{c}",{}).get("total_hot",0) +
         ca.get(f"colour_{c}",{}).get("total_cold",0)) > 0
        for c in ["red","black","zero"]
    ) if ca else False
    has_irr    = any(d.get("flag",False) for d in si.values()) if si else False

    alert_count = (1 if has_irr else 0) + (1 if has_cluster else 0) + (1 if n_severe>0 else 0)

    if alert_count == 0:
        verdict_color = OK_COLOR
        verdict_text  = "WHEEL BEHAVIOUR CONSISTENT WITH TRUE RANDOMNESS"
        verdict_sym   = "OK"
    elif alert_count == 1:
        verdict_color = AMBER
        verdict_text  = "MINOR ANOMALIES DETECTED — WITHIN PLAUSIBLE VARIANCE"
        verdict_sym   = "~"
    elif alert_count == 2:
        verdict_color = ORANGE
        verdict_text  = "NOTABLE PATTERNS DETECTED — INVESTIGATE FURTHER"
        verdict_sym   = "!"
    else:
        verdict_color = ALERT_COLOR
        verdict_text  = "MULTIPLE ANOMALIES — DISTRIBUTION WARRANTS SCRUTINY"
        verdict_sym   = "!!!"

    print()
    print(center(f"{verdict_color}{BOLD}[{verdict_sym}]  {verdict_text}  [{verdict_sym}]{RESET}"))
    print()
    print(f"  {SILVER}Numbers flagged (99%):  {AMBER}{n_flags}{RESET}  "
          f"| Severe (99.9%): {ALERT_COLOR if n_severe else OK_COLOR}{n_severe}{RESET}  "
          f"| Clusters: {ALERT_COLOR if has_cluster else OK_COLOR}{'YES' if has_cluster else 'NO'}{RESET}  "
          f"| Streak irregularity: {ALERT_COLOR if has_irr else OK_COLOR}{'YES' if has_irr else 'NO'}{RESET}")
    print()
    hr("=", color=ORANGE)


# =============================================================================
#  EXISTING REPORTS (unchanged)
# =============================================================================

def build_frequency_table(results):
    counts = Counter(results); n = len(results); lines = []
    lines.append(f"\n{GOLD}{'-'*70}{RESET}")
    lines.append(center(f"{AMBER}{BOLD}FREQUENCY TABLE -- {n:,} SPINS{RESET}"))
    lines.append(f"{GOLD}{'-'*70}{RESET}")
    lines.append(f"  {CREAM}{'No':>3}  {'Colour':<7}  {'Hits':>7}  {'%':>7}  {'Distribution':<24}{RESET}")
    lines.append(f"  {SILVER}{'-'*60}{RESET}")
    max_count = max(counts.values())
    for num in range(37):
        hit = counts.get(num,0); pct = hit/n*100
        bar = "|"*int((hit/max_count)*24) + "."*(24-int((hit/max_count)*24))
        if num==0:   cl,bc = f"{LTGREEN}Zero  {RESET}",LTGREEN
        elif num in RED_NUMBERS: cl,bc = f"{CRIMSON}Rouge {RESET}",CRIMSON
        else:        cl,bc = f"{SILVER}Noir  {RESET}",GREY
        nc = num_color(num)
        lines.append(f"  {nc}{num:>3}{RESET}  {cl}  {CREAM}{hit:>7,}{RESET}  {AMBER}{pct:>6.2f}%{RESET}  {bc}{bar}{RESET}")
    lines.append(f"{GOLD}{'-'*70}{RESET}\n")
    return "\n".join(lines)

def build_summary(results):
    n=len(results); counts=Counter(results)
    reds=sum(counts[x] for x in RED_NUMBERS); blacks=sum(counts[x] for x in BLACK_NUMBERS)
    greens=counts.get(0,0); hottest=counts.most_common(5)
    coldest=sorted(counts.items(),key=lambda x:x[1])[:5]
    expected=n/37
    chi_sq=sum((counts.get(i,0)-expected)**2/expected for i in range(37))
    unif="Excellent" if chi_sq<54 else ("Good" if chi_sq<72 else "Review")
    lines=[]
    lines.append(f"\n{GOLD}{'='*70}{RESET}")
    lines.append(center(f"{AMBER}{BOLD}+  CROUPIER'S SUMMARY REPORT  +{RESET}"))
    lines.append(f"{GOLD}{'='*70}{RESET}")
    def row(label,val,color=CREAM): lines.append(f"  {SILVER}{label:<30}{RESET}  {color}{val}{RESET}")
    row("Total Spins:",f"{n:,}"); row("Expected hits/number:",f"{expected:,.2f}  (1/37 = {100/37:.4f}%)")
    lines.append(f"  {DIM}{'.'*66}{RESET}")
    row("Red (Rouge):",f"{reds:,}  ({reds/n*100:.3f}%)",CRIMSON)
    row("Black (Noir):",f"{blacks:,}  ({blacks/n*100:.3f}%)",SILVER)
    row("Zero:",f"{greens:,}  ({greens/n*100:.3f}%)",LTGREEN)
    lines.append(f"  {DIM}{'.'*66}{RESET}")
    hot="  ".join(f"{num_color(n)}{n}{RESET}x{c:,}" for n,c in hottest)
    cld="  ".join(f"{num_color(n)}{n}{RESET}x{c:,}" for n,c in coldest)
    lines.append(f"  {SILVER}{'Hottest numbers:':<30}{RESET}  {hot}")
    lines.append(f"  {SILVER}{'Coldest numbers:':<30}{RESET}  {cld}")
    lines.append(f"  {DIM}{'.'*66}{RESET}")
    lines.append(f"  {SILVER}{'Chi-sq Goodness-of-Fit:':<30}{RESET}  {AMBER}{chi_sq:.2f}{RESET}  {DIM}(df=36) -> {LTGREEN}{unif}{RESET}")
    lines.append(f"{GOLD}{'='*70}{RESET}\n")
    return "\n".join(lines)

def print_streak_report(tracker):
    ss=tracker.streak_summary(); n=len(tracker.spins)
    hr("=",color=PURPLE)
    print(center(f"{PURPLE}{BOLD}+  WIN / LOSS STREAK REPORT  +{RESET}"))
    hr("-",color=PURPLE); print()
    for kind,label in [("colour","COLOUR STREAKS"),("parity","ODD / EVEN STREAKS")]:
        if kind not in ss: continue
        d=ss[kind]
        print(f"  {AMBER}{BOLD}  {label}{RESET}")
        print(f"  {SILVER}{'-'*62}{RESET}")
        print(f"  {CREAM}Total streak events : {AMBER}{d['total_streaks']:,}{RESET}")
        print(f"  {CREAM}Average streak len  : {AMBER}{d['avg_length']:.2f}{RESET}")
        mx_val,mx_len=d["max"]
        mx_col=CRIMSON if mx_val=="red" else LTGREEN if mx_val=="zero" else SILVER
        print(f"  {CREAM}Longest streak      : {mx_col}{BOLD}{mx_val.upper()}{RESET}  {AMBER}x{mx_len}{RESET}")
        print()
        print(f"  {SILVER}{'Value':<14}{'Streaks':>8}{'Avg Len':>10}{'Max Len':>10}  Profile{RESET}")
        print(f"  {GREY}{'-'*64}{RESET}")
        max_count=max(v["count"] for v in d["by_value"].values()) or 1
        for val,vd in sorted(d["by_value"].items()):
            vc=(CRIMSON if val=="red" else LTGREEN if val=="zero" else SILVER if val=="black" else CYAN if val=="even" else AMBER)
            bar=_bar(vd["count"],max_count,20)
            print(f"  {vc}{val:<14}{RESET}{CREAM}{vd['count']:>8,}{RESET}{AMBER}{vd['avg']:>10.2f}{RESET}{GOLD}{vd['max']:>10}{RESET}  {vc}{bar}{RESET}")
        print()
    all_cs=[l for _,l in tracker.streaks.get("colour",[])]
    if all_cs:
        print(f"  {AMBER}{BOLD}  STREAK LENGTH HISTOGRAM (colour){RESET}")
        print(f"  {SILVER}{'-'*62}{RESET}")
        lc=Counter(all_cs); max_l=min(max(lc),30); max_c=max(lc.values())
        for l in range(1,max_l+1):
            c=lc.get(l,0); bar=_bar(c,max_c,32)
            print(f"  {CREAM}{l:>3}x  {SILVER}{bar}  {AMBER}{c:,}{RESET}")
        if max(all_cs)>30: print(f"  {DIM}  ... (streaks >30 omitted){RESET}")
        print()
    hr("=",color=PURPLE)

def print_frequency_report(tracker):
    counts=tracker.frequency(); n=len(tracker.spins); expected=n/37
    hr("=",color=GOLD)
    print(center(f"{AMBER}{BOLD}+  NUMBER FREQUENCY REPORT  +{RESET}"))
    hr("-",color=GOLD); print()
    print(f"  {CREAM}{'No':>3}  {'Col':<6}  {'Hits':>7}  {'%':>7}  {'vs Expected':>12}  {'Bar':<26}{RESET}")
    print(f"  {SILVER}{'-'*65}{RESET}")
    max_count=max(counts.values()) if counts else 1
    for num in range(37):
        hit=counts.get(num,0); pct=hit/n*100; diff=hit-expected
        sign="+" if diff>=0 else ""; diff_col=LTGREEN if diff>=0 else CRIMSON
        if num==0:   cl,bar_col=f"{LTGREEN}Zero  {RESET}",LTGREEN
        elif num in RED_NUMBERS: cl,bar_col=f"{CRIMSON}Rouge {RESET}",CRIMSON
        else:        cl,bar_col=f"{SILVER}Noir  {RESET}",GREY
        bar=_bar(hit,max_count,26)
        nc=num_color(num)
        print(f"  {nc}{num:>3}{RESET}  {cl}{CREAM}{hit:>7,}{RESET}  {AMBER}{pct:>6.2f}%{RESET}  {diff_col}{sign}{diff:>+9.1f}{RESET}  {bar_col}{bar}{RESET}")
    print()
    for title,freq_fn,order in [
        ("COLOUR SPLIT",tracker.colour_frequency,["red","black","zero"]),
        ("ODD / EVEN",tracker.parity_frequency,["odd","even","zero"]),
        ("DOZENS",tracker.dozen_frequency,["1st dozen","2nd dozen","3rd dozen","zero"]),
        ("HALVES",tracker.half_frequency,["low (1-18)","high (19-36)","zero"]),
    ]:
        freq=freq_fn(); total=sum(freq.values()) or 1
        print(f"  {AMBER}{BOLD}  {title}{RESET}")
        for k in order:
            v=freq.get(k,0); pct=v/total*100; bar=_pct_bar(pct,28)
            kc=(CRIMSON if k=="red" else LTGREEN if k=="zero" else CYAN if k=="even" else AMBER if "1st" in k else GOLD if "2nd" in k else PURPLE if "3rd" in k else SILVER)
            print(f"    {kc}{k:<18}{RESET}  {CREAM}{v:>8,}  {AMBER}{pct:>6.2f}%{RESET}  {kc}{bar}{RESET}")
        print()
    hr("=",color=GOLD)

def print_distribution_report(tracker, segments=10):
    segs=tracker.distribution_over_time(segments); n=len(tracker.spins)
    hr("=",color=CYAN)
    print(center(f"{CYAN}{BOLD}+  DISTRIBUTION OVER TIME  +{RESET}"))
    print(center(f"{DIM}({segments} equal segments . {n:,} total spins){RESET}"))
    hr("-",color=CYAN); print()
    print(f"  {CREAM}{'Seg':>4}  {'Spins':>7}  {'Red%':>7}  {'Blk%':>7}  {'Zer%':>6}  {'Odd%':>7}  {'Evn%':>7}{RESET}")
    print(f"  {SILVER}{'-'*58}{RESET}")
    for s in segs:
        print(f"  {GOLD}{s['segment']:>4}{RESET}  {CREAM}{s['spins']:>7,}{RESET}  {CRIMSON}{s['red_pct']:>6.2f}%{RESET}  {SILVER}{s['black_pct']:>6.2f}%{RESET}  {LTGREEN}{s['zero_pct']:>5.2f}%{RESET}  {AMBER}{s['odd_pct']:>6.2f}%{RESET}  {CYAN}{s['even_pct']:>6.2f}%{RESET}")
    print()
    SPARK=" 123456789"
    for label,key,col in [("RED",  "red_pct",  CRIMSON),("BLACK","black_pct",SILVER)]:
        print(f"  {AMBER}{BOLD}  {label} % sparkline{RESET}")
        line="  "
        for s in segs:
            idx=int(s[key]/100*(len(SPARK)-1)); line+=f"{col}{SPARK[idx]}{RESET}"
        print(f"  {line}")
        print()
    print(f"  {AMBER}{BOLD}  HOTTEST NUMBER per segment{RESET}")
    print(f"  {SILVER}{'-'*58}{RESET}")
    for s in segs:
        top_str="  ".join(f"{num_color(num)}{num}{RESET}({c})" for num,c in s["top5"])
        print(f"  {GOLD}Seg {s['segment']:>2}{RESET}  {top_str}")
    print()
    hr("=",color=CYAN)


# =============================================================================
#  CORE SIMULATION
# =============================================================================

def spin_wheel():   return random.randint(0,36)
def run_simulation(n): return [spin_wheel() for _ in range(n)]


# ── VISUALIZATION MODULE ── appended to roulette_casino.py ──────────────────

import pathlib as _pathlib
_LIVE_DASHBOARD_PATH = _pathlib.Path(__file__).parent / "casino_dashboard.html"

def _write_live_dashboard(path):
    """Write the live interactive roulette dashboard."""
    # If bundled alongside the script, copy it; otherwise embed inline
    if _LIVE_DASHBOARD_PATH.exists():
        import shutil
        shutil.copy(_LIVE_DASHBOARD_PATH, path)
    else:
        # Fallback: create a redirect page
        with open(path, 'w') as f:
            f.write('<meta http-equiv="refresh" content="0; url=casino_dashboard.html">')


def generate_visualization_html(tracker, output_path=None):
    """
    Build a standalone HTML dashboard (Chart.js) from tracker data.
    Contains 6 panels:
      1. Expected vs Actual — bar chart per number 0-36
      2. Colour Frequency — donut chart
      3. Running Red % — line chart over spin index
      4. Streak Length Distribution — bar + geometric overlay
      5. Frequency Curve — smooth area chart (KDE-style)
      6. Dozen / Parity split — grouped bar chart
    """
    import json as _json, math as _math
    from collections import Counter as _Counter

    spins   = tracker.spins
    n       = len(spins)
    counts  = _Counter(spins)
    expected = n / 37

    # ── Dataset prep ──────────────────────────────────────────────────────────
    nums      = list(range(37))
    observed  = [counts.get(i, 0) for i in nums]
    exp_flat  = [round(expected, 2)] * 37

    # Colour pie
    reds   = sum(counts[x] for x in RED_NUMBERS)
    blacks = sum(counts[x] for x in BLACK_NUMBERS)
    zeros  = counts.get(0, 0)

    # Running red % (sample every max(1, n//200) spins)
    step = max(1, n // 300)
    run_labels, run_red, run_exp = [], [], []
    for i in range(step, n + 1, step):
        sl  = spins[:i]
        r   = sum(1 for x in sl if x in RED_NUMBERS)
        run_labels.append(i)
        run_red.append(round(r / i * 100, 2))
        run_exp.append(round(18 / 37 * 100, 2))

    # Streak length distribution
    colour_streaks = [l for _, l in tracker.streaks.get("colour", [])]
    max_streak_len = max(colour_streaks) if colour_streaks else 10
    sc = _Counter(colour_streaks)
    streak_labels = list(range(1, min(max_streak_len, 20) + 1))
    streak_obs    = [sc.get(k, 0) for k in streak_labels]
    total_streaks = len(colour_streaks)
    p_cont = 18 / 37
    p_brk  = 1 - p_cont
    streak_geo = [round(total_streaks * p_brk * (p_cont ** (k - 1)), 2)
                  for k in streak_labels]

    # Dozen / parity
    df2     = tracker.dozen_frequency()
    pf      = tracker.parity_frequency()
    nz      = n - zeros
    dozen_data  = [df2.get("1st dozen", 0), df2.get("2nd dozen", 0), df2.get("3rd dozen", 0)]
    dozen_exp   = [round(nz * 12 / 36, 1)] * 3
    parity_data = [pf.get("odd", 0), pf.get("even", 0)]
    parity_exp  = [round(nz * 0.5, 1)] * 2

    # Frequency curve — kernel density style (Gaussian, bandwidth = 1.5)
    bw = 1.5
    kde_x = [i for i in range(37)]
    kde_y = []
    for xi in kde_x:
        val = sum(_math.exp(-0.5 * ((xi - xj) / bw) ** 2) / (_math.sqrt(2 * _math.pi) * bw)
                  for xj in spins)
        kde_y.append(round(val, 4))
    kde_max = max(kde_y) if kde_y else 1
    kde_norm = [round(y / kde_max * max(observed), 2) for y in kde_y]

    # Number colours for chart
    bar_colors = []
    for i in nums:
        if i == 0:             bar_colors.append("rgba(50,200,100,0.85)")
        elif i in RED_NUMBERS: bar_colors.append("rgba(220,20,40,0.85)")
        else:                  bar_colors.append("rgba(160,160,160,0.85)")

    stamp = datetime.now().strftime("%d %b %Y · %H:%M")

    # z-scores for coloring bars
    sigma = _math.sqrt(n * (1/37) * (36/37)) if n > 0 else 1
    z_scores = [round((counts.get(i, 0) - expected) / sigma, 2) for i in nums]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Grand Casino Royale — Visualisation Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&display=swap" rel="stylesheet">
<style>
  :root {{
    --gold:    #d4af37;
    --amber:   #ffbf00;
    --cream:   #fff5c8;
    --felt:    #0a2015;
    --felt2:   #0e2a1a;
    --felt3:   #122e1e;
    --red:     #dc1428;
    --silver:  #b4b4b4;
    --green:   #32c864;
    --bg:      #060e0a;
    --panel:   rgba(10,32,21,0.95);
    --border:  rgba(212,175,55,0.3);
    --glow:    rgba(212,175,55,0.15);
  }}
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: var(--bg);
    color: var(--cream);
    font-family: 'Crimson Pro', Georgia, serif;
    min-height: 100vh;
    overflow-x: hidden;
  }}

  /* ── Felt texture overlay ── */
  body::before {{
    content: '';
    position: fixed; inset: 0; z-index: 0;
    background:
      repeating-linear-gradient(
        45deg,
        transparent,
        transparent 2px,
        rgba(0,40,20,0.08) 2px,
        rgba(0,40,20,0.08) 4px
      ),
      radial-gradient(ellipse at 20% 10%, rgba(18,46,30,0.6) 0%, transparent 60%),
      radial-gradient(ellipse at 80% 90%, rgba(10,32,21,0.8) 0%, transparent 60%);
    pointer-events: none;
  }}

  /* ── Header ── */
  header {{
    position: relative; z-index: 1;
    text-align: center;
    padding: 3rem 2rem 2rem;
    border-bottom: 1px solid var(--border);
    background: linear-gradient(180deg, rgba(6,14,10,1) 0%, rgba(10,32,21,0.5) 100%);
  }}
  header::after {{
    content: '';
    position: absolute; bottom: -1px; left: 10%; right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
  }}

  .crest {{
    font-size: 2rem; letter-spacing: 0.3em;
    color: var(--gold); margin-bottom: 0.5rem;
  }}
  h1 {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(1.8rem, 4vw, 3rem);
    font-weight: 900; font-style: italic;
    background: linear-gradient(135deg, var(--amber) 0%, var(--gold) 40%, #a07820 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
  }}
  .subtitle {{
    font-size: 1rem; letter-spacing: 0.25em;
    color: rgba(212,175,55,0.7);
    text-transform: uppercase;
  }}
  .meta {{
    margin-top: 1.2rem;
    display: flex; gap: 2rem; justify-content: center; flex-wrap: wrap;
  }}
  .meta-pill {{
    background: rgba(212,175,55,0.08);
    border: 1px solid var(--border);
    border-radius: 2rem;
    padding: 0.35rem 1.2rem;
    font-size: 0.9rem;
    color: var(--cream);
  }}
  .meta-pill span {{ color: var(--amber); font-weight: 600; }}

  /* ── Grid ── */
  .grid {{
    position: relative; z-index: 1;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(560px, 1fr));
    gap: 1.5rem;
    padding: 2rem;
    max-width: 1600px;
    margin: 0 auto;
  }}
  .grid-wide {{
    grid-column: 1 / -1;
  }}

  /* ── Panel ── */
  .panel {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.8rem;
    position: relative;
    overflow: hidden;
    box-shadow:
      0 0 0 1px rgba(0,0,0,0.8),
      0 4px 24px rgba(0,0,0,0.6),
      inset 0 1px 0 rgba(212,175,55,0.1);
    transition: box-shadow 0.3s ease;
  }}
  .panel:hover {{
    box-shadow:
      0 0 0 1px rgba(0,0,0,0.8),
      0 8px 40px rgba(0,0,0,0.7),
      0 0 30px var(--glow),
      inset 0 1px 0 rgba(212,175,55,0.15);
  }}
  .panel::before {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
  }}

  .panel-title {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 0.75rem;
    font-weight: 400;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 0.3rem;
  }}
  .panel-heading {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--cream);
    margin-bottom: 1.2rem;
    border-bottom: 1px solid rgba(212,175,55,0.15);
    padding-bottom: 0.8rem;
  }}

  canvas {{
    width: 100% !important;
    max-height: 340px;
  }}

  /* ── Corner ornaments ── */
  .panel::after {{
    content: '✦';
    position: absolute; bottom: 0.6rem; right: 0.8rem;
    color: rgba(212,175,55,0.2);
    font-size: 0.8rem;
  }}

  /* ── Stat row ── */
  .stat-row {{
    display: flex; gap: 1rem; flex-wrap: wrap;
    margin-bottom: 1.2rem;
  }}
  .stat {{
    flex: 1; min-width: 100px;
    background: rgba(212,175,55,0.05);
    border: 1px solid rgba(212,175,55,0.15);
    border-radius: 3px;
    padding: 0.6rem 1rem;
    text-align: center;
  }}
  .stat-val {{
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--amber);
    display: block;
  }}
  .stat-lbl {{
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    color: rgba(255,245,200,0.5);
    text-transform: uppercase;
  }}
  .stat-red  {{ border-color: rgba(220,20,40,0.3); }}
  .stat-red  .stat-val {{ color: #ff4060; }}
  .stat-blk  .stat-val {{ color: var(--silver); }}
  .stat-grn  {{ border-color: rgba(50,200,100,0.3); }}
  .stat-grn  .stat-val {{ color: var(--green); }}

  /* ── Legend ── */
  .legend {{
    display: flex; gap: 1.2rem; flex-wrap: wrap;
    margin-top: 0.8rem;
    font-size: 0.82rem;
  }}
  .legend-item {{ display: flex; align-items: center; gap: 0.4rem; }}
  .legend-dot {{
    width: 10px; height: 10px;
    border-radius: 50%;
    display: inline-block;
  }}

  footer {{
    position: relative; z-index: 1;
    text-align: center;
    padding: 2rem;
    border-top: 1px solid var(--border);
    color: rgba(212,175,55,0.4);
    font-size: 0.8rem;
    letter-spacing: 0.15em;
  }}

  @media (max-width: 700px) {{
    .grid {{ grid-template-columns: 1fr; padding: 1rem; }}
  }}
</style>
</head>
<body>

<header>
  <div class="crest">✦ ✦ ✦</div>
  <h1>Grand Casino Royale</h1>
  <div class="subtitle">Visualisation Dashboard · Monte Carlo Analytics</div>
  <div class="meta">
    <div class="meta-pill">Spins analysed: <span>{n:,}</span></div>
    <div class="meta-pill">Expected / number: <span>{expected:.1f}</span></div>
    <div class="meta-pill">Generated: <span>{stamp}</span></div>
  </div>
</header>

<div class="grid">

  <!-- ══ PANEL 1 — Expected vs Actual ══ -->
  <div class="panel grid-wide">
    <div class="panel-title">Module I</div>
    <div class="panel-heading">Expected vs Actual — All 37 Numbers</div>
    <div class="stat-row">
      <div class="stat stat-red">
        <span class="stat-val">{reds:,}</span>
        <span class="stat-lbl">Red hits</span>
      </div>
      <div class="stat stat-blk">
        <span class="stat-val">{blacks:,}</span>
        <span class="stat-lbl">Black hits</span>
      </div>
      <div class="stat stat-grn">
        <span class="stat-val">{zeros:,}</span>
        <span class="stat-lbl">Zero hits</span>
      </div>
      <div class="stat">
        <span class="stat-val">{expected:.1f}</span>
        <span class="stat-lbl">Expected / №</span>
      </div>
    </div>
    <canvas id="chart-freq" height="200"></canvas>
    <div class="legend">
      <div class="legend-item"><span class="legend-dot" style="background:#dc1428"></span> Rouge</div>
      <div class="legend-item"><span class="legend-dot" style="background:#b4b4b4"></span> Noir</div>
      <div class="legend-item"><span class="legend-dot" style="background:#32c864"></span> Zéro</div>
      <div class="legend-item"><span class="legend-dot" style="background:#d4af37;border-radius:2px"></span> Expected</div>
    </div>
  </div>

  <!-- ══ PANEL 2 — Frequency Curve (KDE) ══ -->
  <div class="panel">
    <div class="panel-title">Module II</div>
    <div class="panel-heading">Frequency Density Curve</div>
    <canvas id="chart-kde"></canvas>
  </div>

  <!-- ══ PANEL 3 — Colour Donut ══ -->
  <div class="panel">
    <div class="panel-title">Module III</div>
    <div class="panel-heading">Colour · Parity · Dozen Split</div>
    <canvas id="chart-donut" height="220"></canvas>
  </div>

  <!-- ══ PANEL 4 — Running Red % ══ -->
  <div class="panel grid-wide">
    <div class="panel-title">Module IV</div>
    <div class="panel-heading">Running Red % — Convergence to Expected (48.65%)</div>
    <canvas id="chart-run" height="160"></canvas>
  </div>

  <!-- ══ PANEL 5 — Streak Distribution ══ -->
  <div class="panel">
    <div class="panel-title">Module V</div>
    <div class="panel-heading">Streak Length Distribution vs Geometric Model</div>
    <canvas id="chart-streak"></canvas>
  </div>

  <!-- ══ PANEL 6 — Z-score deviation ══ -->
  <div class="panel">
    <div class="panel-title">Module VI</div>
    <div class="panel-heading">Deviation Z-Scores (per number)</div>
    <canvas id="chart-zscore"></canvas>
  </div>

</div>

<footer>Grand Casino Royale · Monte Carlo Analytics · {stamp}</footer>

<script>
// ── Shared defaults ──────────────────────────────────────────────────────────
Chart.defaults.color         = 'rgba(255,245,200,0.6)';
Chart.defaults.borderColor   = 'rgba(212,175,55,0.15)';
Chart.defaults.font.family   = "'Crimson Pro', Georgia, serif";
Chart.defaults.font.size     = 13;

const GOLD   = '#d4af37';
const AMBER  = '#ffbf00';
const CREAM  = 'rgba(255,245,200,0.85)';
const DGOLD  = 'rgba(212,175,55,0.18)';

// ── Data from Python ─────────────────────────────────────────────────────────
const nums        = {_json.dumps(nums)};
const observed    = {_json.dumps(observed)};
const expFlat     = {_json.dumps(exp_flat)};
const barColors   = {_json.dumps(bar_colors)};
const runLabels   = {_json.dumps(run_labels)};
const runRed      = {_json.dumps(run_red)};
const runExp      = {_json.dumps(run_exp)};
const streakLabels= {_json.dumps(streak_labels)};
const streakObs   = {_json.dumps(streak_obs)};
const streakGeo   = {_json.dumps(streak_geo)};
const kdeNorm     = {_json.dumps(kde_norm)};
const zScores     = {_json.dumps(z_scores)};
const reds        = {reds};
const blacks      = {blacks};
const zeros       = {zeros};
const dozen1      = {dozen_data[0]};
const dozen2      = {dozen_data[1]};
const dozen3      = {dozen_data[2]};
const dExp        = {dozen_exp[0]};
const pOdd        = {parity_data[0]};
const pEven       = {parity_data[1]};
const pExp        = {parity_exp[0]};

// ── 1. Expected vs Actual bar chart ─────────────────────────────────────────
new Chart(document.getElementById('chart-freq'), {{
  type: 'bar',
  data: {{
    labels: nums.map(n => n === 0 ? '0' : n),
    datasets: [
      {{
        label: 'Observed',
        data: observed,
        backgroundColor: barColors,
        borderColor: barColors.map(c => c.replace('0.85','1')),
        borderWidth: 1,
        borderRadius: 2,
      }},
      {{
        label: 'Expected',
        data: expFlat,
        type: 'line',
        borderColor: GOLD,
        borderWidth: 2.5,
        borderDash: [6,4],
        pointRadius: 0,
        tension: 0,
        fill: false,
        order: 0,
      }}
    ]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: true,
    animation: {{ duration: 1200, easing: 'easeOutQuart' }},
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{
          title: ctx => `Number ${{ctx[0].label}}`,
          afterBody: ctx => {{
            const obs = ctx[0].raw;
            const exp = expFlat[0];
            const diff = obs - exp;
            return `Δ Expected: ${{diff >= 0 ? '+' : ''}}${{diff.toFixed(1)}}`;
          }}
        }},
        backgroundColor: 'rgba(10,32,21,0.95)',
        borderColor: GOLD, borderWidth: 1,
        titleColor: AMBER, bodyColor: CREAM,
      }}
    }},
    scales: {{
      x: {{
        grid: {{ color: 'rgba(212,175,55,0.06)' }},
        ticks: {{ maxRotation: 0, font: {{ size: 10 }} }}
      }},
      y: {{
        grid: {{ color: 'rgba(212,175,55,0.08)' }},
        beginAtZero: true,
      }}
    }}
  }}
}});

// ── 2. KDE Frequency Curve ───────────────────────────────────────────────────
new Chart(document.getElementById('chart-kde'), {{
  type: 'line',
  data: {{
    labels: nums,
    datasets: [
      {{
        label: 'Frequency Density',
        data: kdeNorm,
        borderColor: AMBER,
        borderWidth: 2.5,
        backgroundColor: 'rgba(255,191,0,0.12)',
        fill: true,
        tension: 0.45,
        pointRadius: 3,
        pointBackgroundColor: barColors,
        pointBorderColor: barColors,
      }},
      {{
        label: 'Expected',
        data: expFlat,
        borderColor: GOLD,
        borderWidth: 1.5,
        borderDash: [5,4],
        pointRadius: 0,
        fill: false,
        tension: 0,
      }}
    ]
  }},
  options: {{
    responsive: true,
    animation: {{ duration: 1400, easing: 'easeOutCubic' }},
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        backgroundColor: 'rgba(10,32,21,0.95)',
        borderColor: GOLD, borderWidth: 1,
        titleColor: AMBER, bodyColor: CREAM,
      }}
    }},
    scales: {{
      x: {{ grid: {{ color: 'rgba(212,175,55,0.06)' }} }},
      y: {{ grid: {{ color: 'rgba(212,175,55,0.08)' }}, beginAtZero: true }}
    }}
  }}
}});

// ── 3. Donut — colour + bar insets ──────────────────────────────────────────
new Chart(document.getElementById('chart-donut'), {{
  type: 'bar',
  data: {{
    labels: ['Red', 'Black', 'Zero', '1st Dozen', '2nd Dozen', '3rd Dozen', 'Odd', 'Even'],
    datasets: [
      {{
        label: 'Observed',
        data: [reds, blacks, zeros, dozen1, dozen2, dozen3, pOdd, pEven],
        backgroundColor: [
          'rgba(220,20,40,0.82)', 'rgba(160,160,160,0.82)', 'rgba(50,200,100,0.82)',
          'rgba(212,175,55,0.82)', 'rgba(255,191,0,0.82)', 'rgba(180,100,220,0.82)',
          'rgba(80,200,220,0.82)', 'rgba(0,200,180,0.82)'
        ],
        borderRadius: 3, borderWidth: 1,
      }},
      {{
        label: 'Expected',
        data: [
          Math.round({n}*18/37), Math.round({n}*18/37), Math.round({n}*1/37),
          dExp, dExp, dExp,
          pExp, pExp
        ],
        backgroundColor: 'rgba(212,175,55,0.0)',
        borderColor: GOLD,
        borderWidth: 2,
        type: 'line',
        pointRadius: 5,
        pointStyle: 'crossRot',
        pointBorderColor: GOLD,
        fill: false,
        tension: 0,
      }}
    ]
  }},
  options: {{
    responsive: true,
    animation: {{ duration: 1000 }},
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        backgroundColor: 'rgba(10,32,21,0.95)',
        borderColor: GOLD, borderWidth: 1,
        titleColor: AMBER, bodyColor: CREAM,
      }}
    }},
    scales: {{
      x: {{ grid: {{ color: 'rgba(212,175,55,0.06)' }} }},
      y: {{ grid: {{ color: 'rgba(212,175,55,0.08)' }}, beginAtZero: true }}
    }}
  }}
}});

// ── 4. Running Red % ─────────────────────────────────────────────────────────
new Chart(document.getElementById('chart-run'), {{
  type: 'line',
  data: {{
    labels: runLabels,
    datasets: [
      {{
        label: 'Running Red %',
        data: runRed,
        borderColor: 'rgba(220,20,40,0.9)',
        borderWidth: 2,
        backgroundColor: 'rgba(220,20,40,0.06)',
        fill: true,
        tension: 0.3,
        pointRadius: 0,
      }},
      {{
        label: 'Expected 48.65%',
        data: runExp,
        borderColor: GOLD,
        borderWidth: 1.5,
        borderDash: [6,4],
        pointRadius: 0,
        fill: false,
      }}
    ]
  }},
  options: {{
    responsive: true,
    animation: {{ duration: 1600, easing: 'easeOutSine' }},
    plugins: {{
      legend: {{ labels: {{ color: CREAM, boxWidth: 14 }} }},
      tooltip: {{
        backgroundColor: 'rgba(10,32,21,0.95)',
        borderColor: GOLD, borderWidth: 1,
        titleColor: AMBER, bodyColor: CREAM,
        callbacks: {{ label: ctx => ` ${{ctx.dataset.label}}: ${{ctx.raw}}%` }}
      }}
    }},
    scales: {{
      x: {{
        grid: {{ color: 'rgba(212,175,55,0.06)' }},
        ticks: {{
          maxTicksLimit: 10,
          callback: v => runLabels[v] ? runLabels[v].toLocaleString() : ''
        }}
      }},
      y: {{
        grid: {{ color: 'rgba(212,175,55,0.08)' }},
        min: Math.max(0, Math.min(...runRed) - 3),
        max: Math.min(100, Math.max(...runRed) + 3),
        ticks: {{ callback: v => v + '%' }}
      }}
    }}
  }}
}});

// ── 5. Streak Distribution ───────────────────────────────────────────────────
new Chart(document.getElementById('chart-streak'), {{
  type: 'bar',
  data: {{
    labels: streakLabels.map(l => l + 'x'),
    datasets: [
      {{
        label: 'Observed streaks',
        data: streakObs,
        backgroundColor: 'rgba(180,100,220,0.75)',
        borderColor: 'rgba(180,100,220,1)',
        borderWidth: 1,
        borderRadius: 3,
        order: 1,
      }},
      {{
        label: 'Geometric expectation',
        data: streakGeo,
        type: 'line',
        borderColor: GOLD,
        borderWidth: 2.5,
        borderDash: [5,3],
        backgroundColor: 'rgba(212,175,55,0.07)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: GOLD,
        order: 0,
      }}
    ]
  }},
  options: {{
    responsive: true,
    animation: {{ duration: 1000 }},
    plugins: {{
      legend: {{ labels: {{ color: CREAM, boxWidth: 14 }} }},
      tooltip: {{
        backgroundColor: 'rgba(10,32,21,0.95)',
        borderColor: GOLD, borderWidth: 1,
        titleColor: AMBER, bodyColor: CREAM,
      }}
    }},
    scales: {{
      x: {{ grid: {{ color: 'rgba(212,175,55,0.06)' }} }},
      y: {{ grid: {{ color: 'rgba(212,175,55,0.08)' }}, beginAtZero: true }}
    }}
  }}
}});

// ── 6. Z-score bars ──────────────────────────────────────────────────────────
const zColors = zScores.map(z => {{
  if (z > 2.58)  return 'rgba(255,80,80,0.85)';
  if (z > 1.5)   return 'rgba(255,180,0,0.85)';
  if (z < -2.58) return 'rgba(80,180,255,0.85)';
  if (z < -1.5)  return 'rgba(80,220,220,0.7)';
  return 'rgba(50,200,100,0.6)';
}});

new Chart(document.getElementById('chart-zscore'), {{
  type: 'bar',
  data: {{
    labels: nums.map(n => n === 0 ? '0' : n),
    datasets: [
      {{
        label: 'Z-score',
        data: zScores,
        backgroundColor: zColors,
        borderColor: zColors.map(c => c.slice(0, -2) + '1)'),
        borderWidth: 1,
        borderRadius: 2,
      }},
      {{
        label: '+2.58σ (99%)',
        data: Array(37).fill(2.58),
        type: 'line',
        borderColor: 'rgba(255,80,80,0.5)',
        borderWidth: 1,
        borderDash: [4,3],
        pointRadius: 0,
        fill: false,
      }},
      {{
        label: '−2.58σ (99%)',
        data: Array(37).fill(-2.58),
        type: 'line',
        borderColor: 'rgba(80,180,255,0.5)',
        borderWidth: 1,
        borderDash: [4,3],
        pointRadius: 0,
        fill: false,
      }}
    ]
  }},
  options: {{
    responsive: true,
    animation: {{ duration: 900 }},
    plugins: {{
      legend: {{ labels: {{ color: CREAM, boxWidth: 14, filter: i => i.text !== 'Z-score' }} }},
      tooltip: {{
        backgroundColor: 'rgba(10,32,21,0.95)',
        borderColor: GOLD, borderWidth: 1,
        titleColor: AMBER, bodyColor: CREAM,
        callbacks: {{
          title: ctx => `Number ${{ctx[0].label}}`,
          label: ctx => ` Z = ${{ctx.raw > 0 ? '+' : ''}}${{ctx.raw}}`
        }}
      }}
    }},
    scales: {{
      x: {{ grid: {{ color: 'rgba(212,175,55,0.06)' }}, ticks: {{ font: {{ size: 10 }} }} }},
      y: {{
        grid: {{ color: 'rgba(212,175,55,0.08)' }},
        ticks: {{ callback: v => (v > 0 ? '+' : '') + v + 'σ' }}
      }}
    }}
  }}
}});
</script>
</body>
</html>"""

    if output_path is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"casino_viz_{stamp}.html"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Also write the live interactive dashboard alongside
    live_path = output_path.replace("casino_viz_", "casino_live_")
    _write_live_dashboard(live_path)

    return output_path, live_path
# =============================================================================
#  MENUS
# =============================================================================

def tracker_menu(tracker, n_spins):
    while True:
        clear(); print_header()
        print(center(f"{CREAM}{ITALIC}Session: {len(tracker.spins):,} spins logged{RESET}"))
        print()
        hr("-",color=AMBER)
        print(f"\n  {GOLD}Session Reports:{RESET}\n")
        opts = {
            "1": ("Frequency Table (classic)",                    CREAM),
            "2": ("Croupier Summary",                             CREAM),
            "3": (f"[Tracker]  Streak Report",                    PURPLE),
            "4": (f"[Tracker]  Frequency Deep-Dive",              PURPLE),
            "5": (f"[Tracker]  Distribution Over Time",           PURPLE),
            "6": (f"[Tracker]  All three tracker reports",        PURPLE),
            "7": (f"[Pattern]  Pattern Detection Engine",         ORANGE),
            "8": (f"[Pattern]  Full Analysis (all reports)",      ORANGE),
            "v": (f"[Visual]   Generate HTML Dashboard  <-- NEW", TEAL),
            "9": (f"Export raw data  ->  CSV + JSON",             CYAN),
            "b": ("Back to main table",                           CREAM),
        }
        for k,(v,col) in opts.items():
            print(f"  {AMBER}[{k}]{RESET}  {col}{v}{RESET}")
        print()
        hr("-",color=SILVER)
        choice = input(f"\n  {GOLD}Your choice >{RESET} ").strip().lower()
        if choice=="b": break

        clear(); print_header()

        if   choice=="1": print(build_frequency_table(tracker.spins)); pause()
        elif choice=="2": print(build_summary(tracker.spins)); pause()
        elif choice=="3": print_streak_report(tracker); pause()
        elif choice=="4": print_frequency_report(tracker); pause()
        elif choice=="5":
            segs=10 if n_spins>=1000 else 5
            print_distribution_report(tracker,segments=segs); pause()
        elif choice=="6":
            print_streak_report(tracker)
            print_frequency_report(tracker)
            print_distribution_report(tracker,segments=(10 if n_spins>=1000 else 5))
            pause()
        elif choice=="7": print_pattern_detection(tracker); pause()
        elif choice=="8":
            print_streak_report(tracker)
            print_frequency_report(tracker)
            print_distribution_report(tracker,segments=(10 if n_spins>=1000 else 5))
            print_pattern_detection(tracker)
            pause()
        elif choice=="v":
            print(f"\n  {TEAL}Generating visualization dashboards ...{RESET}\n")
            stamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_p = f"casino_viz_{stamp}.html"
            result = generate_visualization_html(tracker, output_path=html_p)
            static_path, live_path = result if isinstance(result, tuple) else (result, None)
            print(f"  {LTGREEN}OK  Static snapshot  ->  {AMBER}{static_path}{RESET}")
            if live_path:
                print(f"  {LTGREEN}OK  Live dashboard   ->  {AMBER}{live_path}{RESET}")
            print(f"\n  {CREAM}The LIVE dashboard has an interactive spinning wheel.")
            print(f"  Each spin updates all 6 charts in real time.{RESET}\n")
            # Try to open live dashboard first, fall back to static
            open_path = live_path if live_path and os.path.exists(live_path) else static_path
            try:
                import subprocess, platform
                abs_path = os.path.abspath(open_path)
                sys_name = platform.system()
                if sys_name == "Darwin":
                    subprocess.Popen(["open", abs_path])
                elif sys_name == "Windows":
                    os.startfile(abs_path)
                else:
                    subprocess.Popen(["xdg-open", abs_path])
                print(f"  {LTGREEN}OK  Opening in your browser ...{RESET}\n")
            except Exception:
                print(f"  {AMBER}Open manually: file://{os.path.abspath(open_path)}{RESET}\n")
            pause()
        elif choice=="9":
            stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_p=f"casino_spins_{stamp}.csv"; json_p=f"casino_spins_{stamp}.json"
            tracker.export_csv(csv_p); tracker.export_json(json_p)
            print(f"\n  {LTGREEN}OK  CSV  saved ->  {AMBER}{csv_p}{RESET}")
            print(f"  {LTGREEN}OK  JSON saved ->  {AMBER}{json_p}{RESET}\n")
            pause()
        else:
            print(f"\n  {RED}Invalid selection.{RESET}\n"); time.sleep(1)


def menu():
    options = {
        "1": ("Single animated spin",           1,         True),
        "2": ("Quick run",                       1_000,     False),
        "3": ("Standard run",                    10_000,    False),
        "4": ("Grand run",                       100_000,   False),
        "5": ("High Roller -- one million",      1_000_000, False),
    }
    print_header()
    print(f"  {GOLD}Choose your table:{RESET}\n")
    for key,(label,n,_) in options.items():
        spins=f"  {DIM}({n:,} spins){RESET}" if n>1 else ""
        print(f"  {AMBER}[{key}]{RESET}  {CREAM}{label:<38}{RESET}{spins}")
    print(f"\n  {AMBER}[q]{RESET}  {CREAM}Quit{RESET}\n")
    hr("-",color=SILVER)
    choice=input(f"\n  {GOLD}Your choice >{RESET} ").strip().lower()
    if choice=="q":
        print(f"\n  {GOLD}The house always wins. Bonne nuit.{RESET}\n"); sys.exit(0)
    if choice not in options:
        print(f"\n  {RED}Invalid. Try again.{RESET}\n"); time.sleep(1.2); return
    label,n_spins,animated=options[choice]
    clear(); print_header()
    tracker=OutcomeTracker()
    if animated:
        result=spin_wheel(); tracker.record(result)
        print(f"  {CREAM}Le croupier lache la bille ...{RESET}")
        spinning_animation(result)
        cw="ZERO" if result==0 else ("ROUGE" if result in RED_NUMBERS else "NOIR")
        print(center(f"{GOLD}{BOLD}+  Numero {num_color(result)}{result}{GOLD} -- {cw}  +{RESET}"))
        print(); hr("-",color=SILVER)
        input(f"\n  {AMBER}Press ENTER ...{RESET}  ")
    else:
        print(f"  {CREAM}Running {n_spins:,} spins ...{RESET}\n")
        t0=time.perf_counter(); results=run_simulation(n_spins); elapsed=time.perf_counter()-t0
        print(f"  {DIM}Done in {elapsed*1000:.1f} ms  ({n_spins/elapsed:,.0f} spins/sec){RESET}\n")
        tracker.record_batch(results); tracker.flush_streaks()
        tracker_menu(tracker,n_spins)


def main():
    try:
        while True: clear(); menu()
    except KeyboardInterrupt:
        print(f"\n\n  {GOLD}La maison gagne toujours. Bonne nuit.{RESET}\n"); sys.exit(0)

if __name__=="__main__":
    main()
