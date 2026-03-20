#!/usr/bin/env python3
"""
Parse monitor.log (kubectl top pods/nodes snapshots) and generate a
4-panel resource-usage PNG with a 2×2 layout:

  Top-left  : CGW core pods — CPU (millicores)
  Top-right : CGW core pods — Memory (MiB)
  Bot-left  : Infrastructure pods — CPU (millicores)
  Bot-right : Infrastructure pods — Memory (MiB)

CGW core pods are those whose name starts with cgw-, cgw2-, or cgwproxy-.
All other pods are treated as infrastructure.

Usage:
    python generate_perf_graph.py [LOG_PATH [OUT_PATH]]

Defaults:
    LOG_PATH  = ./monitor.log
    OUT_PATH  = ./monitor_resources.png
"""

import re
import sys
from collections import defaultdict
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration / CLI
# ---------------------------------------------------------------------------
LOG_PATH = sys.argv[1] if len(sys.argv) > 1 else "monitor.log"
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "monitor_resources.png"

# A pod is "CGW core" if its name starts with one of these prefixes.
CGW_CORE_PREFIXES = ("cgw-", "cgw2-", "cgwproxy-")

# ---------------------------------------------------------------------------
# 1. Parse the log  (identical parser to gen_graph.py, proven to work)
# ---------------------------------------------------------------------------
TS_RE  = re.compile(r"^=== (.+?) ===$")
POD_RE = re.compile(r"^(\S+)\s+(\d+)m\s+(\d+)Mi\s*$")

timestamps = []
pod_cpu    = defaultdict(list)   # pod_name -> [cpu_m, ...]   (None = missing)
pod_mem    = defaultdict(list)   # pod_name -> [mem_MiB, ...]

current_ts   = None
current_pods = {}
in_nodes     = False
header_skip  = False


def commit_snapshot():
    global current_ts, current_pods
    if current_ts is None:
        return
    timestamps.append(current_ts)
    all_pods = set(pod_cpu.keys()) | set(current_pods.keys())
    for pod in all_pods:
        if pod in current_pods:
            c, m = current_pods[pod]
            pod_cpu[pod].append(c)
            pod_mem[pod].append(m)
        else:
            pod_cpu[pod].append(None)
            pod_mem[pod].append(None)


with open(LOG_PATH, "r") as fh:
    for line in fh:
        line = line.rstrip("\n")

        m = TS_RE.match(line)
        if m:
            commit_snapshot()
            raw_ts = m.group(1)
            try:
                current_ts = datetime.strptime(raw_ts, "%a %d %b %Y %I:%M:%S %p %Z")
            except ValueError:
                parts = raw_ts.rsplit(" ", 1)
                current_ts = datetime.strptime(parts[0], "%a %d %b %Y %I:%M:%S %p")
            current_pods = {}
            in_nodes     = False
            header_skip  = False
            continue

        if line.startswith("---NODES---"):
            in_nodes    = True
            header_skip = True
            continue

        if header_skip:
            header_skip = False
            continue

        if line.startswith("NAME"):
            continue

        if not in_nodes:
            pm = POD_RE.match(line)
            if pm:
                name    = pm.group(1)
                cpu_m   = int(pm.group(2))
                mem_mib = int(pm.group(3))
                current_pods[name] = (cpu_m, mem_mib)

commit_snapshot()

n_snapshots = len(timestamps)
if n_snapshots == 0:
    print("ERROR: no snapshots parsed", file=sys.stderr)
    sys.exit(1)

t_start  = timestamps[0]
t_end    = timestamps[-1]
duration = t_end - t_start
print(f"Snapshots parsed : {n_snapshots}")
print(f"Time range       : {t_start}  -->  {t_end}")
print(f"Duration         : {duration}")

# Align per-pod series to final length
final_len = n_snapshots
for pod in list(pod_cpu.keys()):
    diff = final_len - len(pod_cpu[pod])
    pod_cpu[pod] = [None] * diff + pod_cpu[pod]
    pod_mem[pod] = [None] * diff + pod_mem[pod]

