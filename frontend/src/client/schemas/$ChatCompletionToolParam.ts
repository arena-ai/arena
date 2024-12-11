/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $ChatCompletionToolParam = {
    properties: {
        id: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        function: {
            type: 'Function',
            isRequired: true,
        },
        type: {
            type: 'string',
            isRequired: true,
        },
    },
} as const;
