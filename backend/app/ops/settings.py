from sqlmodel import Session
from app import crud
from app.models import UserOut
import app.lm.models as lmm

from app.ops import Op, Computation

class Setting(Op[tuple[Session, UserOut], str]):
    """An op to access setting by name"""
    name: str

    async def call(self, session: Session, user: UserOut) -> str:
        setting = crud.get_setting(session=session, setting_name=self.name, owner_id=user.id)
        if setting:
            return setting.content
        else:
            return ""


def openai_api_key(session: Session, user: UserOut) -> Computation[str]:
    return Setting(name="OPENAI_API_KEY")(session, user)


def mistral_api_key(session: Session, user: UserOut) -> Computation[str]:
    return Setting(name="MISTRAL_API_KEY")(session, user)


def anthropic_api_key(session: Session, user: UserOut) -> Computation[str]:
    return Setting(name="ANTHROPIC_API_KEY")(session, user)

class LMConfigSetting(Op[tuple[Session, UserOut], lmm.LMConfig]):
    name: str = "LM_CONFIG"
    override: lmm.LMConfig | None = None

    async def call(self, session: Session, user: UserOut) -> lmm.LMConfig:
        if self.override:
            return self.override
        setting = crud.get_setting(session=session, setting_name=self.name, owner_id=user.id)
        if setting:
            return lmm.LMConfig.model_validate_json(setting.content)
        else:
            return lmm.LMConfig()

def lm_config(session: Session, user: UserOut, override: lmm.LMConfig | None = None) -> Computation[lmm.LMConfig]:
    return LMConfigSetting(override=override)(session, user)


class LMApiKeys(Op[tuple[str, str, str], str]):
    async def call(self, openai_api_key: str, mistral_api_key: str, anthropic_api_key: str) -> lmm.LMApiKeys:
        return lmm.LMApiKeys(openai_api_key=openai_api_key, mistral_api_key=mistral_api_key, anthropic_api_key=anthropic_api_key)


def language_models_api_keys(session: Session, user: UserOut) -> Computation[LMApiKeys]:
    return LMApiKeys()(
        openai_api_key(session, user),
        mistral_api_key(session, user),
        anthropic_api_key(session, user),
    )
