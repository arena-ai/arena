/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $app__lm__models__anthropic__ChatCompletionRequest = {
    description: `Maps to:
    https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message_create_params.py#L13
    https://docs.anthropic.com/claude/reference/messages_post`,
    properties: {
        max_tokens: {
            type: 'number',
        },
        messages: {
            type: 'array',
            contains: {
                type: 'Message_Input',
            },
            isRequired: true,
        },
        model: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'Enum',
            }],
            isRequired: true,
        },
        metadata: {
            type: 'any-of',
            contains: [{
                type: 'Metadata',
            }, {
                type: 'null',
            }],
        },
        stop_sequences: {
            type: 'any-of',
            contains: [{
                type: 'array',
                contains: {
                    type: 'string',
                },
            }, {
                type: 'null',
            }],
        },
        system: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        temperature: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        tools: {
            type: 'any-of',
            contains: [{
                type: 'array',
                contains: {
                    type: 'FunctionDefinition',
                },
            }, {
                type: 'null',
            }],
        },
        top_p: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        top_k: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        stream: {
            type: 'any-of',
            contains: [{
                type: 'boolean',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
