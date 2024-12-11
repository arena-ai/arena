/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { app__lm__models__anthropic__CompletionUsage } from './app__lm__models__anthropic__CompletionUsage';
import type { TextBlock } from './TextBlock';

/**
 * https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message.py#L14
 */
export type app__lm__models__anthropic__ChatCompletionResponse = {
    id: string;
    content: Array<TextBlock>;
    model: string;
    role?: string;
    stop_reason?: ('end_turn' | 'max_tokens' | 'stop_sequence' | null);
    stop_sequence?: (string | null);
    type?: string;
    usage?: (app__lm__models__anthropic__CompletionUsage | null);
};

