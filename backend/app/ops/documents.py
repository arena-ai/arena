from typing import Mapping
from pydantic import Field, ConfigDict
from faker import Faker
from sqlmodel import Session

from app.models import User
from app.services.masking import Analyzer, AnalyzerRequest, Anonymizer, AnonymizerRequest, Anonymizers, Replace, Redact, Mask, Hash, Encrypt, Keep
from app.ops import Op
from app.api.deps import CurrentUser
from app.services.object_store import Documents

class Paths(Op[User, list[str]]):
    async def call(self, user: User) -> list[str]:
        docs = Documents()
        prefixes = docs.list() if user.is_superuser else [f"{user.id}/"]
        return [path for prefix in prefixes for path in docs.list(prefix=prefix)]

# class Path(Op[[User, str], str]):
#     async def call(self, user: User) -> list[str]:
#         docs = Documents()
#         prefixes = docs.list() if user.is_superuser else [f"{user.id}/"]
#         return [path for prefix in prefixes for path in docs.list(prefix=prefix)]

# def get_path(docs: Documents, current_user: CurrentUser, name: str):
#     """Get the path of a document from its name"""
#     if current_user.is_superuser:
#         return next(path for path in list_paths(docs, current_user) if path.split("/")[1]==name)
#     else:
#         return f"{current_user.id}/{name}/"

# class GetAsText(Op[tuple[Session, User, str], str]):
#     async def call(self, session: Session, user: User, ) -> str:
#         analyzer = Analyzer()
#         anonymizer = Anonymizer()
#         analysis = await analyzer.analyze(AnalyzerRequest(text=input))
#         anonymized = await anonymizer.anonymize(AnonymizerRequest(
#             text=input,
#             anonymizers=Anonymizers(DEFAULT=Replace()),
#             analyzer_results=analysis,
#         ))
#         return anonymized.text

# get_as_text = GetAsText()
