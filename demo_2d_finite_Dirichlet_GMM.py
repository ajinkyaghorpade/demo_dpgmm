'''
 Author: Thierry Guillemot <thierry.guillemot.work@gmail.com>
 License: BSD 3 clause

 Author: Ajinkya Ghorpade <ajinkya@mit.edu>
 This code was used to demonstrate a finite Gaussian Mixture Model with dirichlet distribution prior on a 2-D toy dataset.
 '''
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.stats import multivariate_normal
import matplotlib._color_data as mcd

from sklearn.mixture import BayesianGaussianMixture

np.random.seed(1)

# This method calculates the posterior probability of the given point under finite GMM.
def score_fn_dpgmm(x, estimator):
    return estimator.score_samples(x.reshape(1,-1))

# This method calculates the posterior probability of the given point under its component distribution
def score_fn_mvn(x, mean, covar):
    return multivariate_normal.pdf(x, mean, covar)

# This method plots the contours of the posterior distribution and the posterior Gaussian components
def plot_contours(ax, estimator, weights, means, covars, xx, yy):
    new_colors = colors
    if new_colors.shape[0] < means.shape[0]:
        new_clusters = means.shape[0] - new_colors.shape[0]
        new_colors = np.append(new_colors, list(mcd.CSS4_COLORS.values())[0:4*(new_clusters-1):4])
    zz = np.array([score_fn_dpgmm(x, estimator) for x in np.c_[xx.ravel(), yy.ravel()]])
    zz = zz.reshape(xx.shape)
    ax.contourf(xx, yy, zz, linestyles = 'dashed', alpha = 0.5)
    for n in range(means.shape[0]):
        zz = np.array([score_fn_mvn(x, means[n], covars[n]) for x in np.c_[xx.ravel(), yy.ravel()]])
        zz = zz.reshape(xx.shape)
        ax.contour(xx, yy, zz, colors=new_colors[n - 1], linestyles='dashed', linewidths=1, alpha = 0.4)


# This method plots the posterior distributions
def plot_results(ax1, ax2, estimator, xx, yy):
    plot_contours(ax1, estimator, estimator.weights_, estimator.means_,
                  estimator.covariances_, xx, yy)
    ax2.get_xaxis().set_tick_params(direction='out')
    ax2.yaxis.grid(True, alpha=0.7)
    #keep non-zero weights only
    weights = estimator.weights_[np.where(estimator.weights_>SMALL_PROBS)]
    for k, w in enumerate(weights):
        ax2.bar(k, w, width=0.3, color='#56B4E9', zorder=3,
                align='center', edgecolor='black')
        ax2.text(k, w + 0.007, "%.1f%%" % (w * 100.),
                 horizontalalignment='center')
    ax2.set_xlim(-.6, 3 * n_components - .4)
    ax2.set_ylim(0., 1.1)
    ax2.tick_params(axis='y', which='both', left='off',
                    right='off', labelleft='off')
    ax2.tick_params(axis='x', which='both', top='off')


# This method plots the 2-D toy data set
def init_plots(ax1, ax2, X, y, title, plot_title=False, generate_mesh = False):
    ax1.set_title(title)
    ax1.scatter(X[:, 0], X[:, 1], s=15, marker='o', color=colors[y], alpha=0.8)
    ax1.set_xlim(-4., 4.)
    ax1.set_ylim(-6., 6.)
    ax1.set_xticks(())
    ax1.set_yticks(())

    if plot_title:
        ax1.set_ylabel('Estimated Mixtures')
        ax2.set_ylabel('Weight of each component')

    # Initialize the meshgrid for drawing contours and speed
    xx = []
    yy = []
    if generate_mesh:
        x_min, x_max = ax1.get_xlim()
        y_min, y_max = ax1.get_ylim()
        h = max((x_max-x_min)/50., (y_max-y_min)/50.)
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                      np.arange(y_min, y_max, h))
    return [ax1, ax2, xx, yy]


# Parameters of the dataset
random_state, n_components, n_features = 2, 6, 2
colors = np.array(['#0072B2', '#F0E442', '#D55E00', '#EE82EE', '#A0522D', '#2E8B57'])

covars = np.array([[[.1, .02], [.02, .15]],
                   [[.3, -.01], [-.01, .3]],
                   [[.7, .4], [.3, .6]],
                   [[.3, .03], [.09, .3]],
                   [[.6, -.07], [-.05, .6]],
                   [[.6, .13], [.12, .86]]])
samples = np.array([300, 500, 400, 400, 400, 300])
means = np.array([[.8, -2.0],
                  [-2.5, -.05],
                  [-2, 2.0],
                  [1.2, 2.5],
                  [2, 0.7],
                  [-1, -2.0]])

# mean_precision_prior= 0.8 to minimize the influence of the prior
estimators = [    ("Variational Inference in Finite mixture with Dirichlet Prior ",
     BayesianGaussianMixture(
        weight_concentration_prior_type="dirichlet_distribution",
        n_components=3 * n_components, reg_covar=0, init_params='random',
        max_iter=5, mean_precision_prior=.8,
        random_state=random_state, tol=1e-5), [1])]

#Discard small proportions
SMALL_PROBS = 0

# Generate data
rng = np.random.RandomState(random_state)
X = np.vstack([
    rng.multivariate_normal(means[j], covars[j], samples[j])
    for j in range(n_components)])
y = np.concatenate([j * np.ones(samples[j], dtype=int)
                    for j in range(n_components)])

# np.savetxt('data.csv',np.asarray(np.concatenate([X,y.reshape(-1,1)],1)), delimiter=',')

# Fit the model and plot the contours
for (title, estimator, concentrations_prior) in estimators:
    plt.figure(figsize=(4.7 * 3, 8))
    plt.subplots_adjust(bottom=.04, top=0.90, hspace=.05, wspace=.05,
                        left=.03, right=.99)
    gs = gridspec.GridSpec(3, len(concentrations_prior))
    for k, concentration in enumerate(concentrations_prior):
        estimator.weight_concentration_prior = concentration
        estimator.warm_start = True
        ax1 = plt.subplot(gs[0:2, k])
        ax2 = plt.subplot(gs[2, k])
        (ax1, ax2, xx, yy) = init_plots(ax1, ax2, X, y, r"%s$%.1e$" % (title, concentration),
                                plot_title=k == 0)
        plt.pause(0.1)
        raw_input("Press ENTER to continue.")
        estimator.fit(X)
        ax1.clear()
        ax2.clear()
        (ax1, ax2, xx, yy) = init_plots(ax1, ax2, X, y, r"%s$%.1e$" % (title, concentration),
                                plot_title=k == 0, generate_mesh=True)
        plot_results(ax1, ax2, estimator, xx, yy)
        plt.pause(0.001)
        raw_input("Press ENTER to continue.")
        while not estimator.converged_:
            estimator.fit(X)
            ax1.clear()
            ax2.clear()
            (ax1, ax2, _, _) = init_plots(ax1, ax2, X, y, r"%s$%.1e$" % (title, concentration),
                                    plot_title=k == 0)
            plot_results(ax1, ax2, estimator, xx, yy)
            plt.pause(0.001)
        print(estimator.converged_)
        raw_input("Press ENTER to continue.")