from sqlmodel import Session
from app import crud
from app.models import Event, EventCreate, User
from app.lm.models import LanguageModelsApiKeys

from app.ops import Op, Computation, Var

class Setting(Op[tuple[Session, User], str]):
    name: str

    async def call(self, session: Session, user: User) -> str:
        return crud.get_setting(session=session, setting_name=self.name, owner_id=user.id)


openai_api_key: Op = Setting("OPENAI_API_KEY")

mistral_api_key: Op = Setting("MISTRAL_API_KEY")

anthropic_api_key: Op = Setting("ANTHROPIC_API_KEY")
    

language_models_api_keys: Computation = Const(value=LanguageModelsApiKeys(

))