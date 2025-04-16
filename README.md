Massive Search: LLM Structured Outputs is All You Need
```json
[
  {
    "sub_query": "Find books with 'prince' in the title under $30",
    "title": {
      "keywords": ["prince"]
    },
    "description": {
      "keywords": []
    },
    "price": {
      "number_ranges": [
        {
          "start_number": null,
          "end_number": 30
        }
      ]
    }
  },
  {
    "sub_query": "Find books with 'prince' in the description under $30",
    "title": {
      "keywords": []
    },
    "description": {
      "keywords": ["prince"]
    },
    "price": {
      "number_ranges": [
        {
          "start_number": null,
          "end_number": 30
        }
      ]
    }
  },
  {
    "sub_query": "Find books with 'lord' in the title under $30",
    "title": {
      "keywords": ["lord"]
    },
    "description": {
      "keywords": []
    },
    "price": {
      "number_ranges": [
        {
          "start_number": null,
          "end_number": 30
        }
      ]
    }
  },
  {
    "sub_query": "Find books with 'lord' in the description under $30",
    "title": {
      "keywords": []
    },
    "description": {
      "keywords": ["lord"]
    },
    "price": {
      "number_ranges": [
        {
          "start_number": null,
          "end_number": 30
        }
      ]
    }
  }
]
```
