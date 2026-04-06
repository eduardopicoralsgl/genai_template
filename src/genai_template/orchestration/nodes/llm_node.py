from ..state import PipelineState

from genai_template.llm.call import call_llm_chat
from genai_template.llm.message_thread import ChatMessageThread
from genai_template.prompts.registry import get_prompt
from genai_template.observability.langfuse import get_langfuse


def llm_node(state: PipelineState) -> PipelineState:
    with get_langfuse().start_as_current_observation(
        as_type="span",
        name="llm_node",
    ) as obs:
        try:
            prompt = get_prompt("example")
            user_message = state.get("input", {}).get("message", "")

            thread = ChatMessageThread().add_system(prompt).add_user(user_message)

            result, _ = call_llm_chat(thread.to_messages(), purpose="llm", origin="llm_node")

            obs.update(output=result)
            state["result"] = result

            return state

        except Exception as e:
            obs.update(output={"error": str(e)})
            raise
