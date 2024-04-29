/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $ChoiceLogprobs_Output = {
    properties: {
        content: {
            type: 'any-of',
            contains: [{
                type: 'array',
                contains: {
                    type: 'TokenLogprob',
                },
            }, {
                type: 'null',
            }],
        },
    },
} as const;
