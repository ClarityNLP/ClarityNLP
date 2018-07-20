pft_value_extraction
************************
Custom module built on top of General Value Extraction to extract Pulmonary Function Test Values(PFT)

Overview
========

Please visit value_extraction.rst to get more information on Value Extraction

pft_value_extraction was built to address the specific problem of getting pulmonary function test values from text.
It has an additional feature of extracting unit (if present) for each value that was extracted.
Units supported are ml, l, cc, %, % predicted


It extracts values for
1. FEV1
Ranges that are being used are (0,6),(20,190),(300,6000)
2. FVC
Ranges that are being used are (300,6000),(15,170),(0.3,6)
3. FEV1/FVC
Ranges that are being used are (0,2),(10,180)

These ranges were selected after observing and testing on many instances of pft values present in the MIMIC database.


Value Extractor is meant for general use.
For the sentence "FEV1/FVC is 95% and FVC is 92% predicted", General Value extractor captures FVC as 95%.
In such special situations, building a custom extractor on top of General Value extractor can be very useful.
