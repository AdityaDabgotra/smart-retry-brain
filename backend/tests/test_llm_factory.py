import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os
import pytest

from app.llm.factory import get_llm_provider


def test_unknown_provider_raises():
    os.environ["RETRY_BRAIN_LLM_PROVIDER"] = "not_a_real_provider"
    get_llm_provider.cache_clear()
    from app.core.config import Settings
    import app.llm.factory as factory_module
    factory_module.settings = Settings()
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        get_llm_provider()


def test_anthropic_without_key_raises_clean_error():
    os.environ["RETRY_BRAIN_LLM_PROVIDER"] = "anthropic"
    os.environ["RETRY_BRAIN_ANTHROPIC_API_KEY"] = ""
    get_llm_provider.cache_clear()
    from app.core.config import Settings
    import app.llm.factory as factory_module
    factory_module.settings = Settings()
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        get_llm_provider()