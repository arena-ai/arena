/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $Choice_Input = {
    properties: {
        finish_reason: {
            type: 'any-of',
            contains: [{
                type: 'Enum',
            }, {
                type: 'null',
            }],
        },
        index: {
            type: 'number',
            isRequired: true,
        },
        logprobs: {
            type: 'any-of',
            contains: [{
                type: 'ChoiceLogprobs_Input',
            }, {
                type: 'null',
            }],
        },
        message: {
            type: 'Message_Input',
            isRequired: true,
        },
    },
} as const;
