# Basic Examples

## Finding Symptoms

Here is an example of some code
```java
phenotype "Patient Temperatures" version "2";

     include ClarityCore version "1.0" called Clarity;

     documentset NursingNotes:
        Clarity.createReportTagList(["Nurse"]);

     termset TemperatureTerms:
        ["temp","temperature","t"];

      define Temperature:
        Clarity.ValueExtraction({
          termset:[TemperatureTerms],
          documentset: [NursingNotes],
          minimum_value: "96",
          maximum_value: "106"
          });

      define final hasFever:
          where Temperature.value >= 100.4;
```

## Looking up stuff

### Looking up more stuff
