/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ChatCompletionToolParam } from './ChatCompletionToolParam';

/**
 * Maps to:
 * https://github.com/openai/openai-python/blob/main/src/openai/types/chat/chat_completion_message_param.py#L15
 * https://github.com/openai/openai-python/blob/main/src/openai/types/chat/chat_completion_user_message_param.py#L13
 * https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message_param.py#L15
 */
export type app__lm__models__chat_completion__Message_Output = {
    content: string;
    role: 'system' | 'user' | 'assistant' | 'tools';
    name?: (string | null);
    tool_calls?: (Array<ChatCompletionToolParam> | null);
};

