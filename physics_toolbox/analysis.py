"""
Strumenti di analisi dati per il laboratorio: caricamento tabelle, fit, medie pesate,
propagazione degli errori, formattazione e grafici.
"""
import os
import zipfile

import numpy as np
import pandas as pd
from scipy.linalg import block_diag
from scipy.optimize import brentq, curve_fit
from scipy.stats import chi2 as chi2_dist

from .base_plotter import BasePlotter
from .sheet_connector import SheetConnector

__all__ = ["Tabelle", "col", "pulisci", "tra", "media_pesata", "propaga", "fit",
        "banda_fit", "x_da_y", "fmt", "grafico_fit", "salva", "scarica_figure"]


# ------------------------------- dati -----------------------------------------
class Tabelle:
    """
    Carica (una sola volta per sessione) le tabelle descritte in 'definizioni'.

        carica = Tabelle(URL, {"bode": dict(foglio="Incertezze", colonne=("A", "I"), riga_intestazioni=8)})
        df = carica("bode")                       # carica("bode", ricarica=True) per riscaricare
    """
    def __init__(self, url, definizioni):
        self.url, self.definizioni = url, definizioni
        self._conn, self._cache = SheetConnector(), {}

    def __call__(self, nome, ricarica=False):
        if "docs.google.com" not in self.url:
            raise ValueError("URL del foglio non valido: imposta URL_FOGLIO nella configurazione.")
        if nome not in self.definizioni:
            raise KeyError(f"Tabella {nome!r} non definita. Disponibili: {list(self.definizioni)}")
        if ricarica or nome not in self._cache:
            t = self.definizioni[nome]
            self._cache[nome] = self._conn.get_table_block(
                self.url, t["colonne"][0], t["colonne"][1],
                header_row_idx=t["riga_intestazioni"],
                worksheet_identifier=t["foglio"],
                end_row=t.get("righe_max", 100))
        return self._cache[nome]


def col(df, nome):
    """Colonna come array float (celle vuote o testo -> NaN)."""
    if nome not in df.columns:
        raise KeyError(f"Colonna {nome!r} non trovata. Colonne: {list(df.columns)}")
    return pd.to_numeric(df[nome], errors="coerce").to_numpy(dtype=float)


def pulisci(*arrays, ordina_per=0):
    """Scarta le righe con NaN in almeno un array e ordina per l'array 'ordina_per' (None = no)."""
    A = np.column_stack(arrays)
    A = A[np.isfinite(A).all(axis=1)]
    if ordina_per is not None:
        A = A[np.argsort(A[:, ordina_per], kind="stable")]
    return [A[:, i] for i in range(A.shape[1])]


def tra(x, lo, hi):
    """Maschera booleana lo <= x <= hi."""
    return (x >= lo) & (x <= hi)


# ------------------------------ statistica ------------------------------------
def media_pesata(x, s):
    """Media pesata con pesi 1/s^2. Ritorna (media, incertezza, chi2 ridotto)."""
    x, s = np.asarray(x, float), np.asarray(s, float)
    w = 1 / s ** 2
    m = np.sum(w * x) / np.sum(w)
    chi2r = np.sum(((x - m) / s) ** 2) / (len(x) - 1) if len(x) > 1 else np.nan
    return m, 1 / np.sqrt(np.sum(w)), chi2r


def propaga(func, p, err=None, cov=None):
    """
    Propagazione numerica degli errori per una funzione arbitraria func(p) -> float.
    p: valori; err: incertezze indipendenti, oppure cov: matrice di covarianza completa.
    Ritorna (valore, incertezza).
    """
    p = np.asarray(p, float)
    cov = np.diag(np.asarray(err, float) ** 2) if cov is None else np.asarray(cov, float)
    grad = np.zeros_like(p)
    for i in range(len(p)):
        h = 1e-4 * np.sqrt(cov[i, i]) if cov[i, i] > 0 else 1e-8 * max(abs(p[i]), 1.0)
        dp = np.zeros_like(p)
        dp[i] = h
        grad[i] = (func(p + dp) - func(p - dp)) / (2 * h)
    return func(p), float(np.sqrt(grad @ cov @ grad))


