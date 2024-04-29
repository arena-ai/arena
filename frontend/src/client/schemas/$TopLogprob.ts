/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $TopLogprob = {
    properties: {
        token: {
            type: 'string',
            isRequired: true,
        },
        bytes: {
            type: 'any-of',
            contains: [{
                type: 'array',
                contains: {
                    type: 'number',
                },
            }, {
                type: 'null',
            }],
        },
        logprob: {
            type: 'number',
            isRequired: true,
        },
    },
} as const;
