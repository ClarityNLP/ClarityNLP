### Vocabulary Expansion

**About:** 

This API is responsible for vocabulary explosion for a given concept. API accepts a _type_ which can be synonyms, ancestors or descendants. The API has to accept the _concept_ name which is supposed be exploded. The vocabulary _vocab_ can also be passed as an optional parameter.

**Parameters:**

- Type: mandatory
  - 1: synonyms
  - 2: ancestors
  - 3: descendants
- Concept: mandatory
- Vocab: optional

**Example usage:**

```
~/vocabExpansion?type=1&concept=Inactive

~/vocabExpansion?type=1&concept=Inactive&vocab=SNOMED
```