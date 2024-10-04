/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $DocumentDataExampleOut = {
    properties: {
        document_id: {
            type: 'string',
            isRequired: true,
        },
        data: {
            type: 'string',
            isRequired: true,
        },
        document_data_extractor_id: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        id: {
            type: 'number',
            isRequired: true,
        },
    },
} as const;
