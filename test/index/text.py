"""Text Index Schema."""

from massivesearch.spec import BaseIndex, SpecBuilder

spec_builder = SpecBuilder()


@spec_builder.index("text_index")
class TextIndex(BaseIndex):
    """Schema for text index."""

    examples: list[str]
