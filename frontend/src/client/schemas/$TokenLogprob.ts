/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $TokenLogprob = {
    properties: {
        token: {
            type: 'string',
            isRequired: true,
        },
        logprob: {
            type: 'number',
            isRequired: true,
        },
        top_logprobs: {
            type: 'array',
            contains: {
                type: 'TopLogprob',
            },
            isRequired: true,
        },
    },
} as const;
