/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $DocumentDataExtractorUpdate = {
    properties: {
        name: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        prompt: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        response_template: {
            type: 'any-of',
            contains: [{
                type: 'dictionary',
                contains: {
                    type: 'any[]',
                    maxItems: 2,
                    minItems: 2,
                },
            }, {
                type: 'null',
            }],
        },
    },
} as const;
