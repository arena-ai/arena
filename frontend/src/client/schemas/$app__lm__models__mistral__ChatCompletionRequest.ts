/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $app__lm__models__mistral__ChatCompletionRequest = {
    description: `Maps to:
    https://github.com/mistralai/client-python/blob/main/src/mistralai/client.py#L153
    https://github.com/mistralai/client-python/blob/main/src/mistralai/models/chat_completion.py
    https://docs.mistral.ai/api/#operation/createChatCompletion`,
    properties: {
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
        max_tokens: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        response_format: {
            type: 'any-of',
            contains: [{
                type: 'ResponseFormat',
            }, {
                type: 'null',
            }],
        },
        safe_prompt: {
            type: 'any-of',
            contains: [{
                type: 'boolean',
            }, {
                type: 'null',
            }],
        },
        random_seed: {
            type: 'any-of',
            contains: [{
                type: 'number',
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
        tool_choice: {
            type: 'any-of',
            contains: [{
                type: 'Enum',
            }, {
                type: 'null',
            }],
        },
        tools: {
            type: 'any-of',
            contains: [{
                type: 'array',
                contains: {
                    type: 'ChatCompletionToolParam',
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
