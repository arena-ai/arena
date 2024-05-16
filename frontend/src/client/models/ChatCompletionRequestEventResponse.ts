/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { app__lm__models__anthropic__ChatCompletionRequest } from './app__lm__models__anthropic__ChatCompletionRequest';
import type { app__lm__models__anthropic__ChatCompletionResponse } from './app__lm__models__anthropic__ChatCompletionResponse';
import type { app__lm__models__chat_completion__ChatCompletionRequest } from './app__lm__models__chat_completion__ChatCompletionRequest';
import type { app__lm__models__chat_completion__ChatCompletionResponse_Input } from './app__lm__models__chat_completion__ChatCompletionResponse_Input';
import type { app__lm__models__mistral__ChatCompletionRequest } from './app__lm__models__mistral__ChatCompletionRequest';
import type { app__lm__models__mistral__ChatCompletionResponse_Input } from './app__lm__models__mistral__ChatCompletionResponse_Input';
import type { app__lm__models__openai__ChatCompletionRequest } from './app__lm__models__openai__ChatCompletionRequest';
import type { app__lm__models__openai__ChatCompletionResponse_Input } from './app__lm__models__openai__ChatCompletionResponse_Input';

export type ChatCompletionRequestEventResponse = {
    request?: (app__lm__models__chat_completion__ChatCompletionRequest | app__lm__models__openai__ChatCompletionRequest | app__lm__models__mistral__ChatCompletionRequest | app__lm__models__anthropic__ChatCompletionRequest | null);
    request_event_id: number;
    response: (app__lm__models__chat_completion__ChatCompletionResponse_Input | app__lm__models__openai__ChatCompletionResponse_Input | app__lm__models__mistral__ChatCompletionResponse_Input | app__lm__models__anthropic__ChatCompletionResponse);
};

