+++
title = "Automatically Evading Classifiers"
+++

**EvadeML** is an evolutionary framework based on genetic programming
  for automatically finding variants that evade detection by machine
  learning-based malware classifiers.

<center>
<a href="/images/method.png"><img src="/images/method.png" alt="Overview" width="650px" height="199px"></a>
</center>
<p>
Machine learning is widely used to develop classifiers for security
tasks. However, the robustness of these methods against motivated
adversaries is uncertain. In this work, we propose a generic method to
evaluate the robustness of classifiers under attack. The key idea is to
stochastically manipulate a malicious sample to find a variant that
preserves the malicious behavior but is classified as benign by the
classifier. We present a general approach to search for evasive variants
and report on results from experiments using our techniques against two
PDF malware classifiers, PDFrate and Hidost. 

Our method is able to automatically find evasive variants for both
classifiers for all of the 500 malicious seeds in our study. Our results
suggest a general method for evaluating classifiers used in security
applications, and raise serious doubts about the effectiveness of
classifiers based on superficial features in the presence of
adversaries.

<center>
<a href="/images/accumulated_evasion_by_trace_length.png"><img src="/images/accumulated_evasion_by_trace_length.png" alt="Overview" width="531px" height="369px"></a>
</center>


## References

### Paper

Weilin Xu, Yanjun Qi, and David Evans. [_Automatically Evading
Classifiers A Case Study on PDF Malware Classifiers_](/docs/evademl.pdf).  [_Network and
Distributed Systems Symposium
2016_](https://www.internetsociety.org/events/ndss-symposium-2016),
21-24 February 2016, San Diego, California. Full paper (15 pages): [[PDF](/docs/evademl.pdf)]

### Talks

[**Classifiers Under Attack**](https://youtu.be/XYJamxDROOs), David Evans' talk at [_USENIX Enigma 2017_](https://www.usenix.org/conference/enigma2017/conference-program/presentation/evans) (1 February 2017)  
[**Automatically Evading Classifiers**](//www.jeffersonswheel.org/2016/ndss-talk-automatically-evading-classifiers-including-gmails), Weilin Xu's talk at NDSS 2016 (24 February 2016)  
[More talks...](/talks)

### Source Code

<a href="https://github.com/uvasrg/EvadeML">https://github.com/uvasrg/EvadeML</a>  

## Team

[Weilin Xu](http://www.cs.virginia.edu/~wx4ed/) (Lead PhD Student)  
Anant Kharkar (Undergraduate Researcher)  
Helen Simecek (Undergraduate Researcher)  

[Yanjun Qi](https://www.cs.virginia.edu/yanjun/) (Faculty Co-Advisor)  
[David Evans](https://www.cs.virginia.edu/evans) (Faculty Co-Advisor)  
