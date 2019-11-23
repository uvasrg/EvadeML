+++
title = "Cost-Sensitive Robustness"
+++

Several recent works have developed methods for training classifiers
that are certifiably robust against norm-bounded adversarial
perturbations. However, these methods assume that all the adversarial
transformations provide equal value for adversaries, which is seldom
the case in real-world applications. 

We advocate for cost-sensitive robustness as the criteria for
measuring the classifier's performance for specific tasks. We encode
the potential harm of different adversarial transformations in a cost
matrix, and propose a general objective function to adapt the robust
training method of Wong & Kolter (2018) to optimize for cost-sensitive
robustness. Our experiments on simple MNIST and CIFAR10 models and a
variety of cost matrices show that the proposed approach can produce
models with substantially reduced cost-sensitive robust error, while
maintaining classification accuracy.

<center>
<img src="/images/protecteven.png" width="70%"> 
<div class="caption" align="left" style="padding-left:5rem;padding-right:5rem">
This shows the results of cost-sensitive robustness training to protect the odd classes. By incorporating a cost matrix in the loss function for robustness training, we can produce a model where selected transitions are more robust to adversarial transformation.
</center>

<center>
<a href="/docs/cost-sensitive-poster.pdf"><img src="/images/cost-sensitive-poster-small.png" width="90%" align="center"></a>
</center>

### Paper

Xiao Zhang and David Evans. [_Cost-Sensitive Robustness against Adversarial Examples_](/docs/cost-sensitive-robustness.pdf). In <a
href="https://iclr.cc/Conferences/2019"><em>Seventh International Conference on Learning Representations</em></a> (ICLR). New Orleans. May 2019. [<a href="https://arxiv.org/abs/1810.09225">arXiv</a>] [<a
href="https://openreview.net/forum?id=BygANhA9tQ">OpenReview</a>] [<a href="/docs/cost-sensitive-robustness.pdf">PDF</a>]

### Code

[_https://github.com/xiaozhanguva/Cost-Sensitive-Robustness_](https://github.com/xiaozhanguva/Cost-Sensitive-Robustness)
