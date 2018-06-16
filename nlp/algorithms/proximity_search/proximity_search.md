# proximity_search

This is a very basic module that comprises of proximity_phrase and proximity_sentence.
Both are meant to compliment each other's functionality.
Their input parameters are the same.
**parameters**
- sentence(mandatory): Element of interest (can be sentence/paragraphs/documents )
- word1(mandatory): first word (can be group of words or phrase)
- word2(mandatory): second word (can be group of words or phrase)
- number(mandatory): number of words between "word1" and "word2"
- boolean value(optional with default as True): if order == True, word1..number_of_words...word2; i.e. word1 should precede word2 in the text



The specific use:
**proximity_sentence**
Result: (boolean) True if "word1" and "word2" are separated by less than "number" words.

It intended to be used on a large set of documents/sentences; Results in filtering elements that return "True" for the given input parameters.

**proximity_phrase**
Results in giving the specific phrase that was positive for the condition entered in parameters.

It is ideally intended to be run only on sentences/documents that were filtered using proximity_sentence.
So effectively by using the two in succession, we can obtain the phrases that are positive for the parameters.


# Uses of proximity_search

1. By chartreviewer- If integrated with patient charts, can be used as a smarter search feature to quickly glance through the chart and find relevant information quickly.

2. Filter tool- Can be run on large collections of text to filter out relevant content of interest

To sum it up, this tool can capture domain knowledge much better than the normal search feature because it takes into account interrelation between words of interest.

Quality of results obtained will depend on choice of parameters by the domain expert

How it works?
proximity_sentence
1. Converts to lower case
2. Replaces words of interest
3. converts document to array,
4. Gets difference between position of "word1", "word2"
5. Depending on "order" parameter, uses absolute value
6. Compares with "number"

How it works?
proximity_phrase
1. Finds words of interest and makes multiple combinations between the two groups.
2. Calculates number of words between the combinations and, compares with "number".
3. Returns phrase if number of words is less than "number".
