+++
title = "Empirically Measuring Concentration"
+++

## Estimating the Intrinsic Robustness for Image Benchmarks 

<center>
<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/7yFcqwNWxwQ" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</center>

Recent theoretical results, starting with Gilmer et al.'s
[_Adversarial Spheres_](https://aipavilion.github.io/) (2018), show
that if inputs are drawn from a concentrated metric probability space,
then adversarial examples with small perturbation are inevitable.c The
key insight from this line of research is that [_concentration of
measure_](https://en.wikipedia.org/wiki/Concentration_of_measure">)
gives lower bound on adversarial risk for a large collection of
classifiers (e.g. imperfect classifiers with risk at least $\alpha$),
which further implies the impossibility results for robust learning
against adversarial examples.

<center><img src="/images/concentration/advRisk.png" width="80%" align="center"></center>

However, it is not clear whether these theoretical results apply to
actual distributions such as images. This work presents a method for
empirically measuring and bounding the concentration of a concrete
dataset which is proven to converge to the actual concentration. More
specifically, we prove that by simultaneously increasing the sample
size and a complexity parameter of the selected collection of subsets
$\mathcal{G}$, the concentration of the empirical measure based on
samples converges to the actual concentration asymptotically.

<center><img src="/images/concentration/theory.png" width="70%" align="center"></center>

To solve the empirical concentration problem, we propose heuristic
algorithms to find error regions with small expansion under both
$\ell_\infty$ and $\ell_2$ metrics. 

For instance, our algorithm for $\ell_\infty$ starts by sorting the
dataset based on the empirical density estimated using k-nearest
neighbor, and then obtains $T$ rectangular data clusters by performing
k-means clustering on the top-$q$ densest images. After expanding each
of the rectangles by $\epsilon$, the error region $\mathcal{E}$ is
then specified as the complement of the expanded rectangles (the
reddish region in the following figure). Finally, we search for the
best error region by tuning the number of rectangles $T$ and the
initial coverage percentile $q$.

<img src="/images/concentration/alg.png" width="80%" align="center"></center>

Based on the proposed algorithm, we empirically measure the
concentration for image benchmarks, such as MNIST and
CIFAR-10. Compared with state-of-the-art robustly trained models, our
estimated bound shows that, for most settings, there exists a large
gap between the robust error achieved by the best current models and
the theoretical limits implied by concentration.

<img src="/images/concentration/experiments.png" width="100%" align="center"><br></center>

This suggests the concentration of measure is not the only reason
behind the vulnerability of existing classifiers to adversarial
perturbations. Thus, either there is room for improving the robustness
of image classifiers or a need for deeper understanding of the reasons
for the gap between intrinsic robustness and the actual robustness
achieved by robust models.


### Papers

<a href="https://www.cs.virginia.edu/~sm5fd/">Saeed Mahloujifar</a><sup><font size="-2">&#9733;</font></sup>, <a href="https://www.people.virginia.edu/~xz7bc/">Xiao Zhang</a><sup><font size="-2">&#9733;</font></sup>, <a href="https://www.cs.virginia.edu/~mohammad/">Mohamood Mahmoody</a> and <a href="https://www.cs.virginia.edu/evans/">David Evans</a>. [_Empirically Measuring Concentration: Fundamental Limits on Intrinsic Robustness_](/docs/empirically-measuring-concentration.pdf). In [_NeurIPS 2019_](https://nips.cc/Conferences/2019/) ([_spotlight presentation_](https://nips.cc/Conferences/2019/ScheduleMultitrack?event=15792)). Vancouver, December 2019. [[PDF](/docs/empirically-measuring-concentration.pdf)] [[arXiv](https://arxiv.org/abs/1905.12202)] 

Preliminary version presented at <a
href="https://sites.google.com/view/safeml-iclr2019">Safe Machine
Learning</a> and <a
href="https://debug-ml-iclr2019.github.io/">Debugging ML Models</a>
workshops at ICLR 2019, as well as <a
href="https://sites.google.com/view/udlworkshop2019/">Uncertainty &
Robustness in Deep Learning</a> workshop at ICML 2019.


### Code

[_https://github.com/xiaozhanguva/Measure-Concentration_](https://github.com/xiaozhanguva/Measure-Concentration)
