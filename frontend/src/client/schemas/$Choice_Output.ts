/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $Choice_Output = {
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
                type: 'ChoiceLogprobs_Output',
            }, {
                type: 'null',
            }],
        },
        message: {
            type: 'app__lm__models__chat_completion__Message_Output',
            isRequired: true,
        },
    },
} as const;
