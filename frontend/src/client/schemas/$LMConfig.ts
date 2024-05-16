/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $LMConfig = {
    properties: {
        pii_removal: {
            type: 'any-of',
            contains: [{
                type: 'Enum',
            }, {
                type: 'null',
            }],
        },
        judge_evaluation: {
            type: 'boolean',
        },
    },
} as const;
