/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $JSONSchema = {
    properties: {
        name: {
            type: 'string',
            isRequired: true,
        },
        schema: {
            type: 'dictionary',
            contains: {
                properties: {
                },
            },
        },
        strict: {
            type: 'any-of',
            contains: [{
                type: 'boolean',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
