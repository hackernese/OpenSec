# Analysis of the experiment

The results demonstrated both the advantage and flaws regarding agentic-based security assessment. From the analysis, Claude Opus 4.7 


## New bugs discovery
Claude is ranked first when it comes to discovering new vulnerabilities (
Grok is second in terms of new bugs discovery (
DeepSeek is ranked last

## Cost and time evaluation
DeepSeek V4 Pro as expected produced the most cost-effective and fastest solution, where the median price across all assessments is roughly 1$ AUD and took around 35.8 minutes to complete the engagement. Claude Opus 4.7 on the other hands experienced the highest cost and time duration of around 14.3$ AUD and 63.4 minutes. Additionally, Grok 4.6 tends to provide a more balanced setup, where the median cost equals 4.8$ and tends to require 39 minutes to accomplish. However, Opus 4.7 produced the best lowest error rate and outliers, where DeepSeek V4 Pro experienced and infinite loop over night which costed over 15$ until manual intervention occurred and Grok 4.6 recorded a 600 minutes engagement.   

# Conclusion
DeepSeek is best when it comes to discovering intentional bugs within the codebase whilst Claude performs best with regards to unveiling new generic vulnerabilities. Additionally, Claude is the only model which managed to link an IDOR with a Self-XSS to esclate it to a more sever vulnerability. This proves that Claude Opus 4.7 is capable to critically analyse the engagement from a perspective of a practical penetration tester. Opus 4.7 and DeepSeek V4 Pro provided the most significant findings, where one is optimised in time execution and cost whilst the other discovered the most unexpected bugs, unique vulnerabilities and resemble a more practical penetration tester mindset.    