# Quantifying Bias In Hierarchical Category Sysyems
Code to analyze western and gender bias as the category and item (book) level in both the Library of Congress Classification (LCC) and the Dewey Decimal Classification (DDC). An analysis of bias towards domestic mammals versus wild mammals in WordNet is also included.

The analyses are presented in Warburton, K., Kemp, C., Xu, Y., & Frermann, L. (2024). Quantifying Bias in Hierarchical Category Systems. _Open Mind: Discoveries in Cognitive Science_. https://doi.org/10.1162/opmi_a_00121

## Required Python Libraries
### For main analyses:
* numpy
* scipy
* matplotlib
* tabulate
* statistics
* pickle
  
### Additional Libraries
#### For parsing MARC Records:
* pymarc

#### For parsing author gender data:
* regex
* pyarrow
* polars
* pandas

#### For scraping LibraryThing
* BeautifulSoup
  
## Attributions
All copyright rights in the Dewey Decimal Classification system are owned by OCLC. Dewey, Dewey Decimal Classification, DDC and WebDewey are registered trademarks of OCLC. This project contains information from OhioLINK Circulation Data which is made available by OCLC Online Computer Library Center, Inc. and OhioLINK under the ODC Attribution License. LCC outlines are extracted from PDFs created by the Library of Congress and stored at: https://www.loc.gov/catdir/cpso/lcco/.

## Other
This is code that was written a while ago and alread existed on OSF in this format. I've moved it here as well. Some data can only be found on OSF as it is too large for GitHub. **See the full project at: https://osf.io/wd9c6/**
