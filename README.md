Massive Search: LLM Structured Outputs is All You Need
=================

For complex search task like searching both images, text, boolean, and numbers,
these is no simple query language that can express the search.

Massive Search is a way to search for complex data using LLM Structured Outputs.
Here is an example of book searching:

1. Book data, full data in [examples/book/books.csv](examples/book/books.csv):

``` csv
title,description,author,price
"Snow White and the Seven Dwarfs","A fairy tale about a princess and seven dwarfs.","Grimm Brothers",10.99
"The Little Prince","A story about a young prince who travels to different planets.","Antoine de Saint-Exupéry",12.99
...
```

2. Define the search spec, example in [examples/book/book_spec.yaml](examples/book/book_spec.yaml):

``` yaml
indexs:
  - name: title
    type: text_index
    ...
    search_engine:
      type: book_text_search
      ...
  - name: description
    type: text_index
    ...
    search_engine:
      type: book_text_search
      ...
  - name: price
    type: number_index
    ...
    search_engine:
      type: book_price_search
      ...
aggregator:
  type: book_aggregator
  ...
ai_client:
  type: azure_openai
  ...
```

3. Use SpecBuilder to register related index, search engine, and aggregator, example in [examples/book/main.py](examples/book/main.py):

``` python
book_builder = SpecBuilder()

book_builder.register_index("text_index", BasicTextIndex)
book_builder.register_index("number_index", BasicNumberIndex)
book_builder.register_search_engine("book_text_search", PandasTextSearchEngine)
book_builder.register_search_engine("book_price_search", PandasNumberSearchEngine)

book_builder.register_aggregator_type("book_aggregator", PandasAggregator)
book_builder.register_ai_client_type("azure_openai", AzureOpenAIClient)
```

4. Load data, ai model and use Worker to search, example in [examples/book/main.py](examples/book/main.py):

``` python
with Path("./examples/book/book_spec.yaml").open() as file:
    spec_file = yaml.safe_load(file)

book_builder.include(spec_file)
worker = Worker(book_builder.spec)
agg_result = worker.execute(
    "I want to buy a book about prince or lord, and I only have 20 dollars.",
)
```

5. Check the result, example in [examples/book/main.py](examples/book/main.py):

``` python
print("Search query:")
for result in worker.last_search_query:
    print(result)

print("Books:")
print(agg_result)
```