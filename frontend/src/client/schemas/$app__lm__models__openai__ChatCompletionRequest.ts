/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $app__lm__models__openai__ChatCompletionRequest = {
    description: `https://github.com/openai/openai-python/blob/main/src/openai/types/chat/completion_create_params.py#L24
    https://platform.openai.com/docs/api-reference/chat`,
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
        frequency_penalty: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        logit_bias: {
            type: 'any-of',
            contains: [{
                type: 'dictionary',
                contains: {
                    type: 'number',
                },
            }, {
                type: 'null',
            }],
        },
        logprobs: {
            type: 'any-of',
            contains: [{
                type: 'boolean',
            }, {
                type: 'null',
            }],
        },
        max_tokens: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        'n': {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        presence_penalty: {
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
        seed: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        stop: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'array',
                contains: {
                    type: 'string',
                },
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
                type: 'ChatCompletionToolParam',
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
        top_logprobs: {
            type: 'any-of',
            contains: [{
                type: 'number',
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
        user: {
            type: 'any-of',
            contains: [{
                type: 'string',
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
