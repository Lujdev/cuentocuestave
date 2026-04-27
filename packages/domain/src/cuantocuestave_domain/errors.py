class DomainError(Exception):
    """Base domain error."""


class ProductNotFound(DomainError):
    pass


class ListingNotFound(DomainError):
    pass


class MatchingError(DomainError):
    pass


class ScrapingError(DomainError):
    pass
