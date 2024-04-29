/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { app__lm__models__anthropic__ChatCompletionResponse } from '../models/app__lm__models__anthropic__ChatCompletionResponse';
import type { app__lm__models__chat_completion__ChatCompletionResponse_Output } from '../models/app__lm__models__chat_completion__ChatCompletionResponse_Output';
import type { app__lm__models__mistral__ChatCompletionResponse } from '../models/app__lm__models__mistral__ChatCompletionResponse';
import type { app__lm__models__openai__ChatCompletionResponse } from '../models/app__lm__models__openai__ChatCompletionResponse';
import type { Body_language_models_chat_completion_chat_completion_response } from '../models/Body_language_models_chat_completion_chat_completion_response';
import type { ChatCompletionRequest } from '../models/ChatCompletionRequest';
import type { Event } from '../models/Event';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class LanguageModelsChatCompletionService {

    /**
     * Openai Chat Completion
     * OpenAI integration
     * @returns app__lm__models__openai__ChatCompletionResponse Successful Response
     * @throws ApiError
     */
    public static openaiChatCompletion({
        requestBody,
    }: {
        requestBody: Record<string, any>,
    }): CancelablePromise<app__lm__models__openai__ChatCompletionResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/lm/openai/chat/completions',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Mistral Chat Completion
     * Mistral integration
     * @returns app__lm__models__mistral__ChatCompletionResponse Successful Response
     * @throws ApiError
     */
    public static mistralChatCompletion({
        requestBody,
    }: {
        requestBody: Record<string, any>,
    }): CancelablePromise<app__lm__models__mistral__ChatCompletionResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/lm/mistral/v1/chat/completions',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Anthropic Chat Completion
     * Anthropic integration
     * @returns app__lm__models__anthropic__ChatCompletionResponse Successful Response
     * @throws ApiError
     */
    public static anthropicChatCompletion({
        requestBody,
    }: {
        requestBody: Record<string, any>,
    }): CancelablePromise<app__lm__models__anthropic__ChatCompletionResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/lm/anthropic/v1/messages',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Chat Completion
     * Abstract version
     * @returns app__lm__models__chat_completion__ChatCompletionResponse_Output Successful Response
     * @throws ApiError
     */
    public static chatCompletion({
        requestBody,
    }: {
        requestBody: ChatCompletionRequest,
    }): CancelablePromise<app__lm__models__chat_completion__ChatCompletionResponse_Output> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/lm/chat/completions',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Chat Completion Request
     * @returns Event Successful Response
     * @throws ApiError
     */
    public static chatCompletionRequest({
        requestBody,
    }: {
        requestBody: ChatCompletionRequest,
    }): CancelablePromise<Event> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/lm/chat/completions/request',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Chat Completion Response
     * @returns Event Successful Response
     * @throws ApiError
     */
    public static chatCompletionResponse({
        requestBody,
    }: {
        requestBody: Body_language_models_chat_completion_chat_completion_response,
    }): CancelablePromise<Event> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/lm/chat/completions/response/{request_event_id}',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
