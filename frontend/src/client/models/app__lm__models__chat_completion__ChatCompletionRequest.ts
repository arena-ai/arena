/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ChatCompletionToolParam } from './ChatCompletionToolParam';
import type { LMConfig } from './LMConfig';
import type { Message_Input } from './Message_Input';
import type { ResponseFormatBase } from './ResponseFormatBase';
import type { ResponseFormatJSONSchema } from './ResponseFormatJSONSchema';

/**
 * Maps to:
 * https://github.com/openai/openai-python/blob/main/src/openai/types/chat/completion_create_params.py#L24
 * https://github.com/mistralai/client-python/blob/main/src/mistralai/client.py#L153
 * https://github.com/mistralai/client-python/blob/main/src/mistralai/models/chat_completion.py
 * https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message_create_params.py#L13
 */
export type app__lm__models__chat_completion__ChatCompletionRequest = {
    messages: Array<Message_Input>;
    model: (string | null);
    frequency_penalty?: (number | null);
    logit_bias?: (Record<string, number> | null);
    logprobs?: (boolean | null);
    max_tokens?: (number | null);
    'n'?: (number | null);
    presence_penalty?: (number | null);
    response_format?: (ResponseFormatJSONSchema | ResponseFormatBase | null);
    safe_prompt?: (boolean | null);
    seed?: (number | null);
    stop?: (string | Array<string> | null);
    temperature?: (number | null);
    tool_choice?: ('none' | 'auto' | ChatCompletionToolParam | null);
    tools?: (Array<ChatCompletionToolParam> | null);
    top_logprobs?: (number | null);
    top_p?: (number | null);
    user?: (string | null);
    stream?: (boolean | null);
    lm_config?: (LMConfig | null);
};

