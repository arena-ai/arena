/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ChoiceLogprobs_Input } from './ChoiceLogprobs_Input';
import type { Message_Input } from './Message_Input';

export type Choice_Input = {
    finish_reason?: ('stop' | 'length' | 'tool_calls' | 'content_filter' | 'function_call' | 'error' | null);
    index: number;
    logprobs?: (ChoiceLogprobs_Input | null);
    message: Message_Input;
};

