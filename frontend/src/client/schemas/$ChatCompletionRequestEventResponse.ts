/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $ChatCompletionRequestEventResponse = {
    properties: {
        request: {
            type: 'any-of',
            contains: [{
                type: 'app__lm__models__chat_completion__ChatCompletionRequest',
            }, {
                type: 'app__lm__models__openai__ChatCompletionRequest',
            }, {
                type: 'app__lm__models__mistral__ChatCompletionRequest',
            }, {
                type: 'app__lm__models__anthropic__ChatCompletionRequest',
            }, {
                type: 'null',
            }],
        },
        request_event_id: {
            type: 'number',
            isRequired: true,
        },
        response: {
            type: 'any-of',
            contains: [{
                type: 'app__lm__models__chat_completion__ChatCompletionResponse_Input',
            }, {
                type: 'app__lm__models__openai__ChatCompletionResponse_Input',
            }, {
                type: 'app__lm__models__mistral__ChatCompletionResponse_Input',
            }, {
                type: 'app__lm__models__anthropic__ChatCompletionResponse',
            }],
            isRequired: true,
        },
    },
} as const;
