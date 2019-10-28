+++
title = "EvadeML: Evading Machine Learning Classifiers"
type = "index"
+++

# Is Robust Machine Learning Possible?

Machine learning has shown remarkable success in solving complex
classification problems, but current machine learning techniques
produce models that are vulnerable to adversaries who may wish to
confuse them, especially when used for security applications like
malware classification.

<img align="right" src="/images/mlassumption.png" width=600>

The key assumption of machine learning is that a model that is trained
on training data will perform well in deployment because the training
data is representative of the data that will be seen when the
classifier is deployed.

When machine learning classifiers are used in security applications,
however, adversaries may be able to generate samples that exploit the
invalidity of this assumption. 

Our project is focused on understanding, evaluating, and improving the
effectiveness of machine learning methods in the presence of motivated
and sophisticated adversaries.

## Projects

<section style="display: table;width: 100%">
  <header style="display: table-row; padding: 0.5rem">
    <div style="display: table-cell; padding: 0.5rem; color:#FFFFFF;background:#663399;text-align: center;width: 49%">
<a href="/gpevasion" class="hlink">Genetic&nbsp;Programming</a>
    </div>
        <div style="display: table-cell; padding: 0.5rem;color:#000000;background: #FFFFFF;text-align: center; width:2%""></div>
    <div style="display: table-cell; padding: 0.5rem;color:#FFFFFF;background: #2c0f52;text-align: center;">
<a href="/squeezing" class="hlink">Feature Squeezing</a>
    </div>
  </header>
  <div style="display: table-row;">
    <div style="display: table-cell;">
    <a href="/gpevasion"><img src="/images/geneticsearch.png" alt="Genetic Search" width="100%" align="center"></a><br>
Evolutionary framework to automatically find variants that preserve malicious behavior but evade a target classifier.
    </div>
    <div style="display: table-cell;"></div>
    <div style="display: table-cell;text-align:center">
    <a href="/squeezing"><img src="/images/squeezing.png" alt="Feature Squeezing" width="100%" align="center"></a><br>
Reducing the search space for adversaries by coalescing inputs.<br>
<font size="-1" style="color:#666;">(The top row shows L<sub>0</sub> adversarial examples, squeezed by median smoothing.)</font>
</div>
  </div>
</section>

## Papers

Saeed Mahloujifar<sup><font size="-2">&#9733;</font></sup>, Xiao Zhang<sup><font size="-2">&#9733;</font></sup>, Mohammad Mahmooday, and David Evans. [_Empirically Measuring Concentration: Fundamental Limits on Intrinsic Robustness_](/docs/empirically-measuring-concentration.pdf). In [_NeurIPS 2019_](https://nips.cc/Conferences/2019/). Vancouver, December 2019. (Earlier versions appeared in [_Debugging Machine Learning Models_](https://debug-ml-iclr2019.github.io/) and [_Safe Machine Learning: Specification, Robustness and Assurance_](https://sites.google.com/view/safeml-iclr2019), workshops attached to m>Seventh International Conference on Learning Representations</em></a> (ICLR). New Orleans. May 2019. [[PDF](/docs/empirically-measuring-concentration.pdf)] [[Post](https://jeffersonswheel.org/empirically-measuring-concentration/)]

Xiao Zhang and David Evans. [_Cost-Sensitive Robustness against Adversarial Examples_](/docs/cost-sensitive-robustness.pdf). In <a
href="https://iclr.cc/Conferences/2019"><em>Seventh International Conference on Learning Representations</em></a> (ICLR). New Orleans. May 2019. [<a href="https://arxiv.org/abs/1810.09225">arXiv</a>] [<a
href="https://openreview.net/forum?id=BygANhA9tQ">OpenReview</a>] [<a href="/docs/cost-sensitive-robustness.pdf">PDF</a>]

