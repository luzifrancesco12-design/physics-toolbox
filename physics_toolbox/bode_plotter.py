import numpy as np
from .base_plotter import BasePlotter

class BodePlotter(BasePlotter):
    """
    Classe specializzata per la generazione di diagrammi di Bode (Modulo e Fase).
    """
    def __init__(self, figsize=(8, 6)):
        super().__init__(figsize=figsize, nrows=1, ncols=2, sharex=True)
        self.ax_mag = self.axes[0]
        self.ax_phase = self.axes[1]

        # Configurazione standard per analisi in frequenza
        self.add_grid(ax_idx=0, xscale ="log", yscale="linear")
        self.add_grid(ax_idx=1, xscale ="log", yscale="linear")

        self.set_labels(xlabel=r"$\omega\text{ [rad/s]}$", ylabel=r"$|H(j\omega)|\text{ [dB]}$", ax_idx=0)
        self.set_labels(xlabel=r"$\omega\text{ [rad/s]}$", ylabel=r"$\arg(H)\text{ [deg]}$", ax_idx=1)

    def plot_bode(self, freq, magnitude, phase_deg, freq_err=None, magnitude_err=None, phase_err_deg=None,
                is_db=True, label_mag=None, label_phase=None,
                marker='o', markersize=3,
                capsize=3, elinewidth=1.2):
        """
        Traccia modulo e fase con supporto opzionale a barre di errore.ª
        
        Parametri:
        - freq: array delle frequenze (o pulsazioni)
        - magnitude: array del modulo (in dB se is_db=True, in unità lineari se is_db=False)
        - phase_deg: array della fase in gradi
        - is_db: booleano, indica se il modulo è già in scala decibel
        """
        # Conversione automatica in dB se i dati in input sono lineari
        mag_plot = magnitude if is_db else 20.0 * np.log10(np.abs(magnitude))
        mag_plot_err = magnitude_err if is_db else 20.0 * np.log10(np.abs(magnitude_err))
        
        self.ax_mag.errorbar(
            freq, mag_plot, xerr=freq_err, yerr=mag_plot_err, label=label_mag, marker=marker,
            markersize=markersize, linewidth=1.5, elinewidth=elinewidth, capsize=capsize
        )
        self.ax_phase.errorbar(
            freq, phase_deg, xerr=freq_err, yerr=phase_err_deg, label=label_phase, marker=marker,
            markersize=markersize, linewidth=1.5, elinewidth=elinewidth, capsize=capsize
        )

        # Riunisce le etichette dei due pannelli in una sola legenda sul grafico superiore.
        handles, labels = [], []
        for ax in (self.ax_mag, self.ax_phase):
            ax_handles, ax_labels = ax.get_legend_handles_labels()
            for handle, label in zip(ax_handles, ax_labels):
                if label and label not in labels:
                    handles.append(handle)
                    labels.append(label)

        if handles:
            if self.ax_mag.get_legend() is not None:
                self.ax_mag.get_legend().remove()
            if self.ax_phase.get_legend() is not None:
                self.ax_phase.get_legend().remove()
            self.ax_mag.legend(handles, labels, loc='best', frameon=True)

        return self.ax_mag, self.ax_phase
