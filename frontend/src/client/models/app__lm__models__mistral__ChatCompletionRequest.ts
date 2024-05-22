/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ChatCompletionToolParam } from './ChatCompletionToolParam';
import type { Message_Input } from './Message_Input';
import type { ResponseFormat } from './ResponseFormat';

/**
 * Maps to:
 * https://github.com/mistralai/client-python/blob/main/src/mistralai/client.py#L153
 * https://github.com/mistralai/client-python/blob/main/src/mistralai/models/chat_completion.py
 * https://docs.mistral.ai/api/#operation/createChatCompletion
 */
export type app__lm__models__mistral__ChatCompletionRequest = {
    messages: Array<Message_Input>;
    model: (string | 'mistral-large-latest' | 'mistral-medium' | 'mistral-medium-latest' | 'mistral-small' | 'mistral-small-latest' | 'mistral-tiny' | 'open-mistral-7b' | 'open-mixtral-8x7b');
    max_tokens?: (number | null);
    response_format?: (ResponseFormat | null);
    safe_prompt?: (boolean | null);
    random_seed?: (number | null);
    temperature?: (number | null);
    tool_choice?: ('none' | 'auto' | 'any' | null);
    tools?: (Array<ChatCompletionToolParam> | null);
    top_p?: (number | null);
    stream?: (boolean | null);
};

