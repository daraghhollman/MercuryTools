import datetime as dt

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from hermean_toolbelt import mag, plotting_tools, trajectory, boundary_crossings

mpl.rcParams["font.size"] = 14


###################### MAG #########################
root_dir = "/home/daraghhollman/Main/data/mercury/messenger/mag/"
philpott_crossings = boundary_crossings.Load_Crossings("../../philpott_crossings.p")

data = mag.Load_Messenger(
    [
        root_dir + "2011/04_APR/MAGMSOSCIAVG11101_01_V08.TAB",
    ]
)

start = dt.datetime(year=2011, month=4, day=11, hour=5, minute=0)
end = dt.datetime(year=2011, month=4, day=11, hour=5, minute=30)

# Isolating only a particular portion of the files
data = mag.StripData(data, start, end)

# Converting to MSM
data = mag.MSO_TO_MSM(data)

# Accounting for solar wind aberration angle
data = mag.AdjustForAberration(data)

# This data can then be plotted using external libraries
fig = plt.figure()

ax1 = plt.subplot2grid((6, 3), (0, 0), colspan=1, rowspan=2)
ax2 = plt.subplot2grid((6, 3), (0, 1), colspan=1, rowspan=2)
ax3 = plt.subplot2grid((6, 3), (0, 2), colspan=1, rowspan=2)
trajectory_axes = [ax1, ax2, ax3]

ax4 = plt.subplot2grid((6, 3), (2, 0), colspan=3)
ax5 = plt.subplot2grid((6, 3), (3, 0), colspan=3)
ax6 = plt.subplot2grid((6, 3), (4, 0), colspan=3)
ax7 = plt.subplot2grid((6, 3), (5, 0), colspan=3)
mag_axes = [ax4, ax5, ax6, ax7]

ax4.set_title(" ")

to_plot = ["mag_x", "mag_y", "mag_z", "mag_total"]
y_labels = ["B$_x$", "B$_y$", "B$_z$", "|B|"]

for i, ax in enumerate(mag_axes):

    # Plot Data
    ax.plot(data["date"], data[to_plot[i]], color="black", lw=0.8)
    ax.set_ylabel(y_labels[i])

    # Plot hline at 0
    ax.axhline(0, color="grey", ls="dotted")

    ax.set_xmargin(0)
    ax.tick_params("x", which="major", direction="inout", length=16, width=1)
    ax.tick_params("x", which="minor", direction="inout", length=8, width=0.8)

    # Plotting crossing intervals as axvlines
    boundary_crossings.Plot_Crossing_Intervals(ax, start, end, philpott_crossings, label=True)

    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(10))


# Plotting ephemeris information to the last panel
# We need a metakernel to retrieve ephemeris information
metakernel = "/home/daraghhollman/Main/SPICE/messenger/metakernel_messenger.txt"
plotting_tools.Add_Tick_Ephemeris(
    mag_axes[-1],
    metakernel,
    include={"date", "hours", "minutes", "range", "latitude", "local time"},
)

for ax in mag_axes:
    # For some reason sharex works differently for subplot2grid so we need
    # to remove tick labels manually
    if ax != mag_axes[-1]:
        ax.set_xticklabels([])



##################### TRAJECTORIES ######################
# Add trajectory subplot

# we are going to get positions between these two dates
time_padding = dt.timedelta(hours=6)
dates = [start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")]
padded_dates = [
    (start - time_padding).strftime("%Y-%m-%d %H:%M:%S"),
    (end + time_padding).strftime("%Y-%m-%d %H:%M:%S"),
]

frame = "MSM"

# Get positions in MSO coordinate system
positions = trajectory.Get_Trajectory("Messenger", dates, metakernel, frame=frame)
padded_positions = trajectory.Get_Trajectory("Messenger", padded_dates, metakernel, frame=frame)

# Convert from km to Mercury radii
positions /= 2439.7
padded_positions /= 2439.7

trajectory_axes[0].plot(positions[:, 0], positions[:, 1], color="magenta", lw=3, zorder=10)
trajectory_axes[1].plot(positions[:, 0], positions[:, 2], color="magenta", lw=3, zorder=10, label="Plotted Trajectory")
trajectory_axes[2].plot(positions[:, 1], positions[:, 2], color="magenta", lw=3, zorder=10)

# We also would like to give context and plot the orbit around this
trajectory_axes[0].plot(padded_positions[:, 0], padded_positions[:, 1], color="grey")
trajectory_axes[1].plot(padded_positions[:, 0], padded_positions[:, 2], color="grey", label=r"Trajectory $\pm$ 6 hours")
trajectory_axes[2].plot(padded_positions[:, 1], padded_positions[:, 2], color="grey")

planes = ["xy", "xz", "yz"]
for i, ax in enumerate(trajectory_axes):
    plotting_tools.Plot_Mercury(
        ax, shaded_hemisphere="left", plane=planes[i], frame=frame
    )
    plotting_tools.AddLabels(ax, planes[i], frame=frame)
    plotting_tools.PlotMagnetosphericBoundaries(ax, plane=planes[i], add_legend=True)
    plotting_tools.SquareAxes(ax, 4)

trajectory_axes[1].legend(bbox_to_anchor=(0.5, 1.2), loc="center", ncol=2, borderaxespad=0.5)

plt.show()
