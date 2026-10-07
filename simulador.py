import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from Airplanes import *
from functions_aircrafts import simulate_cdo, result_on_given_distance

KT = 0.514444      # 1 kt in m/s
NM = 1852          # 1 NM in m
ft = 0.3048        # 1 ft in m

airplanes = {"B767": B767, "B777": B777, "B737": B737, "A320": A320, "A319": A319}

# Distance from every STAR (first waypoint -> IAF), in NM.
# We will complete it with the STAR charts from the AIP of ENAIRE
distance_from_star = {"ALBER1Z": 50, "PUMAL1Z": 50, "MARTA3Z": 50,
                      "MATEX3Z": 50, "LOBAR2W": 50, "CASPE2W": 50}

class SimulatorApp:
    def __init__(self, root):
        self.root = root
        root.title("CDO Simulator")
        self.flights = []          # every flight added: label, star, distance, table, results

        # ---------------- Left panel: inputs ----------------
        panel = ttk.LabelFrame(root, text="New flight", padding=10)
        panel.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        ttk.Label(panel, text="Airplane").grid(row=0, column=0, sticky="w")
        self.var_airplane = tk.StringVar(value=list(airplanes)[0])
        ttk.Combobox(panel, textvariable=self.var_airplane, values=list(airplanes),
                     state="readonly", width=15).grid(row=0, column=1, pady=3)

        ttk.Label(panel, text="Weight (% MLW)").grid(row=1, column=0, sticky="w")
        self.var_weight = tk.StringVar(value="100")
        ttk.Entry(panel, textvariable=self.var_weight, width=17).grid(row=1, column=1, pady=3)

        ttk.Label(panel, text="STAR").grid(row=2, column=0, sticky="w")
        self.var_star = tk.StringVar(value=list(distance_from_star)[0])
        cb_star = ttk.Combobox(panel, textvariable=self.var_star,
                               values=list(distance_from_star) + ["OTHER"],
                               state="readonly", width=15)
        cb_star.grid(row=2, column=1, pady=3)
        cb_star.bind("<<ComboboxSelected>>", self.on_star_selected)

        ttk.Label(panel, text="Distance WP-IAF (NM)").grid(row=3, column=0, sticky="w")
        self.var_distance = tk.StringVar(value=str(distance_from_star[self.var_star.get()]))
        ttk.Entry(panel, textvariable=self.var_distance, width=17).grid(row=3, column=1, pady=3)

        ttk.Button(panel, text="Add flight", command=self.add_flight).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(10, 3))
        ttk.Button(panel, text="Add all (5 aircraft, 100% and 80%)", command=self.add_all).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=3)
        ttk.Button(panel, text="Remove last", command=self.remove_last).grid(
            row=6, column=0, columnspan=2, sticky="ew", pady=3)
        ttk.Button(panel, text="Clear all", command=self.clear_all).grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=3)

        ttk.Label(panel, text="Results").grid(row=8, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.txt_results = tk.Text(panel, width=38, height=14, state="disabled")
        self.txt_results.grid(row=9, column=0, columnspan=2)

        # ---------------- Right panel: plots ----------------
        self.fig = Figure(figsize=(10, 7))
        self.ax_h = self.fig.add_subplot(2, 1, 1)
        self.ax_v = self.fig.add_subplot(2, 1, 2, sharex=self.ax_h)
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew")
        NavigationToolbar2Tk(self.canvas, root, pack_toolbar=False).grid(row=1, column=1, sticky="ew")
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        self.redraw()

    # ---------------- Actions ----------------
    def on_star_selected(self, event=None):
        """When a STAR is chosen, we fill its distance (editable if OTHER)."""
        star = self.var_star.get()
        if star in distance_from_star:
            self.var_distance.set(str(distance_from_star[star]))

    def simulate(self, airplane, pct):
        table = simulate_cdo(airplane, pct * airplane.max_landing_weight)
        label = f"{airplane.name} [{round(pct * 100)}% MLW]"
        return table, label

    def add_flight(self):
        # 1) Read and validate the inputs
        try:
            pct = float(self.var_weight.get().replace(",", ".")) / 100
            dist_nm = float(self.var_distance.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Weight and distance must be numbers.")
            return
        if not 0.5 <= pct <= 1.0:
            messagebox.showerror("Error", "Weight must be between 50 and 100 % MLW.")
            return
        if not 1 <= dist_nm <= 300:
            messagebox.showerror("Error", "Distance must be between 1 and 300 NM.")
            return

        # 2) Simulate and read the table at the given distance
        airplane = airplanes[self.var_airplane.get()]
        table, label = self.simulate(airplane, pct)
        altitude, t = result_on_given_distance(table, dist_nm * NM)

        self.flights.append({"label": label, "star": self.var_star.get(),
                             "dist_nm": dist_nm, "table": table,
                             "altitude": altitude, "t": t})
        self.refresh_results()
        self.redraw()

    def add_all(self):
        """Reproduces the reference figure: every aircraft at 100% and 80% MLW."""
        for airplane in airplanes.values():
            for pct in (1.0, 0.8):
                table, label = self.simulate(airplane, pct)
                self.flights.append({"label": label, "star": None, "dist_nm": None,
                                     "table": table, "altitude": None, "t": None})
        self.refresh_results()
        self.redraw()

    def remove_last(self):
        if self.flights:
            self.flights.pop()
            self.refresh_results()
            self.redraw()

    def clear_all(self):
        self.flights.clear()
        self.refresh_results()
        self.redraw()

    # ---------------- Output ----------------
    def refresh_results(self):
        self.txt_results.config(state="normal")
        self.txt_results.delete("1.0", "end")
        for f in self.flights:
            if f["dist_nm"] is None:
                continue
            self.txt_results.insert("end", f"{f['label']} - {f['star']}\n")
            if f["altitude"] is None:
                self.txt_results.insert("end", "   Distance out of the table\n")
            else:
                self.txt_results.insert(
                    "end", f"   Altitude at WP: {f['altitude'] / ft:.0f} ft ({f['altitude']:.0f} m)\n"
                           f"   Time WP -> IAF: {f['t'] / 60:.1f} min\n")
        self.txt_results.config(state="disabled")

    def redraw(self):
        self.ax_h.clear()
        self.ax_v.clear()

        for f in self.flights:
            x = [-row[1] for row in f["table"]]                   # negative: before the IAF (m)
            line, = self.ax_h.plot(x, [row[2] for row in f["table"]], label=f["label"])
            self.ax_v.plot(x, [row[3] / KT for row in f["table"]],
                           color=line.get_color(), label=f["label"])
            if f["altitude"] is not None:                          # mark the entry WP
                self.ax_h.plot(-f["dist_nm"] * NM, f["altitude"], "o", color=line.get_color())
                self.ax_h.annotate(f"{f['star']}: {f['altitude']:.0f} m",
                                   (-f["dist_nm"] * NM, f["altitude"]),
                                   textcoords="offset points", xytext=(8, 8))

        self.ax_h.axhline(6000 * ft, color="gray", linestyle="--", linewidth=0.8)
        self.ax_h.set_ylabel("h [m]")
        self.ax_h.set_title("Continuous descent (CDO) until the IAF (x = 0)")
        self.ax_h.grid(True)
        self.ax_v.set_xlabel("x [m]")
        self.ax_v.set_ylabel("TAS [kt]")
        self.ax_v.grid(True)

        if self.flights:
            self.ax_h.legend(loc="upper right", fontsize=8)

        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    SimulatorApp(root)
    root.mainloop()