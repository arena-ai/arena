/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { app__lm__models__chat_completion__CompletionUsage } from './app__lm__models__chat_completion__CompletionUsage';
import type { Choice_Input } from './Choice_Input';
import type { LMConfig } from './LMConfig';

/**
 * https://github.com/openai/openai-python/blob/main/src/openai/types/chat/chat_completion.py#L40
 */
export type app__lm__models__openai__ChatCompletionResponse_Input = {
    id: string;
    choices: Array<Choice_Input>;
    created?: (number | null);
    model: string;
    object?: (string | null);
    system_fingerprint?: (string | null);
    usage?: (app__lm__models__chat_completion__CompletionUsage | null);
    lm_config?: (LMConfig | null);
};

