from factory import Factory, BUILD_STRATEGY

from src.app.adapters.http.dtos import PersonResponse


class PersonResponseFactory(Factory):
    class Meta:
        model = PersonResponse
        strategy = BUILD_STRATEGY

    name = "Luke"
