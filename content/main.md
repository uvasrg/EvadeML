+++
title = "ScriptInspector: Monitoring Embedded Web Scripts"
+++

### Understanding and Monitoring Embedded Web Scripts

Modern web applications make frequent use of third-party scripts, often
in ways that allow scripts loaded from external servers to make
unrestricted changes to the embedding page and access citical resources
including private user information.

<center>
<a href="/images/overview.png"><img src="/images/overview.png" alt="Overview" width="500px" height="372px"></a>
</center>

**ScriptInspector** assists site administrators in understanding,
monitoring, and restricting the behavior of third-party scripts embedded
in their site.  ScriptInspector is a modified browser that can
intercept, record, and check third-party script accesses to critical
resources against security policies.  

ScriptInspector includes a **Visualizer** tool that allows users to
conveniently view recorded script behaviors and candidate policies and a
**PolicyGenerator** tool that aids script providers and site
administrators in writing policies.  Site administrators can manually
refine these policies with minimal effort to produce policies that
effectively and robustly limit the behavior of embedded scripts.

### Paper

Yuchen Zhou and David Evans. _Understanding and Monitoring Embedded Web Scripts_.  [_36<sup>th</sup> IEEE Symposium on Security and Privacy_](http://www.ieee-security.org/TC/SP2015/) ("Oakland"). San Jose, CA. 18-20 May 2015. 

Full paper (16 pages): {{<pdflink "ScriptInspector.pdf" >}}

### Source Code

<a href="https://github.com/Treeeater/JSAccessVisualizer">https://github.com/Treeeater/JSAccessVisualizer</a>  
Includes code for the ScriptInspector, Visualizer, and PolicyGenerator.

### Policies

[Browse Policies](https://github.com/uvasrg/ScriptInspector/tree/master/content/docs/policies) (or download a [.zip file with all policies](/docs/policies.zip))  
[Spreadsheet with list of URLs and full policy data (.xlsx)](/docs/urls.xlsx)

### Authors

[Yuchen Zhou](http://www.yuchenzhou.info/) (University of Virginia; now at Palo Alto Networks)  
[David Evans](http://www.cs.virginia.edu/evans) (University of Virginia)
