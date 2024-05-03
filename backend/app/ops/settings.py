from sqlmodel import Session
from app import crud
from app.models import User, LMConfig
from app.lm import models

from app.ops import Op, Computation, Var

class Setting(Op[tuple[Session, User], str]):
    """An op to access setting by name"""
    name: str

    async def call(self, session: Session, user: User) -> str:
        setting = crud.get_setting(session=session, setting_name=self.name, owner_id=user.id)
        if setting:
            return setting.content
        else:
            return ""


def openai_api_key(session: Session, user: User) -> Computation[str]:
    return Setting(name="OPENAI_API_KEY")(session, user)


def mistral_api_key(session: Session, user: User) -> Computation[str]:
    return Setting(name="MISTRAL_API_KEY")(session, user)


def anthropic_api_key(session: Session, user: User) -> Computation[str]:
    return Setting(name="ANTHROPIC_API_KEY")(session, user)

class LMConfigSetting(Op[tuple[Session, User], LMConfig]):
    name: str = "LM_CONFIG"
    override: LMConfig | None = None

    async def call(self, session: Session, user: User) -> LMConfig:
        if self.override:
            return self.override
        setting = crud.get_setting(session=session, setting_name=self.name, owner_id=user.id)
        if setting:
            return LMConfig.model_validate_json(setting.content)
        else:
            return LMConfig()

def lm_config(session: Session, user: User, override: LMConfig | None = None) -> Computation[LMConfig]:
    return LMConfigSetting(override=override)(session, user)


class LanguageModelsApiKeys(Op[tuple[str, str, str], str]):
    async def call(self, openai_api_key: str, mistral_api_key: str, anthropic_api_key: str) -> models.LanguageModelsApiKeys:
        return models.LanguageModelsApiKeys(openai_api_key=openai_api_key, mistral_api_key=mistral_api_key, anthropic_api_key=anthropic_api_key)


def language_models_api_keys(session: Session, user: User) -> Computation[LanguageModelsApiKeys]:
    return LanguageModelsApiKeys()(
        openai_api_key(session, user),
        mistral_api_key(session, user),
        anthropic_api_key(session, user),
    )