# ---------------------------------------------------------------------------
# 2. Split pods into CGW core vs. infrastructure
# ---------------------------------------------------------------------------
all_pods   = sorted(pod_cpu.keys())
cgw_pods   = [p for p in all_pods if p.startswith(CGW_CORE_PREFIXES)]
infra_pods = [p for p in all_pods if not p.startswith(CGW_CORE_PREFIXES)]

print(f"\nCGW core pods    : {cgw_pods}")
print(f"Infrastructure   : {infra_pods}")

# ---------------------------------------------------------------------------
# 3. Build X axis (elapsed minutes)
# ---------------------------------------------------------------------------
xs_min = [(t - t_start).total_seconds() / 60.0 for t in timestamps]


def build_series(data_dict, pod_name):
    """Return (xs_clean, ys_clean) dropping None points."""
    x_clean, y_clean = [], []
    for x, y in zip(xs_min, data_dict[pod_name]):
        if y is not None:
            x_clean.append(x)
            y_clean.append(y)
    return x_clean, y_clean


# ---------------------------------------------------------------------------
# 4. Plot
# ---------------------------------------------------------------------------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "matplotlib", "--break-system-packages"])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

# Colour palettes — separate for each group so colours don't collide
try:
    # matplotlib >= 3.7 preferred API (avoids deprecation warning)
    CGW_CMAP   = matplotlib.colormaps["tab10"].resampled(max(len(cgw_pods),  1))
    INFRA_CMAP = matplotlib.colormaps["tab20b"].resampled(max(len(infra_pods), 1))
except AttributeError:
    # older matplotlib fallback
    CGW_CMAP   = plt.cm.get_cmap("tab10",  max(len(cgw_pods),  1))  # noqa: deprecated
    INFRA_CMAP = plt.cm.get_cmap("tab20b", max(len(infra_pods), 1))  # noqa: deprecated

fig, axes = plt.subplots(2, 2, figsize=(22, 14))
fig.suptitle(
    f"Kubernetes Resource Usage\n"
    f"{t_start.strftime('%Y-%m-%d %H:%M:%S')}  to  {t_end.strftime('%H:%M:%S')}  "
    f"({n_snapshots} snapshots, {int(duration.total_seconds() // 60)} min)",
    fontsize=14, fontweight="bold"
)

ax_cgw_cpu, ax_cgw_mem = axes[0][0], axes[0][1]
ax_inf_cpu, ax_inf_mem = axes[1][0], axes[1][1]


def draw_panel(ax, data_dict, pod_list, cmap, ylabel, title):
    for i, pod in enumerate(pod_list):
        xc, yc = build_series(data_dict, pod)
        if xc:
            ax.plot(xc, yc, label=pod, color=cmap(i), linewidth=1.4, alpha=0.88)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_xlabel("Elapsed time (minutes)", fontsize=10)
    ax.set_title(title, fontsize=12)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=8))
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper left", bbox_to_anchor=(0, 1),
              fontsize=8, ncol=1, title="Pods",
              framealpha=0.75)


draw_panel(ax_cgw_cpu,  pod_cpu,  cgw_pods,   CGW_CMAP,
           "CPU (millicores)", "CGW Core Pods — CPU")

draw_panel(ax_cgw_mem,  pod_mem,  cgw_pods,   CGW_CMAP,
           "Memory (MiB)",     "CGW Core Pods — Memory")

draw_panel(ax_inf_cpu,  pod_cpu,  infra_pods, INFRA_CMAP,
           "CPU (millicores)", "Infrastructure Pods — CPU")

draw_panel(ax_inf_mem,  pod_mem,  infra_pods, INFRA_CMAP,
           "Memory (MiB)",     "Infrastructure Pods — Memory")

plt.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
print(f"\nPNG saved to     : {OUT_PATH}")
