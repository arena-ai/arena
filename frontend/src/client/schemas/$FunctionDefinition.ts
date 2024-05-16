/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $FunctionDefinition = {
    properties: {
        name: {
            type: 'string',
            isRequired: true,
        },
        description: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        input_schema: {
            type: 'dictionary',
            contains: {
                properties: {
                },
            },
            isRequired: true,
        },
    },
} as const;
