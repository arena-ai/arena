/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ArenaParameters } from './ArenaParameters';
import type { Choice_Input } from './Choice_Input';
import type { CompletionUsage_Input } from './CompletionUsage_Input';

/**
 * Maps to:
 * https://github.com/openai/openai-python/blob/main/src/openai/types/chat/chat_completion.py#L40
 * https://github.com/mistralai/client-python/blob/main/src/mistralai/models/chat_completion.py#L86
 * https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message.py#L14
 */
export type ChatCompletionResponse_Input = {
    id: string;
    choices: Array<Choice_Input>;
    created?: (number | null);
    model: string;
    object?: ('chat.completion' | null);
    system_fingerprint?: (string | null);
    usage?: (CompletionUsage_Input | null);
    arena_parameters?: (ArenaParameters | null);
};

