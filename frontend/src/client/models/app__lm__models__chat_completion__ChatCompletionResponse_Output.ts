/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { app__lm__models__chat_completion__CompletionUsage } from './app__lm__models__chat_completion__CompletionUsage';
import type { ArenaParameters } from './ArenaParameters';
import type { Choice_Output } from './Choice_Output';

/**
 * Maps to:
 * https://github.com/openai/openai-python/blob/main/src/openai/types/chat/chat_completion.py#L40
 * https://github.com/mistralai/client-python/blob/main/src/mistralai/models/chat_completion.py#L86
 * https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message.py#L14
 */
export type app__lm__models__chat_completion__ChatCompletionResponse_Output = {
    id: string;
    choices: Array<Choice_Output>;
    created?: (number | null);
    model: string;
    object?: ('chat.completion' | null);
    system_fingerprint?: (string | null);
    usage?: (app__lm__models__chat_completion__CompletionUsage | null);
    arena_parameters?: (ArenaParameters | null);
};

