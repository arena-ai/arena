/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { FunctionDefinition } from './FunctionDefinition';
import type { Message_Input } from './Message_Input';
import type { Metadata } from './Metadata';

/**
 * Maps to:
 * https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message_create_params.py#L13
 * https://docs.anthropic.com/claude/reference/messages_post
 */
export type app__lm__models__anthropic__ChatCompletionRequest = {
    max_tokens?: number;
    messages: Array<Message_Input>;
    model: (string | 'claude-3-opus-20240229' | 'claude-3-sonnet-20240229' | 'claude-3-haiku-20240307' | 'claude-2.1' | 'claude-2.0' | 'claude-instant-1.2');
    metadata?: (Metadata | null);
    stop_sequences?: (Array<string> | null);
    system?: (string | null);
    temperature?: (number | null);
    tools?: (Array<FunctionDefinition> | null);
    top_p?: (number | null);
    top_k?: (number | null);
    stream?: (boolean | null);
};