def fit(modello, x, y, sy=None, p0=None, nomi=None, **kw):
    """
    Fit di modello(x, *params). Con sy il fit è pesato (absolute_sigma=True).
    Stampa i parametri e ritorna un dict: modello, popt, perr, pcov, n, dof (+ chi2, p_value se sy).
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    sy = None if sy is None else np.asarray(sy, float)
    popt, pcov = curve_fit(modello, x, y, p0=p0, sigma=sy, absolute_sigma=sy is not None, **kw)
    perr = np.sqrt(np.diag(pcov))
    res = dict(modello=modello, popt=popt, perr=perr, pcov=pcov, n=len(x), dof=len(x) - len(popt))
    for n_, v, s in zip(nomi or [f"p{i}" for i in range(len(popt))], popt, perr):
        print(f"  {n_} = {fmt(v, s)}")
    if sy is not None and res["dof"] > 0:
        res["chi2"] = float(np.sum(((y - modello(x, *popt)) / sy) ** 2))
        res["p_value"] = float(chi2_dist.sf(res["chi2"], res["dof"]))
        print(f"  chi2/dof = {res['chi2']:.2f}/{res['dof']} = {res['chi2'] / res['dof']:.2f},  p-value = {res['p_value']:.3f}")
    return res


def banda_fit(res, xs):
    """Incertezza a 1 sigma della curva fittata nei punti xs (covarianza completa)."""
    popt, f = res["popt"], res["modello"]
    J = np.zeros((len(xs), len(popt)))
    for i in range(len(popt)):
        h = 1e-4 * res["perr"][i] if res["perr"][i] > 0 else 1e-8
        dp = np.zeros_like(popt)
        dp[i] = h
        J[:, i] = (f(xs, *(popt + dp)) - f(xs, *(popt - dp))) / (2 * h)
    return np.sqrt(np.einsum("ij,jk,ik->i", J, res["pcov"], J))


def x_da_y(res, y0, sy0=0.0, lo=None, hi=None):
    """
    Valore x in [lo, hi] in cui il modello fittato vale y0 (modello monotono nell'intervallo).
    L'incertezza include la covarianza dei parametri e l'incertezza sy0 su y0. Ritorna (x0, sigma_x0).
    """
    f = res["modello"]

    def radice(q):                      # q = [parametri..., y0]
        return brentq(lambda x: f(x, *q[:-1]) - q[-1], lo, hi)

    try:
        return propaga(radice, np.append(res["popt"], y0), cov=block_diag(res["pcov"], [[sy0 ** 2]]))
    except ValueError:
        raise ValueError(f"Il modello non raggiunge y={y0:g} in [{lo:g}, {hi:g}]: allarga l'intervallo.")


# ------------------------------ formattazione ---------------------------------
def fmt(v, s, unita="", latex=False):
    """
    Valore ± errore con 2 cifre significative sull'errore (notazione scientifica se |esponente| >= 4).
    latex=True ritorna una stringa mathtext per le legende, es. $(1.23 \\pm 0.04)\\ \\mathrm{kHz}$.
    """
    if not (np.isfinite(s) and s > 0):
        return f"{v:.4g} {unita}".strip()
    e = int(np.floor(np.log10(abs(v)))) if v != 0 else 0
    if abs(e) < 4:
        e = 0
    v2, s2 = v / 10 ** e, s / 10 ** e
    dec = max(0, 1 - int(np.floor(np.log10(s2))))
    pm = r" \pm " if latex else " ± "
    txt = f"{v2:.{dec}f}{pm}{s2:.{dec}f}"
    if e:
        txt = f"({txt})" + (rf"\times 10^{{{e}}}" if latex else f"e{e:+d}")
    if unita:
        txt += rf"\ \mathrm{{{unita}}}" if latex else f" {unita}"
    return f"${txt}$" if latex else txt


# -------------------------------- grafici -------------------------------------
def grafico_fit(x, y, sy, res, xlabel="x", ylabel="y", xscale="linear", yscale="linear",
                residui=True, label="Dati", x_range=None, figsize=(9, 6)):
    """
    Dati con barre d'errore + curva fittata + banda 1 sigma (+ pannello dei residui normalizzati).
    Ritorna il BasePlotter: si può completare (add_hline, add_vline, ...), poi salva(g, ...) e g.show().
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    g = BasePlotter(figsize=figsize if residui else (9, 5), nrows=2 if residui else 1, ncols=1, sharex=residui)
    g.add_grid(0, xscale, yscale)
    g.set_labels("" if residui else xlabel, ylabel, 0)
    g.plot_error(x, y, yerr=sy, ax_idx=0, label=label, linestyle="none")

    lo, hi = x_range if x_range else (x.min(), x.max())
    xs = np.geomspace(lo, hi, 300) if xscale == "log" else np.linspace(lo, hi, 300)
    ys = res["modello"](xs, *res["popt"])
    linea = g.plot(xs, ys, ax_idx=0, label="Fit", linestyle="-", marker="")[0]
    b = banda_fit(res, xs)
    g.axes[0].fill_between(xs, ys - b, ys + b, color=linea.get_color(), alpha=0.25,
                        label=r"Incertezza fit ($1\sigma$)")
    g.add_legend(0)

    if residui:
        r = y - res["modello"](x, *res["popt"])
        if sy is not None:
            r = r / np.asarray(sy, float)
        g.plot_error(x, r, yerr=None if sy is None else np.ones_like(r), ax_idx=1, linestyle="none")
        g.add_hline(0, ax_idx=1, color="gray", linestyle="-")
        g.add_grid(1, xscale, "linear")
        g.set_labels(xlabel, "residui" + (r" [$\sigma$]" if sy is not None else ""), 1)
    return g


# ------------------------------- export ---------------------------------------
FIGURE = []   # grafici salvati con salva(), usati da scarica_figure()


def salva(plotter, nome):
    """Salva il grafico su file e lo registra per lo zip finale."""
    plotter.save(nome)
    FIGURE.append(nome)


def scarica_figure(nome_zip="grafici.zip"):
    """Zip di tutti i grafici salvati con salva(); in Colab avvia il download."""
    with zipfile.ZipFile(nome_zip, "w") as z:
        for f in dict.fromkeys(FIGURE):
            if os.path.exists(f):
                z.write(f)
                print(f"Aggiunto: {f}")
    try:
        from google.colab import files
        files.download(nome_zip)
    except ImportError:
        print(f"Fuori da Colab: archivio in {os.path.abspath(nome_zip)}")