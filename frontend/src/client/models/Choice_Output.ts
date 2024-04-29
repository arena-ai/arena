/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { app__lm__models__chat_completion__Message_Output } from './app__lm__models__chat_completion__Message_Output';
import type { ChoiceLogprobs_Output } from './ChoiceLogprobs_Output';

export type Choice_Output = {
    finish_reason?: ('stop' | 'length' | 'tool_calls' | 'content_filter' | 'function_call' | 'error' | null);
    index: number;
    logprobs?: (ChoiceLogprobs_Output | null);
    message: app__lm__models__chat_completion__Message_Output;
};

