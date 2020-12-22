import argparse

import matplotlib.pyplot as plt
import numpy as np
from joblib import dump, load


plt.style.use("seaborn-white")

parser = argparse.ArgumentParser("Learn surrogate model form simulation")
parser.add_argument(
    "-study_dir", help="The study directory, usually '$(MERLIN_WORKSPACE)'"
)
args = parser.parse_args()

study_dir = args.study_dir
npz_path = f"{study_dir}/learner/all_iter_results.npz"
learner_path = f"{study_dir}/learner/surrogate.joblib"
new_samples_path = f"{study_dir}/pick_new_inputs/new_samples.npy"
new_exploit_samples_path = f"{study_dir}/pick_new_inputs/new_exploit_samples.npy"
new_explore_samples_path = f"{study_dir}/pick_new_inputs/new_explore_samples.npy"
new_explore_star_samples_path = (
    f"{study_dir}/pick_new_inputs/new_explore_star_samples.npy"
)
optimum_path = f"{study_dir}/optimizer/optimum.npy"
old_best_path = f"{study_dir}/optimizer/old_best.npy"

from_file = np.load(npz_path, allow_pickle=True)

data = from_file["arr_0"].item()

X = []
y = []

for i in data.keys():
    X.append(data[i]["Inputs"])
    y.append(data[i]["Outputs"])

existing_X = np.array(X)
existing_y = np.array(y)

surrogate = load(learner_path)

new_samples = np.load(new_samples_path)
new_exploit_samples = np.load(new_exploit_samples_path)
new_explore_samples = np.load(new_explore_samples_path)
new_explore_star_samples = np.load(new_explore_star_samples_path)
optimum = np.load(optimum_path)
old_best = np.load(old_best_path)


def rosenbrock_mesh():
    X_mesh_plot = np.array([np.linspace(-2, 2, n_points), np.linspace(-1, 3, n_points)])
    X_mesh = np.meshgrid(X_mesh_plot[0], X_mesh_plot[1])

    Z_mesh = (1 - X_mesh[0]) ** 2 + 100 * (X_mesh[1] - X_mesh[0] ** 2) ** 2

    return X_mesh, Z_mesh


# Script for N_dim Rosenbrock function
n_points = 250

X_mesh, Z_mesh = rosenbrock_mesh()

Z_pred = surrogate.predict(np.c_[X_mesh[0].ravel(), X_mesh[1].ravel()])
Z_pred = Z_pred.reshape(X_mesh[0].shape)

# Surface plot
plt.rcParams.update({"font.size": 15})
fig = plt.figure(figsize=(30, 45))

ax = fig.add_subplot(3, 2, 1, projection="3d")
ax.plot_surface(
    X_mesh[0],
    X_mesh[1],
    Z_mesh,
    rstride=5,
    cstride=5,
    cmap="jet",
    alpha=0.4,
    edgecolor="none",
)
ax.scatter(existing_X[:, 0], existing_X[:, 1], existing_y, marker="x")
ax.view_init(45, 45)
ax.set_xlabel("DIM_1")
ax.set_ylabel("DIM_2")
ax.set_title("Rosenbrock Function")

ax = fig.add_subplot(3, 2, 2, projection="3d")
ax.plot_surface(
    X_mesh[0],
    X_mesh[1],
    Z_pred,
    rstride=5,
    cstride=5,
    cmap="jet",
    alpha=0.4,
    edgecolor="none",
)
ax.scatter(existing_X[:, 0], existing_X[:, 1], existing_y, marker="x")
ax.view_init(45, 45)
ax.set_xlabel("DIM_1")
ax.set_ylabel("DIM_2")
ax.set_title("Surrogate Function")

ax = fig.add_subplot(3, 2, 3, projection="3d")
ax.plot_surface(
    X_mesh[0],
    X_mesh[1],
    np.clip(Z_mesh, -100, 100),
    rstride=5,
    cstride=5,
    cmap="jet",
    alpha=0.4,
    edgecolor="none",
)
ax.scatter(
    existing_X[:, 0], existing_X[:, 1], np.clip(existing_y, -100, 100), marker="x"
)
ax.view_init(45, 45)
ax.set_xlabel("DIM_1")
ax.set_ylabel("DIM_2")
ax.set_title("Rosenbrock Function clipped")

ax = fig.add_subplot(3, 2, 4, projection="3d")
ax.plot_surface(
    X_mesh[0],
    X_mesh[1],
    np.clip(Z_pred, -100, 100),
    rstride=5,
    cstride=5,
    cmap="jet",
    alpha=0.4,
    edgecolor="none",
)
ax.scatter(
    existing_X[:, 0], existing_X[:, 1], np.clip(existing_y, -100, 100), marker="x"
)
ax.view_init(45, 45)
ax.set_xlabel("DIM_1")
ax.set_ylabel("DIM_2")
ax.set_title("Surrogate Function clipped")

ax = fig.add_subplot(3, 2, 5)
ax.scatter(existing_X[:, 0], existing_X[:, 1], label="Existing Inputs")
ax.scatter(new_samples[:, 0], new_samples[:, 1], label="Suggested Inputs")
ax.annotate("Predicted Optimum", xy=optimum, xytext=(1, 0), arrowprops=dict(width=0.01))
ax.annotate(
    "Current Best", xy=old_best, xytext=(-1.5, 1.5), arrowprops=dict(width=0.01)
)
ax.annotate("Actual Minimum", xy=(1, 1), xytext=(1.5, 2.5), arrowprops=dict(width=0.01))

ax.set_xlabel("DIM_1")
ax.set_ylabel("DIM_2")
ax.set_title("Existing Inputs vs Suggested Inputs")
ax.legend()
ax.grid()

ax = fig.add_subplot(3, 2, 6)
ax.scatter(
    new_exploit_samples[:, 0], new_exploit_samples[:, 1], label="Exploit Samples"
)
ax.scatter(
    new_explore_samples[:, 0], new_explore_samples[:, 1], label="Explore Samples"
)
ax.scatter(
    new_explore_star_samples[:, 0],
    new_explore_star_samples[:, 1],
    label="Explore_star Samples",
)
ax.annotate("Predicted Optimum", xy=optimum)
ax.annotate("Current Best", xy=old_best)

ax.set_xlabel("DIM_1")
ax.set_ylabel("DIM_2")
ax.set_title("Suggested Inputs zoomed in")
ax.legend()
ax.grid()

plt.savefig("results.png")
