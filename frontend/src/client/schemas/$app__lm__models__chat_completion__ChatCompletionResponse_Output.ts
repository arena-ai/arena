/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $app__lm__models__chat_completion__ChatCompletionResponse_Output = {
    description: `Maps to:
    https://github.com/openai/openai-python/blob/main/src/openai/types/chat/chat_completion.py#L40
    https://github.com/mistralai/client-python/blob/main/src/mistralai/models/chat_completion.py#L86
    https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message.py#L14`,
    properties: {
        id: {
            type: 'string',
            isRequired: true,
        },
        choices: {
            type: 'array',
            contains: {
                type: 'Choice_Output',
            },
            isRequired: true,
        },
        created: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        model: {
            type: 'string',
            isRequired: true,
        },
        object: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        system_fingerprint: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        usage: {
            type: 'any-of',
            contains: [{
                type: 'app__lm__models__chat_completion__CompletionUsage',
            }, {
                type: 'null',
            }],
        },
        lm_config: {
            type: 'any-of',
            contains: [{
                type: 'LMConfig',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
