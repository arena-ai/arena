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
 * https://github.com/openai/openai-python/blob/main/src/openai/types/chat/completion_create_params.py#L24
 * https://platform.openai.com/docs/api-reference/chat
 */
export type app__lm__models__openai__ChatCompletionRequest = {
    messages: Array<Message_Input>;
    model: (string | 'gpt-4o' | 'gpt-4-turbo' | 'gpt-4' | 'gpt-3.5-turbo' | 'gpt-3.5-turbo-16k');
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

