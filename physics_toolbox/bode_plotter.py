import numpy as np
from .base_plotter import BasePlotter

class BodePlotter(BasePlotter):
    """
    Diagramma di Bode. Di default mostra solo il modulo;
    la fase compare solo con show_phase=True (pannelli impilati).
    """
    def __init__(self, figsize=None, show_phase=False):
        self.show_phase = show_phase
        if figsize is None:
            figsize = (8, 7) if show_phase else (8, 5)

        super().__init__(figsize=figsize,
                        nrows=2 if show_phase else 1,
                        ncols=1,
                        sharex=show_phase)

        self.ax_mag = self.axes[0]
        self.ax_phase = self.axes[1] if show_phase else None

        self.add_grid(ax_idx=0, xscale="log", yscale="linear", alpha=0.7)
        self.set_labels(xlabel=r"$f \mathrm{[Hz]}$",
                        ylabel=r"$|H(j\omega)|\ \mathrm{[dB]}$", ax_idx=0)

        if show_phase:
            self.add_grid(ax_idx=1, xscale="log", yscale="linear", alpha=0.7)
            self.set_labels(xlabel=r"$f \mathrm{[Hz]}$",
                            ylabel=r"$\arg(H)\ \mathrm{[deg]}$", ax_idx=1)
            self.ax_mag.set_xlabel("")  # l'etichetta x resta solo sul pannello in basso

    def plot_bode(self, freq, magnitude, phase_deg=None, freq_err=None,
                magnitude_err=None, phase_err_deg=None, is_db=True, is_db_err=False,
                label_mag=None, label_phase=None,
                marker='o', linestyle='none', markersize=3, capsize=3, elinewidth=1.2):
        magnitude = np.asarray(magnitude, dtype=float)

        if is_db:
            mag_plot= magnitude
        else:
            mag_plot = 20.0 * np.log10(np.abs(magnitude))
            
        lin = 10**(magnitude/20) if is_db else np.abs(magnitude) 
            
        if is_db_err:
            mag_err=magnitude_err
        else: 
            # propagazione dell'errore: d(20 log10 x) = 20/ln(10) * dx/x
            mag_err = None if magnitude_err is None else \
                (20.0 / np.log(10)) * np.asarray(magnitude_err) / lin

        self.ax_mag.errorbar(freq, mag_plot, xerr=freq_err, yerr=mag_err,
                            label=label_mag, marker=marker, linestyle=linestyle, 
                            color='royalblue',markersize=markersize,
                            elinewidth=elinewidth, capsize=capsize)

        if self.show_phase and phase_deg is not None:
            self.ax_phase.errorbar(freq, phase_deg, xerr=freq_err, yerr=phase_err_deg,
                                label=label_phase, marker=marker, linestyle=linestyle, 
                                color='firebrick', markersize=markersize,
                                elinewidth=elinewidth, capsize=capsize)

        # Una legenda per pannello
        if label_mag is not None:
            self.ax_mag.legend(loc='best', frameon=True)
        if self.show_phase and label_phase is not None:
            self.ax_phase.legend(loc='best', frameon=True)

        return self.ax_mag, self.ax_phase