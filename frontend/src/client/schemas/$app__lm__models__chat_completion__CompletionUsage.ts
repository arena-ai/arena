/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $app__lm__models__chat_completion__CompletionUsage = {
    properties: {
        completion_tokens: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        prompt_tokens: {
            type: 'number',
            isRequired: true,
        },
        total_tokens: {
            type: 'number',
            isRequired: true,
        },
    },
} as const;
