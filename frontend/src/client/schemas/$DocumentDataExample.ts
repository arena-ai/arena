/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $DocumentDataExample = {
    properties: {
        id: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
        document_id: {
            type: 'string',
            isRequired: true,
        },
        data: {
            type: 'string',
            isRequired: true,
        },
        document_data_extractor_id: {
            type: 'number',
            isRequired: true,
        },
        start_page: {
            type: 'number',
        },
        end_page: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
