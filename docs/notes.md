# Notes from the May 27 session
Based on the discussion
* Try to see what else is published with the Climate Policy database *@Shota* 
* Extract the policies for the countries we're interested in and see which obvious filters can be applied *@Russell* 
* Train a model or just use a model to work on a taxonomy to label each policy *@Laureen*
* More advanced: have the model rate each policy with regards to resilience

# Notes from the June 10 session
Looking at the paper [Expanding climate policy adoption improves national mitigation efforts](https://www.nature.com/articles/s44168-023-00043-8#MOESM1), we're thinking of doing a similar analysis. The goal is to replicate figure 2. 
* Y-axis would be related to the investments in climate-resilient infrastructure. @Russell
* X-axis would be related to the number of policies related to resilience: the country's "resilience score". @Laureen
* We would also need some control metrics. @Shota

### Policies related to resilience
* List of words related to resilience is based on this paper [A resilience glossary shaped by context: Reviewing resilience-related terms for critical infrastructures](https://www.sciencedirect.com/science/article/pii/S2212420923003734). It is stored in [here](/data/clean/mentges_ci_enhanced_climate_resilience_taxonomy.csv).
* Might need to tune it based on the results (if we get too many false positives, we will narrow down the list)
* **Objective for next session**: Do a first pass at the filtering and get a resilient policy score for each country in the dataset. 