Weilin Xu, David Evans, Yanjun Qi. [_Feature Squeezing: Detecting Adversarial Examples in Deep Neural Networks_](/docs/featuresqueezing.pdf). 
[_2018 Network and Distributed System Security Symposium_](https://www.ndss-symposium.org/ndss2018/). 18-21 February, San Diego, California. Full paper (15 pages): [[PDF](/docs/featuresqueezing.pdf)]

Weilin Xu, Yanjun Qi, and David Evans. [_Automatically Evading
Classifiers A Case Study on PDF Malware Classifiers_](/docs/evademl.pdf).  [_Network and Distributed Systems Symposium 2016_](https://www.internetsociety.org/events/ndss-symposium-2016), 21-24 February 2016, San Diego, California. Full paper (15 pages): [[PDF](/docs/evademl.pdf)]

[More Papers...](papers/)

## Talks

<p>
<a href="https://jeffersonswheel.org/fosad2019/"><b>Trustworthy Machine Learning</b></a>. Mini-course at <a href="http://www.sti.uniurb.it/events/fosad19/"><em>19th International School on Foundations of Security Analysis and Design</em></a>. Bertinoro, Italy. 26&ndash;28 August 2019.
</p>
<a href="https://vid.umd.edu/detsmediasite/Play/e8009558850944bfb2cac477f8d741711d?catalog=74740199-303c-49a2-9025-2dee0a195650"><b>Can
    Machine Learning Ever Be Trustworthy?</b></a>. University of Maryland, <a href="https://ece.umd.edu/events/distinguished-colloquium-series">Booz
    Allen Hamilton Distinguished Colloquium</a>. 7&nbsp;December
2018. [<a href="https://speakerdeck.com/evansuva/can-machine-learning-ever-be-trustworthy">SpeakerDeck</a>]
[<a href="https://vid.umd.edu/detsmediasite/Play/e8009558850944bfb2cac477f8d741711d?catalog=74740199-303c-49a2-9025-2dee0a195650">Video</a>]
</p>
<p>
<a href="https://speakerdeck.com/evansuva/mutually-assured-destruction-and-the-impending-ai-apocalypse"><b>Mutually
    Assured Destruction and the Impending AI Apocalypse</b></a>.  Opening keynote, <a href="https://www.usenix.org/conference/woot18">12<sup>th</sup> USENIX Workshop on Offensive Technologies</a> 2018. (Co-located with <em>USENIX Security Symposium</em>.) Baltimore, Maryland. 13 August 2018. [<a href="https://speakerdeck.com/evansuva/mutually-assured-destruction-and-the-impending-ai-apocalypse">SpeakerDeck</a>]
</p>
<p>
<a href="https://www.youtube.com/watch?v=sFhD6ABghf8"><b>Is "Adversarial Examples" an Adversarial Example</b></a>. Keynote talk at <a href="https://www.ieee-security.org/TC/SPW2018/DLS/#"><em>1st Deep Learning and Security Workshop</em></a> (co-located with the 39th <em>IEEE Symposium on Security and Privacy</em>). San Francisco, California. 24 May 2018. [<a href="https://speakerdeck.com/evansuva/is-adversarial-examples-an-adversarial-example">SpeakerDeck</a>]
<center>
<iframe width="640" height="360" src="https://www.youtube-nocookie.com/embed/sFhD6ABghf8?rel=0" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe><br>
</p>
</center>

[More Talks...](talks/)

## Code

**EvadeML-Zoo:** [https://github.com/mzweilin/EvadeML-Zoo](https://github.com/mzweilin/EvadeML-Zoo)

**Genetic Evasion:** [https://github.com/uvasrg/EvadeML](https://github.com/uvasrg/EvadeML) (Weilin&nbsp;Xu)  

**Cost-Sensitive Robustness:** [https://github.com/xiaozhanguva/Cost-Sensitive-Robustness](https://github.com/xiaozhanguva/Cost-Sensitive-Robustness) (Xiao&nbsp;Zhang)

**Adversarial Learning Playground**: [https://github.com/QData/AdversarialDNN-Playground](https://github.com/QData/AdversarialDNN-Playground) (Andrew Norton) (mostly supersceded by the EvadeML-Zoo toolkit)

**Feature Squeezing:** [https://github.com/uvasrg/FeatureSqueezing](https://github.com/uvasrg/FeatureSqueezing) (Weilin Xu) (supersceded by the EvadeML-Zoo toolkit)

## Team

[Weilin Xu](http://www.cs.virginia.edu/~wx4ed/) (Lead PhD Student, leading work on [Feature Squeezing](/squeezing) and [Genetic Evasion](/gpevasion))  
[Mainuddin Ahmad Jonas](https://sites.google.com/site/mahmadjonas/) (PhD student, working on adversarial examples)  
[Fnu Suya](https://github.com/suyeecav) (PhD student, working on batch attacks)  
[Xiao Zhang](https://people.virginia.edu/~xz7bc/) (PhD student, working on cost-sensitive adversarial robustness)

Yuancheng Lin (Undergraduate researchers working on adversarial examples, since summer 2018)
Helen Simecek (Undergraduate researcher working on [Genetic Evasion](/gpevasion), since 2017)  
Matthew Wallace (Undergraduate researcher working on natural language deception, since summer 2018)

[David Evans](https://www.cs.virginia.edu/evans) (Faculty Co-Advisor)  
[Yanjun Qi](https://www.cs.virginia.edu/yanjun/) (Faculty Co-Advisor for Weilin Xu)  
[Yuan Tian](https://www.ytian.info/) (Faculty Co-Advisor for Fnu Suya) 

### Alumni

Johannes Johnson (Undergraduate researcher working on malware classification and evasion, summer 2018)  
Anant Kharkar (Undergraduate Researcher worked on [Genetic Evasion](/gpevasion), 2016-2018)  
[Noah Kim](http://www.noahdkim.com/) (Undergraduate Researcher worked on [EvadeML-Zoo](/zoo), 2017)  
Felix Park (Undergradaute Researcher, worked on color-aware preprocessors, 2017-2018)  
