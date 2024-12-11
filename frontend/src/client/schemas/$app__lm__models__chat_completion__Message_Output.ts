/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $app__lm__models__chat_completion__Message_Output = {
    description: `Maps to:
    https://github.com/openai/openai-python/blob/main/src/openai/types/chat/chat_completion_message_param.py#L15
    https://github.com/openai/openai-python/blob/main/src/openai/types/chat/chat_completion_user_message_param.py#L13
    https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/types/message_param.py#L15`,
    properties: {
        content: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }],
            isRequired: true,
        },
        role: {
            type: 'Enum',
            isRequired: true,
        },
        name: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        tool_calls: {
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
    },
} as const;
