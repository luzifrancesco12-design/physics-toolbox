import shutil
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# Usa LaTeX solo se è installato, altrimenti ripiega sul mathtext di matplotlib
HAS_LATEX = shutil.which("latex") is not None

plt.rcParams.update({
    "text.usetex": HAS_LATEX,
    "text.latex.preamble": r"\usepackage{amsmath}" if HAS_LATEX else "",
    "font.family": "serif",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.dpi": 100,
    "savefig.dpi": 300
})

class BasePlotter:
    """
    Classe base per la generazione di grafici bidimensionali versatili.
    """
    def __init__(self, figsize=(8, 5), nrows=1, ncols=1, sharex=False, sharey=False):
        self.fig, self.ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, sharex=sharex, sharey=sharey)
        self.axes = np.atleast_1d(self.ax)
        
        #Per il funzionamento sopra: fissando nrows=2 ncols=1 si creano due subplots impilati verticalmente, 
        #che vengono linearizzati in un unico array 1D (23). Per accedere ai rispettivi subplot basterà usare
        #l'indice 0, 1, etc. Nel seguito ax_idx (di default settato a 0) è proprio questo indice. 

    def plot(self, x, y, ax_idx=0, label=None, linestyle=None, marker='o', color=None, markersize=3, linewidth=1.5):
        """Traccia uno scatter plot (oppure una curva) sull'asse specificato."""
        ax = self.axes[ax_idx]
        return ax.plot(x, y, label=label, linestyle=linestyle, marker=marker, color=color, linewidth=linewidth)
    
    def plot_error(self, x, y, xerr=None, yerr=None, ax_idx=0, label=None, linestyle=None, marker='o', color=None, markersize=3, linewidth=1.5, elinewidth=1.0):
        """Traccia uno scatter plot con barre d'errore sull'asse specificato """
        ax=self.axes[ax_idx]
        return ax.errorbar(x, y, xerr=xerr, yerr=yerr, label=label, linestyle=linestyle, marker=marker, color=color, markersize=markersize, linewidth=linewidth, elinewidth=elinewidth)

    def set_labels(self, xlabel, ylabel, ax_idx=0):
        """Imposta le etichette degli assi con supporto LaTeX."""
        ax = self.axes[ax_idx]
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    def set_title(self, title, ax_idx=0):
        """Imposta il titolo del grafico."""
        ax = self.axes[ax_idx]
        ax.set_title(title)

    def add_grid(self, ax_idx=0, xscale="linear", yscale="linear", alpha=0.5):
        """Abilita la griglia (densa) principale e secondaria a seconda del modello scelto."""
        ax = self.axes[ax_idx]
        # --- Gestione scala e asse X ---
        ax.set_xscale(xscale)
        if xscale=="log": 
            ax.xaxis.set_minor_locator(
                ticker.LogLocator(base=10.0, subs=np.arange(2, 10), numticks=100)
            )
        else: 
            ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
        # --- Gestione scala e asse Y ---
        ax.set_yscale(yscale)
        if yscale=="log":
            ax.yaxis.set_minor_locator(
                            ticker.LogLocator(base=10.0, subs=np.arange(2, 10), numticks=100)
                        )
        else: 
            ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
        # --- CONFIGURAZIONE UNIFICATA DELLE GRIGLIE ---
        ax.grid(which="major", linestyle="-", linewidth=0.8, color="gray", alpha=alpha)
        ax.grid(which="minor", linestyle=":", linewidth=0.4, color="lightgray", alpha=alpha)

    def add_hline(self, y, ax_idx=0, color='r', linestyle='--', label=None, linewidth=1):
        """Aggiunge una linea orizzontale di riferimento (es. soglie o asintoti)."""
        ax = self.axes[ax_idx]
        return ax.axhline(y=y, color=color, linestyle=linestyle, label=label, linewidth=linewidth)

    def add_vline(self, x, ax_idx=0, color='g', linestyle='--', label=None, linewidth=1):
        """Aggiunge una linea verticale di riferimento (es. frequenze di taglio)."""
        ax = self.axes[ax_idx]
        return ax.axvline(x=x, color=color, linestyle=linestyle, label=label, linewidth=linewidth)

    def add_legend(self, ax_idx=0, loc='best'):
        """Aggiunge la legenda con bordo."""
        ax = self.axes[ax_idx]
        ax.legend(loc=loc, frameon=True)

    def save(self, filepath, dpi=300):
        """Salva la figura su file in formato vettoriale (PDF) o raster (PNG)."""
        self.fig.savefig(filepath, dpi=dpi, bbox_inches='tight')

    def show(self):
        """Mostra il grafico formattato."""
        plt.tight_layout()
        plt.show()