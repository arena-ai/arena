/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $DocumentDataExtractorOut = {
    properties: {
        name: {
            type: 'string',
            isRequired: true,
        },
        prompt: {
            type: 'string',
            isRequired: true,
        },
        id: {
            type: 'number',
            isRequired: true,
        },
        timestamp: {
            type: 'string',
            isRequired: true,
            format: 'date-time',
        },
        owner_id: {
            type: 'number',
            isRequired: true,
        },
        document_data_examples: {
            type: 'array',
            contains: {
                type: 'DocumentDataExample',
            },
            isRequired: true,
        },
    },
} as const;
