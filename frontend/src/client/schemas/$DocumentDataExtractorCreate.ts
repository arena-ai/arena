/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $DocumentDataExtractorCreate = {
    properties: {
        name: {
            type: 'string',
            isRequired: true,
        },
        prompt: {
            type: 'string',
            isRequired: true,
        },
        response_template: {
            type: 'dictionary',
            contains: {
                type: 'any[]',
                maxItems: 2,
                minItems: 2,
            },
            isRequired: true,
        },
    },
} as const;
