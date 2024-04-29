/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $app__lm__models__anthropic__ChatCompletionResponse = {
    description: `https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message.py#L14`,
    properties: {
        id: {
            type: 'string',
            isRequired: true,
        },
        content: {
            type: 'array',
            contains: {
                type: 'TextBlock',
            },
            isRequired: true,
        },
        model: {
            type: 'string',
            isRequired: true,
        },
        role: {
            type: 'Enum',
        },
        stop_reason: {
            type: 'any-of',
            contains: [{
                type: 'Enum',
            }, {
                type: 'null',
            }],
        },
        stop_sequence: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        type: {
            type: 'Enum',
        },
        usage: {
            type: 'any-of',
            contains: [{
                type: 'app__lm__models__anthropic__CompletionUsage',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
